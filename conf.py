
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from nikola import __version__ as nikola_version
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
        ('/pages/projects.html', 'Software and Photos'),
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

# Name of the theme to use. Themes are located in themes/theme_name
#THEME = 'wordspeak_lite'
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
<input type="button" id="tipue_search_button" value="&#160;">
</span>"""

TIPUE_SUMMARY_LENGTH = 25
TIPUE_STOP_WORDS = ["and", "be", "by", "do", "for", "he", "how", "if", "is", "it", "my", "not", "of", "or", "the", "to", "up", "what", "when"]

ANALYTICS = """
<script type="text/javascript">
var tipuesearch_stop_words = %s;

var tipuesearch_replace = {"words": [
     {"word": "tipua", replace_with: "tipue"},
     {"word": "javscript", replace_with: "javascript"}
]};

var tipuesearch_stem = {"words": [
     {"word": "e-mail", stem: "email"},
     {"word": "javascript", stem: "script"},
     {"word": "javascript", stem: "js"}
]};

$(document).ready(function() {
    $('#tipue_search_input').tipuesearch({
        'mode': 'json',
        'contentLocation': '/assets/js/tipuesearch_content.json',
        'showUrl': false,
        'descriptiveWords': %s
    });
});
</script>
<!-- Built by Nikola v.%s on host %s -->
""" % (json.JSONEncoder().encode(TIPUE_STOP_WORDS), TIPUE_SUMMARY_LENGTH, nikola_version, getfqdn())

EXTRA_HEAD_DATA = """
<div id="tipue_search_content" style="margin-left: auto; margin-right: auto; padding: 1px;"></div>
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
