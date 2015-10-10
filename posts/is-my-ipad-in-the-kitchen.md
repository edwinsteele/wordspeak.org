<!-- 
.. title: Is my iPad in the kitchen? (room-level geolocation)
.. slug: is-my-ipad-in-the-kitchen
.. date: 2015-01-02 13:42:16 UTC+11:00
.. tags: Technology
.. link: 
.. is_orphan: False
.. spellcheck_exceptions: geolocation,WiFi,APs,SSID,SNMP,OIDs,wirelessTimeAssociated,wirelessLastRefreshTime,wirelessNumTX,wirelessStrength,snmpwalk,MIBs,usr,snmp,mibs,BASESTATION,MIB,txt,SolarWinds,SSIDs,DHCP,NATing,TCP,multicast,mDNS,HostAP,adapters,BeagleBone,Ardiuno,GHz,Arduino,Bluetooth,DNS,IP,iOS,iPad,internets
.. description: 
.. type: text
-->

# Why
For some parts of my day, the location of my iPad location is a reasonable proxy for the type of activity that I'm doing. For example, I sleep with my iPad on my beside table but only move it there a few minutes before bedtime. In the morning I move it to the kitchen within 2 minutes of getting up and leave it up that end of the house until I go to work. I'm writing some scripts to automate certain activities and the scripts are more effective if they know what else I'm doing, so I've spent some time attempting to isolate which part of the house my iPad is in.

Specifically, I want to be able to answer the question: *Is a particular device in the house, and if so which part of the house is it in?*

# My initial setup
The shape and materials used in a dwelling impact the ability of WiFi signals to propagate, as do the technical components. We have an *L-shaped* single-level brick house with bedrooms at one end of the L and the lounge room and kitchen are at the other end. There are three access points (APs) broadcasting on a single SSID and all devices are on a single `/24` network. The access points are a second generation Airport Express in the lounge room, a first-generation Airport Express in one of the bedrooms and a fifth-generation Apple Time Capsule in the middle. All of the wireless clients are iOS and are talking to the access points using 802.11n on the 2.4GHz spectrum and there are very few wireless networks sitting on 2.4GHz in the vicinity of the house.

