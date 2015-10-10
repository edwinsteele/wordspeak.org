<!--
.. link: 
.. description: 
.. tags: Technology
.. date: 2014/01/25 19:00:23
.. spellcheck_exceptions: CNAME,DNS,IP,amazonaws,ap,balancer,bxr,ec,lookup,lx,mkt,rsync,wordspeak,www,ze,zsh
.. title: Finding out whether a machine answers for a DNS name (including EC2)
.. slug: finding-out-whether-a-machine-answers-for-a-dns-name
-->


The [deployment script](https://github.com/edwinsteele/wordspeak.org/blob/master/fabfile.py) for this site is designed to be run from several different machines (mainly due to sketchy connectivity during my commute to work). This script copies files to a staging server, and to the production server via local rsync or rsync over ssh. I [do not store all private keys](http://en.wikipedia.org/wiki/Principle_of_least_privilege) on all deployments machines, so I need to have logic in place to use a local rsync when the deployment machine actually hosts the site being deployed. The implementation of this logic needs to handle situations where the DNS name resolves directly to the machine i.e. a.b.c resolves to 1.2.3.4 and 1.2.3.4 is an IP address on an interface on the machine that hosts a.b.c, and the situation where a host is behind a load balancer and only has an IP in the private address space but there is [split horizon DNS](http://www.itgeared.com/articles/1020-what-is-split-brain-split-horizon-or/) in place.

I had the first situation before I used Amazon Route 53 for DNS, where a lookup of www.wordspeak.org from the EC2 instance returned the private IP address (172.31.x.y):

    wordspeak.org        A       54.252.214.49
    www.wordspeak.org    CNAME   ec2-54-252-214-49.ap-southeast-2.compute.amazonaws.com

I have the second situation now, where I use Amazon Route 53 ALIAS records to minimise the number of DNS changes necessary when I rebuild my EC2 instance. In this case, a lookup of www.wordspeak.org from the EC2 instance returns the public IP address (54.252.214.49):

    wordspeak.org.       A       54.252.214.49
    www.wordspeak.org    A       ALIAS wordspeak.org. (ze9bxr3mkt7lx)

While Amazon has a way for an EC2 instance to [find its public address](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html#using-instance-addressing-common), my logic needs to be portable so it works on all the other (non-EC2) hosts that run the deployment script.

So here it is in python:

```.python
def does_this_machine_answer_for_this_hostname(dns_name):
   """Looks at DNS and local interfaces to see if this host answers for the
    DNS name in question

   Caveats:
   - Won't work reliably if the DNS entry resolves to more than one address
   - Assumes the interface configured with the IP associated with the host's
     hostname is actually the interface that accepts public traffic
     associated with DNS name in question
   """
   try:
       my_main_ip = socket.gethostbyname(socket.getfqdn())
   except socket.gaierror:
       # Can't resolve hostname to a public IP, so we're probably going to
       #  be referring to ourselves by localhost, so let's allocate an
       #  IP address accordingly.
       my_main_ip = "127.0.0.1"

   # do a round-trip to so that we match when the host is behind a load
   #  balancer and doesn't have a public IP address (assumes split-horizon
   #  DNS is configured to resolve names to internal addresses) e.g. AWS
   return my_main_ip == socket.gethostbyname(
       socket.gethostbyaddr(socket.gethostbyname(dns_name))[0])
```

And in bash/zsh:

```.bash
function does_this_machine_answer_for_this_hostname () {
   # e.g. if [ does_this_machine_answer_for_this_hostname staging.wordspeak.org ]; ...
   my_main_ip=$(dig +short $(hostname --fqdn));
   resolved_ip=$(dig +short $(dig +short -x $(dig +short $1)));
   return $(test "${my_main_ip}" = "${resolved_ip}");
}
```

I hope you find it useful.

