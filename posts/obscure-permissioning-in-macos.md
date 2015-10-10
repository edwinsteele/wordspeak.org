<!--
.. title: A journey in obscure MacOS permissions
.. slug: a-journey-in-obscure-macos-permissions.md
.. date: 2015/07/11 05:29:47
.. tags: 
.. spellcheck_exceptions: skool, filesystem, OpenBSD, MacOS, xattr, ACLs, chflags,USB
.. is_orphan: False
.. link:
.. description:
-->

I'm in the process of rebuilding my primary Mac (stuff broke and it was easier to do a clean install than try to fix them). One of the things that broke was my normal backups to my Time Capsule, and while I'd successfully done a temporary backup to a local USB drive, that data wasn't available in the Time Machine interface. I reverted to the old skool approach and did the restoration directly, following this pattern (in the case below, restoring my `~/bin` directory):

```
mercury:~ root# cd /Volumes/Offsite Set 1/Backups.backupdb/mercury/2015-07-05-074244/Macintosh HD/Users/esteele/
mercury:esteele root# tar -cf - bin/ | (cd /Users/esteele/; tar -xvf -)
```

When I tried to edit one of the transferred files, I got permissions problems even though, at first glance, filesystem permissions suggest I shouldn't have problems at all:

```
mercury:~ esteele$ touch bin/testfile
touch: bin/testfile: Permission denied
mercury:~ esteele$ ls -l bin/testfile
-rw-r--r--@ 1 esteele  staff  159  4 Jul 08:52 bin/testfile
```

Most of my day is spent on Linux machines, with occasional ventures onto OpenBSD, but I knew that the `@` in the listing was significant and that MacOS made use of flags and extended attributes on files. After fumbling around in `chflags (1)` and `xattr (1)`  man pages and then the `ls (1)` man page, I could see that the `@` meant that extended attributes had been set, and that there were no flags on the file (the dash to the left of 159). I thought it unlikely that those extended attributes were responsible for the permissions problems that I was seeing, so I moved on:

```
mercury:~ esteele$ ls -lO bin/testfile
-rw-r--r--@ 1 esteele  staff  - 159  4 Jul 08:52 bin/testfile
mercury:~ esteele$ ls -l@ bin/testfile
-rw-r--r--@ 1 esteele  staff  159  4 Jul 08:52 bin/testfile
com.apple.metadata:_kTimeMachineNewestSnapshot   50
com.apple.metadata:_kTimeMachineOldestSnapshot   50
```

But any operation to modify the file was impossible, and the messages from `rm` were quite confusing

```
mercury:~ esteele$ rm bin/testfile
override rw-r--r--  esteele/staff for bin/testfile? y
rm: bin/testfile: Permission denied
```

I knew that more granular permissions existed past the usual *owner, group, other* paradigm, but didn't think they were in play here because of a comment in the `ls` man page.

> If the file or directory has extended attributes, the permissions field printed by the -l option is followed by a '@' character.  Otherwise, if the file or directory has extended security information (such as an access control list), the permissions field printed by the -l option is followed by a '+' character.

After quite some gnashing of teeth, I discovered that they were in play...

```
mercury:~ esteele$ ls -le bin/testfile
-rw-r--r--@ 1 esteele  staff  159  4 Jul 08:52 bin/testfile
0: group:everyone deny write,delete,append,writeattr,writeextattr,chown
```

But why didn't I see a `+` when I ran `ls`? It seems extended attributes get display priority over ACLs (notice how the `@` is replaced by a `+` when the extended attributes are removed)

```
mercury:~ esteele$ ls -l@ bin/testfile
-rw-r--r--@ 1 esteele  staff  159  4 Jul 08:52 bin/testfile
mercury:~ esteele$ sudo xattr -d com.apple.metadata:_kTimeMachineNewestSnapshot bin/testfile
mercury:~ esteele$ sudo xattr -d com.apple.metadata:_kTimeMachineOldestSnapshot bin/testfile
mercury:~ esteele$ ls -l@ bin/testfile
-rw-r--r--+ 1 esteele  staff  159  4 Jul 08:52 bin/testfile
```

How frustrating. In retrospect I can see how the man page is alluding to this behaviour, but it'd be easy to make this more explicit e.g.

> If the file or directory has extended attributes, the permissions field printed by the -l option is followed by a '@' character.  If the file or directory has extended security information (such as an access control list), the permissions field printed by the -l option is followed by a '+' character, unless the file or directory also has extended attributes, in which case only the '@' character will be shown. In this case, view extended security information using the -e option.

Or better still, if you're going to jam several flags into a single character and there aren't many combinations, use another character to represent combinations of the two e.g.

> If the file or directory has extended attributes, the permissions field printed by the -l option is followed by a '@' character.  If the file or directory has extended security information (such as an access control list), the permissions field printed by the -l option is followed by a '+' character, unless the file or directory also has extended attributes, in which case the permissions field printed by the -l option is followed by a '#' character

So finally I was able to remove the ACLs, and everything was back to normal

```
mercury:~ esteele$ chmod -a# 0 bin/testfile
mercury:~ esteele$ ls -le bin/testfile
-rw-r--r--  1 esteele  staff  159  4 Jul 08:52 bin/testfile
mercury:~ esteele$ touch bin/testfile
mercury:~ esteele$
```

So, this was a small journey into less frequently used file attributes made necessary by a failure but complicated by unintuitive documentation. I don't know why the failure happened but it makes me appreciate good documentation all the more, and particularly the effort that the OpenBSD guys put into their man pages.