# Airport SNMP - not so hot right now
My original plan had been to enable SNMP on the three access points and look at the list of connected clients but this was derailed quickly. Apple appear to be abandoning SNMP in their network devices; I discovered that recent Time Capsules do not have SNMP capabilities, and the switch to enable SNMP on the Airport Express was removed in recent versions of the Airport Utility ([an old version is still available](http://coreyjmahler.com/2013/03/08/airport-utility-5-6-on-os-x-v10-8-mountain-lion/)). The implementation is disappointing too - I noticed that clients that have migrated to another AP still appear as connected to the AP unless the wireless client changes IP address and I found that few of the OIDs that are exposed are well suited to my task. At a glance, `wirelessTimeAssociated`, `wirelessLastRefreshTime`, `wirelessNumTX` and `wirelessStrength` OIDs all appear as potential indicators of activity between a client and an AP but strangely they were not implemented in my (completely Apple) setup or did not update frequently enough to be useful. Here's an example `snmpwalk` of an Airport Express with one connected client.

```bash
$ snmpwalk -m AIRPORT-BASESTATION-3-MIB -v 2c -c public <access point IP> 1.3.6.1.4.1.63.501.3.2
AIRPORT-BASESTATION-3-MIB::sysConfName.0 = STRING: AP Bedroom
AIRPORT-BASESTATION-3-MIB::sysConfContact.0 = STRING:
AIRPORT-BASESTATION-3-MIB::sysConfLocation.0 = STRING:
AIRPORT-BASESTATION-3-MIB::sysConfUptime.0 = INTEGER: 1103716
AIRPORT-BASESTATION-3-MIB::sysConfFirmwareVersion.0 = STRING: 7.6.4
AIRPORT-BASESTATION-3-MIB::wirelessNumber.0 = INTEGER: 3
AIRPORT-BASESTATION-3-MIB::wirelessPhysAddress."xx:xx:xx:xx:xx:xx" = STRING: "xx:xx:xx:xx:xx:xx"
AIRPORT-BASESTATION-3-MIB::wirelessType."xx:xx:xx:xx:xx:xx" = INTEGER: sta(1)
AIRPORT-BASESTATION-3-MIB::wirelessDataRates."xx:xx:xx:xx:xx:xx" = STRING: 1(b) 2(b) 5(b) 6 9 11(b) 12 18 24 36 48 54 MCS: 0-15
AIRPORT-BASESTATION-3-MIB::wirelessTimeAssociated."xx:xx:xx:xx:xx:xx" = INTEGER: 998910
AIRPORT-BASESTATION-3-MIB::wirelessLastRefreshTime."xx:xx:xx:xx:xx:xx" = INTEGER: 0
AIRPORT-BASESTATION-3-MIB::wirelessStrength."xx:xx:xx:xx:xx:xx" = INTEGER: -50
AIRPORT-BASESTATION-3-MIB::wirelessNoise."xx:xx:xx:xx:xx:xx" = INTEGER: -83
AIRPORT-BASESTATION-3-MIB::wirelessRate."xx:xx:xx:xx:xx:xx" = INTEGER: 65
AIRPORT-BASESTATION-3-MIB::wirelessNumRX."xx:xx:xx:xx:xx:xx" = INTEGER: 0
AIRPORT-BASESTATION-3-MIB::wirelessNumTX."xx:xx:xx:xx:xx:xx" = INTEGER: 0
AIRPORT-BASESTATION-3-MIB::wirelessNumRXErrors."xx:xx:xx:xx:xx:xx" = INTEGER: -1
AIRPORT-BASESTATION-3-MIB::wirelessNumTXErrors."xx:xx:xx:xx:xx:xx" = INTEGER: -1
```

I appreciate that Apple released documentation on the MIBs, however. It was helpful. It's available as `/usr/share/snmp/mibs/AIRPORT-BASESTATION-3-MIB.txt` on Mac OS and also available on the internets ([raw view](http://ipmsupport.solarwinds.com/mibs/AIRPORT-BASESTATION-3-MIB/raw.aspx) and [tree view](http://ipmsupport.solarwinds.com/mibs/AIRPORT-BASESTATION-3-MIB/tree.aspx) courtesy of SolarWinds).

# Understanding wireless client behaviour
Not having done much in this area, there were a few observations that were of particular interest when trying to understand how the wireless clients operated. These were all iOS devices, so these observations may not be true of other types of clients:

* clients seem reluctant to switch between access points on the same SSID. I found situations where the client had poor throughput because it was connected to an AP at the other end of the house, even though it was much closer to another AP.
* clients don't switch between SSIDs, even when signal strength drops and connectivity is incredibly poor. When I thought about it, this makes sense because there's no indication that the different SSIDs provide the same network connectivity.
* iOS clients fall off the network quickly, particularly when the screen is turned off. However, I observed them coming onto the network for 5 seconds every minute or so. This is important because establishing whether a device is present requires a prolonged connectivity test. I haven't worked out whether there's a way to awaken a device e.g. A *Wake-on-LAN* equivalent

# Ideas that didn't work
I tried to:

* provide distinct IP addresses from each AP (all in the same `/24`) by using different SSIDs on the APs and providing different DHCP client IDs for each SSID. This required setting static addresses based on client ID instead of MAC but I found that clients didn't switch automatically between SSIDs.
* provide distinct IP addresses from each AP (each in different `/24`s) using have the Airports but found that they could only do this by NATing clients, which would have meant the clients weren't ping-able.
* connect to the Airport management port (TCP 5009), or sniffing traffic to that port. The information that goes to the Apple Airport Utility comes from this port and seems more up-to-date than SNMP but there's no documentation for the protocol, and traffic isn't human readable. Disappointing.
* query multicast DNS - Apple devices advertise quite a few services on mDNS, but there wasn't any information of value in the responses.

# A solution
Without SNMP, I chose to rely on basic connectivity tests and making sure that access points were providing IP addresses in distinct ranges. I implemented this by disconnecting the lounge room Airport Express and making the adjacent Mac Mini into an AP. I had the Mac Mini provide distinct IP address in a new `/24`, and provide routing to this new `/24` (the Airports could not do this). Introducing a new `/24` meant that I needed to set a static route on my router so all clients could route to it. By having distinct IP addresses from each AP, determining the access point for a client was a case of pinging the allocated IP addresses in the two `/24`s for a long enough period to catch sleeping clients. If there was no response, the device was not in the house. I found that it was necessary to switch of the access point in the middle of the house, so that clients were more inclined to migrate between the Airport APs and the Mac Mini AP. An unintended consequence of having each AP having clients in distinct IP ranges was that the Airport SNMP now appears to provide up-to-date information. Unlike previous situations, attached clients were reported as detached more quickly (when a client migrated from the Airport to the Mac Mini AP, the Airport ceased to it as attached in as little as 3 minutes).

# What's next? Better resolution?
So I have a working solution, but it's coarse-grained. If I wanted to actually identify which room a device is in rather than which end of the house it's in, I'd consider using:

* Off-the-shelf APs with a better SNMP implementation i.e. non-Apple APs (and lots of them)
* Small Linux machines running HostAP (assuming there are compatible 802.11n devices) and the WiFi radios can be turned down in power so that the devices are more likely to switch to a closer AP
* Bluetooth LE adapters attached to BeagleBone or Arduino boards (this sounds the most interesting, and probably most cost effective)

But I'm quite happy with what I have...
