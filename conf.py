"""
Nikola configuration for wordspeak.org site
"""

# -*- coding: utf-8 -*-
import os
from nikola import filters

BLOG_AUTHOR = "Edwin Steele"
BLOG_TITLE = "Wordspeak"
SITE_URL = "https://www.wordspeak.org/"
BLOG_EMAIL = "edwin@wordspeak.org"
BLOG_DESCRIPTION = "Edwin's writings."

DEFAULT_LANG = "en"

# NOT USED - HARD CODED IN TEMPLATE
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

# MUST be absolute - XXX. Why must it be absolute?
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'output')
CACHE_FOLDER = os.path.join(os.path.dirname(__file__), 'cache')

MARKDOWN_EXTENSIONS = [
    'fenced_code',
    'codehilite',
    'footnotes',
    'tables',
    'def_list',
]

COPY_SOURCES = False
SHOW_SOURCELINK = False
USE_CDN = False
GZIP_FILES = True
GZIP_EXTENSIONS = ('.html', '.css', '.js', '.json', '.geojson', '.ico',
                   '.eot', '.svg', '.ttf', '.woff', '.xml')
DISABLED_PLUGINS = ["render_galleries"]

FILTERS = {
    ".html": [filters.typogrify],
}

# Name of the theme to use. Themes are located in themes/theme_name
THEME = 'wordspeak_lite'

# Not used. Stored in template now.
CONTENT_FOOTER = ""

COMMENT_SYSTEM = False
INDEX_DISPLAY_POST_COUNT = 5
CREATE_SINGLE_ARCHIVE = True
WRITE_TAG_CLOUD = False

SEARCH_FORM = ""
EXTRA_HEAD_DATA = ""

TIMEZONE = 'Australia/Sydney'
