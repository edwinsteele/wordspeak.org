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
CONTENT_FOOTER = """
<div class="footerbox">
Site by <a title="About the author" href="/pages/about.html">Edwin Steele</a>
<a title="Email" href="mailto:edwin@wordspeak.org">
  <svg role="img" aria-label="Send email" width="1em" viewBox="0 0 1000 1000" fill="#08C">
    <title>Send email</title>
	<path d="m1000 454v-443q0-37-26-63t-63-27h-822q-36 0-63 27t-26 63v443q25-28 56-49 202-137 278-192 32-24 51-37t53-27 61-13h2q28 0 61 13t53 27 51 37q95 68 278 192 32 22 56 49z m0 164q0-44-27-84t-68-69q-210-146-262-181-5-4-23-17t-30-22-29-18-33-15-27-5h-2q-12 0-27 5t-33 15-29 18-30 22-23 17q-51 35-147 101t-114 80q-35 23-65 64t-31 77q0 43 23 72t66 29h822q36 0 62-26t27-63z" transform="scale(1,-1) translate(0, -1000)"/>
  </svg>
</a> |
Uncopyright. No rights reserved |
<a title="Site Licencing" href="/pages/licensing.html">Why give it away?</a>
</div>
"""

COMMENT_SYSTEM = False
INDEX_DISPLAY_POST_COUNT = 5
CREATE_SINGLE_ARCHIVE = True
WRITE_TAG_CLOUD = False

SEARCH_FORM = ""
EXTRA_HEAD_DATA = ""

TIMEZONE = 'Australia/Sydney'
