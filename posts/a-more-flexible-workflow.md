<!--
.. link: 
.. description: 
.. tags: Technology
.. date: 2013/06/01 07:11:18
.. spellcheck_exceptions: Linode,MySpell,blog,iPad,iSSH,internet,tmux,unix,workflow
.. title: A more flexible publishing workflow
.. slug: a-more-flexible-workflow
-->


My writing workflow is driven by three main considerations:

-   Most of my writing is done during my commute to work
-   I have connectivity during my commute but it is often flaky
-   It's valuable to be able to post from devices other than my laptop

After reading a [few](http://bergie.iki.fi/blog/six-weeks-working-android/) [posts](http://bergie.iki.fi/blog/six-weeks-working-android/) on using a tablet as a primary device, I thought it was worth a go, and a fun experience. I can report that after a month I'm not using my iPad much more than I was, but I understand more about the constraints that I face if I were to use it as a primary device.

Linode
======

I setup a [Linode 1GB virtual server](https://www.linode.com) and moved my blog publishing setup across to it. The act of publishing my blog, as distinct from writing a post, is the part that is most vulnerable to flaky internet connectivity so it makes sense to host it on a device that always has good connectivity.

Now I write my posts on my iPad or my laptop and then upload it for publishing.

Setting up the Linode forced my to brush the cobwebs off the unix sysadmin part of my brain and served as a reminder that porting a workflow to a new platform is rarely a simple task.

What I learnt along the way
===========================

-   [tmux](https://tmux.github.io) is awesome.
-   ssh keys with passwords aren't as hard as I thought (ssh-agent with forwarding is brilliant)
-   [mosh](https://mosh.org) is a great idea, but it doesn't support ssh-agent (which is a deal-breaker)
-   iSSH looks good on the surface but lacks polish and has flaky mosh support
-   that different spell checking tools exist, and their word list is remarkably different (MySpell/GNU Aspell)
-   a few of things about how to get better connectivity while commuting (I'll write about that later)

What's left to do
=================

-   try mosh again once it supports ssh-agent (if the [pull request](https://github.com/mobile-shell/mosh/pull/423) is accepted)
-   get tmux working with ssh agent forwarding
-   streamline my publishing script now that I'll be running it remotely.
-   clean up the way I manage my dot files now that I have them on several machines

And this post was published with the new workflow... hooray!

