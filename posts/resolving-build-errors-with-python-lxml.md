<!-- 
.. title: Resolving build errors with python lxml on low memory machines
.. slug: resolving-build-errors-with-python-lxml
.. date: 2015-01-27 06:23:57 UTC+11:00
.. tags: Technology
.. link: 
.. spellcheck_exceptions: lxml, OpenBSD, VM, AMI, OOM, login
.. description: 
.. type: text
-->

I use the Python lxml module regularly and it's one of the few modules where I've encountered build problems. The problems were related to its memory requirements and the troubleshooting process wasn't helped by the errors that were logged during the build. While there are a few comments on stack overflow about similar errors under Linux, they were hard to find, and there wasn't anything about building on OpenBSD. To be fair, this isn't a reflection on lxml - it's just the unfortunate soul that highlighted these system errors. My solution is below, hopefully with enough context in the error messages that this can be found by someone else who has the same problem.

Here's how it manifests on on a CentOS6 VM with 512Mb RAM and no swap (this is how an EC2 t1.micro comes when you use the official CentOS 6 AMI and how a Rackspace 512Mb Standard instance comes when you use their CentOS6 image)

```
$ pip install lxml
Collecting lxml
  Using cached lxml-3.4.1.tar.gz
    /usr/local/lib/python2.7/distutils/dist.py:267: UserWarning: Unknown distribution option: 'bugtrack_url'
      warnings.warn(msg)
    Building lxml version 3.4.1.
    Building without Cython.
    Using build configuration of libxslt 1.1.26
    Building against libxml2/libxslt in the following directory: /usr/lib64
Installing collected packages: lxml
    
[snip]

    building 'lxml.etree' extension

    creating build/temp.linux-x86_64-2.7

    creating build/temp.linux-x86_64-2.7/src

    creating build/temp.linux-x86_64-2.7/src/lxml

    gcc -pthread -fno-strict-aliasing -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m64 -mtune=generic -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes -fPIC -I/usr/include/libxml2 -I/tmp/pip-build-rlPuyA/lxml/src/lxml/includes -I/usr/local/include/python2.7 -c src/lxml/lxml.etree.c -o build/temp.linux-x86_64-2.7/src/lxml/lxml.etree.o -w

    {standard input}: Assembler messages:

    {standard input}:491197: Warning: end of file not at end of a line; newline inserted

    {standard input}:492215: Error: unknown pseudo-op: `.strin'

    gcc: Internal error: Killed (program cc1)

    Please submit a full bug report.

    See <http://bugzilla.redhat.com/bugzilla> for instructions.

    error: command 'gcc' failed with exit status 1

    ----------------------------------------
    Command "/home/esteele/.virtualenvs/test27/bin/python2.7 -c "import setuptools, tokenize;__file__='/tmp/pip-build-rlPuyA/lxml/setup.py';exec(compile(getattr(tokenize, 'open', open)(__file__).read().replace('\r\n', '\n'), __file__, 'exec'))" install --record /tmp/pip-3YNmLG-record/install-record.txt --single-version-externally-managed --compile --install-headers /home/esteele/.virtualenvs/test27/include/site/python2.7" failed with error code 1 in /tmp/pip-build-rlPuyA/lxml
```

The error messages didn't help much, so let me help by saying that this is because the system ran out of memory. You can confirm this easily:

```
$ sudo tail /var/log/messages | grep -B1 Killed
Jan 25 15:45:49 localhost kernel: Out of memory: Kill process 6979 (cc1) score 676 or sacrifice child
Jan 25 15:45:49 localhost kernel: Killed process 6979, UID 1003, (cc1) total-vm:456244kB, anon-rss:338792kB, file-rss:8kB
```

So I added 512Mb swap:

```
$ sudo dd if=/dev/zero of=/swapfile bs=1024 count=500000
500000+0 records in
500000+0 records out
512000000 bytes (512 MB) copied, 1.8003 s, 284 MB/s
$ sudo mkswap /swapfile
mkswap: /swapfile: warning: don't erase bootbits sectors
        on whole disk. Use -f to force.
Setting up swapspace version 1, size = 499996 KiB
no label, UUID=c3ca02fa-e36f-4275-b452-42f0675b89b5
$ sudo swapon /swapfile
$ free
             total       used       free     shared    buffers     cached
