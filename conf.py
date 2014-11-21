
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from nikola import __version__ as nikola_version
from nikola import filters
from socket import getfqdn
import json
import os
import time

# Comment to force update. Deleteme.

BLOG_AUTHOR = "Edwin Steele"
BLOG_TITLE = "Wordspeak"
SITE_URL = "https://www.wordspeak.org"
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
        ('/categories/index.html', 'Categories'),
        ('/rss.xml', 'RSS'),
        ),
    }

post_pages = (
    ("posts/*.md", "posts", "post.tmpl", True),
    ("posts/*.rst", "posts", "post.tmpl", True),
    ("stories/*.rst", "pages", "story.tmpl", False),
)

post_compilers = {
    "markdown": ('.md', '.mdown', '.markdown'),
    "rest": ('.rst', '.txt'),
}

# Specify these so we can move them outside the dropbox sync'ed area
# MUST be absolute
#OUTPUT_FOLDER='/Users/esteele/Code/wordspeak.org/output'
#CACHE_FOLDER='/Users/esteele/Code/wordspeak.org/cache'
OUTPUT_FOLDER=os.path.join(os.path.expanduser('~'), 'tmp/nikola_wordspeak_output')
CACHE_FOLDER=os.path.join(os.path.expanduser('~'), 'tmp/nikola_wordspeak_cache')

HIDE_SOURCELINK = True
USE_CDN = False
GZIP_FILES = True
GZIP_EXTENSIONS = ('.html', '.css', '.js', '.json', '.geojson')
DISABLED_PLUGINS = ["render_galleries"]

def yui_compressor(infile):
    from nikola.filters import apply_to_file, runinplace
    return runinplace(r'squeeze yuicompressor %1 -o %2', infile)

FILTERS = {
    ".css": [yui_compressor],
    ".html": [filters.typogrify],
}

# Name of the theme to use. Themes are located in themes/theme_name
THEME = 'wordspeak_lite'
#THEME = 'wordspeak'

# A small copyright notice for the page footer (in HTML)
CONTENT_FOOTER = 'Site by <a href="/pages/about.html">Edwin Steele</a> | Uncopyright. No rights reserved | <a href="/pages/licensing.html">Why give it away?</a>'

DISQUS_FORUM = False
ADD_THIS_BUTTONS = False
INDEX_DISPLAY_POST_COUNT = 5
# XXX - what should this be?
# RSS_TEASERS = True

SEARCH_FORM = ""

ANALYTICS = """
<!-- Built by Nikola v.%s on host %s -->
""" % (nikola_version, getfqdn())

EXTRA_HEAD_DATA = ""

ENABLED_EXTRAS = [ ]

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
