
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

# Specify these so we can move them outside the dropbox sync'ed area
# MUST be absolute
#OUTPUT_FOLDER='/Users/esteele/Code/wordspeak.org/output'
#CACHE_FOLDER='/Users/esteele/Code/wordspeak.org/cache'
OUTPUT_FOLDER=os.path.join(os.path.expanduser('~'), 'tmp/nikola_wordspeak_output')
CACHE_FOLDER=os.path.join(os.path.expanduser('~'), 'tmp/nikola_wordspeak_cache')

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

SEARCH_FORM = """
<span class="navbar-form pull-right">
<input type="text" id="tipue_search_input">
<input type="button" id="tipue_search_button">
</span>"""

ANALYTICS = """
<!-- <script type="text/javascript" src="/assets/js/tipuesearch_set.js"></script> -->
<!-- <script type="text/javascript" src="/assets/js/tipuesearch.js"></script> -->
<script type="text/javascript">
$(document).ready(function() {
    $('#tipue_search_input').tipuesearch({
        'mode': 'json',
        'contentLocation': '/assets/js/tipuesearch_content.json',
        'showUrl': false
    });
});
</script>
"""

EXTRA_HEAD_DATA = """
<!-- <link rel="stylesheet" type="text/css" href="/assets/css/tipuesearch.css"> -->
<div id="tipue_search_content" style="margin-left: auto; margin-right: auto; padding: 20px;"></div>
"""

ENABLED_EXTRAS = [
    "local_search",
]

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
