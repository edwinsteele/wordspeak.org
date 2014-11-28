<!--
.. title: Preserving WordPress permalinks in Nikola
.. slug: preserving-wordpress-permalinks-in-nikola
.. date: 2013/02/09 16:41:29
.. tags: Technology, UNIX
.. link: 
.. description: 
-->


Last month I moved from having a dynamic [WordPress](http://wordpress.org) blog to having a statically built blog generated by [Nikola](http://getnikola.com). I wanted to preserve the WordPress-style post and RSS URLs when I migrated and while I could have manually created [redirections](http://getnikola.com/handbook.html#redirections) within Nikola, I thought I could do better through web server directives.

My WordPress installation generated posts URLs in the form `http://wordspeak.org/yyyy/mm/dd/some_post_name`. After using the WordPress importer in Nikola, that post now exists at `http://wordspeak.org/posts/yyyymmddsome_post_name.html`. I noticed that Apache RewriteRules didn't play nicely with the relative paths that Nikola generates but I found I could achieve what I wanted with the Redirect family of directives.

Here's a snippet of my Apache `.htaccess` file to handle these redirections.

```apacheconf
RedirectMatch permanent ^/([0-9]{4})/([0-9]{2})/([0-9]{2})/([a-z][-a-z0-9]*)$ /posts/$1$2$3$4.html
# /feed /feed/ /feed/rss /feed?=http://wordspeak.org
RedirectMatch permanent ^/feed /rss.xml
RedirectPermanent /rss /rss.xml
```

Hopefully someone will find this valuable.
