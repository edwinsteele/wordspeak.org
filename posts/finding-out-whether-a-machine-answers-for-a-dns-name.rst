.. link: 
.. description: 
.. tags: UNIX, Python, Technology, draft
.. date: 2014/01/25 19:00:23
.. title: Finding out whether a machine answers for a DNS name (including EC2)
.. slug: finding-out-whether-a-machine-answers-for-a-dns-name


This is actually a step beyond whether a DNS name resolves to a machine.

I have a deployment script for this site that can be run from just about anywhere. I want to `minimise the number of private keys <http://en.wikipedia.org/wiki/Principle_of_least_privilege>`_ that need to be stored on the deployment machine so the script has logic to prefer a local rsync (over a remote-shell rsync) when the deployment machine answers the site behind deployment (be it the staging host or the production host). The implementation of this logic needs to handle situations where the DNS name resolves directly to the machine i.e. a.b.org resolves to 1.2.3.4 and 1.2.3.4 is an IP address on an interface on the host, and the situation where a host is behind a load balancer and only has an internal IP address (but there is `split horizon DNS <http://www.itgeared.com/articles/1020-what-is-split-brain-split-horizon-or/>`_ in place (specifically, on AWS where an EC2 instance is behind an Elastic IP and does not have an IP address in the public range).

While Amazon has a way for an EC2 instance to find its public address, I need this to be portable so that the logic works on all the other hosts that could run the deployment script

http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html


1.  Use the following command to access the private IP address:
GET http://169.254.169.254/latest/meta-data/local-ipv4
2.  Use the following command to access the public IP address:
GET http://169.254.169.254/latest/meta-data/public-ipv4


.. code-block:: python

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


.. code-block:: bash

 function does_this_machine_answer_for_this_hostname () {
    # e.g. if [ does_this_machine_answer_for_this_hostname staging.wordspeak.org ]; ...
    my_main_ip=$(dig +short $(hostname --fqdn));
    resolved_ip=$(dig +short $(dig +short -x $(dig +short $1)));
    return $(test "${my_main_ip}" = "${resolved_ip}");
 }