Mem:        502220     101812     400408          0       5288      48560
-/+ buffers/cache:      47964     454256
Swap:       499992          0     499992
```

And now it installs:

```
(test27)[esteele@localhost ~]$ pip install lxml
Collecting lxml
  Using cached lxml-3.4.1.tar.gz
    /usr/local/lib/python2.7/distutils/dist.py:267: UserWarning: Unknown distribution option: 'bugtrack_url'
      warnings.warn(msg)
    Building lxml version 3.4.1.
    Building without Cython.
    Using build configuration of libxslt 1.1.26
    Building against libxml2/libxslt in the following directory: /usr/lib64
Installing collected packages: lxml
[snip]
Successfully installed lxml-3.4.1
```

However on a OpenBSD 5.6 machine with the same 512 Mb RAM and even more swap (768Mb), it still wouldn't install - there's something else going on.

```
$ sysctl -a | grep -i physmem; pstat -sk
hw.physmem=520028160
Device      1K-blocks     Used    Avail Capacity  Priority
/dev/wd0b      769984    10468   759516     1%    0
$ pip install lxml
Collecting lxml
  Using cached lxml-3.4.1.tar.gz
    /usr/local/lib/python2.7/distutils/dist.py:267: UserWarning: Unknown distribution option: 'bugtrack_url'
      warnings.warn(msg)
    Building lxml version 3.4.1.
    Building without Cython.
    Using build configuration of libxslt 1.1.28
    Building against libxml2/libxslt in the following directory: /usr/local/lib
Installing collected packages: lxml

[snip]

    building 'lxml.etree' extension

    creating build/temp.openbsd-5.6-amd64-2.7

    creating build/temp.openbsd-5.6-amd64-2.7/src

    creating build/temp.openbsd-5.6-amd64-2.7/src/lxml

    cc -pthread -fno-strict-aliasing -O2 -pipe -DNDEBUG -O2 -pipe -fPIC -fPIC -I/usr/local/include -I/usr/local/include/libxml2 -I/tmp/pip-build-YCP0o0/lxml/src/lxml/includes -I/usr/local/include/python2.7 -c src/lxml/lxml.etree.c -o build/temp.openbsd-5.6-amd64-2.7/src/lxml/lxml.etree.o -w



    cc1: out of memory allocating 4072 bytes after a total of 0 bytes

    error: command 'cc' failed with exit status 1

    ----------------------------------------
    Command "/home/esteele/.virtualenvs/test27/bin/python2.7 -c "import setuptools, tokenize;__file__='/tmp/pip-build-YCP0o0/lxml/setup.py';exec(compile(getattr(tokenize, 'open', open)(__file__).read().replace('\r\n', '\n'), __file__, 'exec'))" install --record /tmp/pip-TRArBR-record/install-record.txt --single-version-externally-managed --compile --install-headers /home/esteele/.virtualenvs/test27/include/site/python2.7" failed with error code 1 in /tmp/pip-build-YCP0o0/lxml
$
```

After a bit of troubleshooting, it's clear that we have a different situation from Linux; we're not being killed by the OOM killer, we're hitting resource limits on the data area.

```
$ ulimit -a
time(cpu-seconds)    unlimited
file(blocks)         unlimited
coredump(blocks)     unlimited
data(kbytes)         524288
stack(kbytes)        4096
lockedmem(kbytes)    161612
memory(kbytes)       483220
nofiles(descriptors) 512
processes            128
```

And an attempt to increase it fails because the user is in the default login class (I'd not come across BSD login classes before so I'd chosen the default when creating the account).

```
$ ulimit -Sd 1000000
ksh: ulimit: bad -d limit: Invalid argument
$ ulimit -aH | grep data
data(kbytes)         524288
```

So I changed the login class and restarted the shell:

```
$ sudo usermod -L staff esteele
```

At that point limits can be increased (I put this in my ```.profile```).

```
$ ulimit -Sd 1000000
$ ulimit -a | grep data
data(kbytes)         1000000
```

And it builds fine:

```
$ pip install lxml
Collecting lxml
  Using cached lxml-3.4.1.tar.gz
    /usr/local/lib/python2.7/distutils/dist.py:267: UserWarning: Unknown distribution option: 'bugtrack_url'
      warnings.warn(msg)
    Building lxml version 3.4.1.
    Building without Cython.
    Using build configuration of libxslt 1.1.28
    Building against libxml2/libxslt in the following directory: /usr/local/lib
Installing collected packages: lxml
[snip] 
Successfully installed lxml-3.4.1
```

So the same root cause (insufficient memory), manifested in two different ways, and in both cases the cause was not immediately obvious to me. Hopefully this saves someone else a little time.
