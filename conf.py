
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import time

BLOG_AUTHOR = "Edwin Steele"
BLOG_TITLE = "Wordspeak"
SITE_URL = "http://www.wordspeak.org"
BLOG_EMAIL = "edwin@wordspeak.org"
BLOG_DESCRIPTION = "Edwin's writings."

DEFAULT_LANG = "en"
TRANSLATIONS = {
    DEFAULT_LANG: "",
}

SIDEBAR_LINKS = {
    DEFAULT_LANG: (
        ('/pages/about.html', 'About'),
        ('/pages/projects.html', 'Projects'),
        ('/pages/photos-and-video.html', 'Photos and Video'),
        ('/archive.html', 'Archives'),
        ('/rss.xml', 'RSS Feed'),
        ),
    }

post_pages = (
    ("posts/*.rst", "posts", "post.tmpl", True),
    ("stories/*.rst", "pages", "story.tmpl", False),
)

post_compilers = {
    "rest": ('.rst', '.txt'),
}

USE_CDN = True
GZIP_FILES = True
GZIP_EXTENSIONS = ('.html', '.css', '.js', '.json', '.geojson')
DISABLED_PLUGINS = ["render_galleries"]

# Name of the theme to use. Themes are located in themes/theme_name
THEME = 'wordspeak'

# A small copyright notice for the page footer (in HTML)
CONTENT_FOOTER = 'Uncopyright. No rights reserved | <a href="/pages/licensing.html">Why give it away?</a>'

DISQUS_FORUM = False
ADD_THIS_BUTTONS = False
INDEX_DISPLAY_POST_COUNT = 5
# XXX - what should this be?
# RSS_TEASERS = True

# Put in global_context things you want available on all your templates.
# It can be anything, data, functions, modules, etc.
GLOBAL_CONTEXT = {
    'blog_author': BLOG_AUTHOR,
    'blog_title': BLOG_TITLE,
    'blog_desc': BLOG_DESCRIPTION,
    'translations': TRANSLATIONS,
    'disqus_forum': DISQUS_FORUM,
    'content_footer': CONTENT_FOOTER,
    'site_url': SITE_URL,
    'sidebar_links': SIDEBAR_LINKS,
}
