
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from nikola import __version__ as nikola_version
from nikola import filters
import os
import rcssmin
import socket

BLOG_AUTHOR = "Edwin Steele"
BLOG_TITLE = "Wordspeak"
SITE_URL = "https://www.wordspeak.org/"
BLOG_EMAIL = "edwin@wordspeak.org"
BLOG_DESCRIPTION = "Edwin's writings."

DEFAULT_LANG = "en"
#TRANSLATIONS = {
#    DEFAULT_LANG: "en",
#}

# XXX - NOT USED - HARD CODED IN TEMPLATE
SIDEBAR_LINKS = NAVIGATION_LINKS = {
    DEFAULT_LANG: (),
}

POSTS = (
    ("posts/*.md", "posts", "post.tmpl"),
)

PAGES = (
    ("stories/*.md", "pages", "story.tmpl"),
)

COMPILERS = {
    "markdown": ('.md', '.mdown', '.markdown'),
}

FAVICONS = {
    ("icon", "/favicon.ico", "16x16"),
}

# Specify these so we can move them outside the dropbox sync'ed area
# MUST be absolute
#OUTPUT_FOLDER='/Users/esteele/Code/wordspeak.org/output'
#CACHE_FOLDER='/Users/esteele/Code/wordspeak.org/cache'
OUTPUT_FOLDER = os.path.join(os.path.expanduser('~'), 'tmp/nikola_wordspeak_output')
CACHE_FOLDER = os.path.join(os.path.expanduser('~'), 'tmp/nikola_wordspeak_cache')

MARKDOWN_EXTENSIONS = ['fenced_code', 'codehilite', 'footnotes', 'tables', 'def_list']

COPY_SOURCES = False
SHOW_SOURCELINK = False
USE_CDN = False
GZIP_FILES = True
GZIP_EXTENSIONS = ('.html', '.css', '.js', '.json', '.geojson',
                   '.eot', '.svg', '.ttf', '.woff', '.xml')
DISABLED_PLUGINS = ["render_galleries"]

FILTERS = {
    ".css": [filters.apply_to_text_file(rcssmin.cssmin)],
    ".html": [filters.typogrify],
}

LINK_CHECK_WHITELIST = ["index-[0-9]+.html"]

# Name of the theme to use. Themes are located in themes/theme_name
THEME = 'wordspeak_lite'

# A small copyright notice for the page footer (in HTML)
# XXX - Not used. Stored in template now.
CONTENT_FOOTER = ""

COMMENT_SYSTEM = False
INDEX_DISPLAY_POST_COUNT = 5
CREATE_SINGLE_ARCHIVE = True
WRITE_TAG_CLOUD = False

SEARCH_FORM = ""

BODY_END = """
<!-- Built by Nikola v.%s on host %s -->
""" % (nikola_version, socket.gethostname())

EXTRA_HEAD_DATA = ""

TIMEZONE = 'Australia/Sydney'

# Put in global_context things you want available on all your templates.
# It can be anything, data, functions, modules, etc.
#GLOBAL_CONTEXT = {
#    'blog_author': BLOG_AUTHOR,
#    'blog_title': BLOG_TITLE,
#    'blog_desc': BLOG_DESCRIPTION,
#    'translations': TRANSLATIONS,
#    'disqus_forum': DISQUS_FORUM,
#    'content_footer': CONTENT_FOOTER,
#    'site_url': SITE_URL,
#    'sidebar_links': SIDEBAR_LINKS,
#}
