# Copyright (c) 2012 Roberto Alsina y otros.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import unicode_literals
import codecs
import json
import os
import string
import types

from nikola.plugin_categories import LateTask
from nikola.utils import config_changed, copy_tree

# This is what we need to produce:
#var tipuesearch = {"pages": [
    #{"title": "Tipue Search, a jQuery site search engine", "text": "Tipue
        #Search is a site search engine jQuery plugin. It's free for both commercial and
        #non-commercial use and released under the MIT License. Tipue Search includes
        #features such as word stemming and word replacement.", "tags": "JavaScript",
        #"loc": "http://www.tipue.com/search"},
    #{"title": "Tipue Search demo", "text": "Tipue Search demo. Tipue Search is
        #a site search engine jQuery plugin.", "tags": "JavaScript", "loc":
        #"http://www.tipue.com/search/demo"},
    #{"title": "About Tipue", "text": "Tipue is a small web development/design
        #studio based in North London. We've been around for over a decade.", "tags": "",
        #"loc": "http://www.tipue.com/about"}
#]};


class Tipue(LateTask):
    """Render the blog posts as JSON data."""

    name = "local_search"

    def gen_tasks(self):
        self.site.scan_posts()

        kw = {
            "translations": self.site.config['TRANSLATIONS'],
            "output_folder": self.site.config['OUTPUT_FOLDER'],
        }

        posts = self.site.timeline[:]
        dst_path = os.path.join(kw["output_folder"], "assets", "js",
                                "tipuesearch_content.json")

        def summarise_text(text):
            """
            summary is the first TIPUE_SUMMARY_LENGTH words, followed by the
            unique words from the rest of the post, in lower case and with
            punctuation removed. The first
            TIPUE_SUMMARY_LENGTH words are displayed in the search results
            """
            summary = " ".join(text.split()[:self.site.config['TIPUE_SUMMARY_LENGTH'] + 1])
            # Look at the rest of the words (no need to consider summary twice
            #  and remove punctuation (we do this before we look at string
            #  length further down. This means that "don't" is actually a 4
            #  letter word, as intended

            # oh joy, markdown-derived posts come through as strings, and rst
            #  come through as unicode.
            # Helper for unicode punctuation, even though there are many more
            #  types of unicode punctuation
            remove_punctuation_map = dict((ord(char), None)
                                          for char in string.punctuation)
            # Unicode single quote
            remove_punctuation_map[ord(u'\u2019')] = None
            # Unicode left double quote
            remove_punctuation_map[ord(u'\u201c')] = None
            # Unicode right double quote
            remove_punctuation_map[ord(u'\u201d')] = None

            words = set()
            for word in text.split()[self.site.config['TIPUE_SUMMARY_LENGTH'] + 1:]:
                # all tipue matches are case insensitive
                #  so no need to have upper and lower in our list
                if isinstance(word, types.StringType):
                    w = word.translate(None, string.punctuation).lower()
                elif isinstance(word, types.UnicodeType):
                    w = word.translate(remove_punctuation_map).lower()
                else:
                    print "Don't know how to handle word - '%s'" % (word,)
                    w = ""
                if len(w) >= self.site.config['TIPUE_MIN_SEARCH_LENGTH']:
                    words.add(w)

            words = words.difference(self.site.config['TIPUE_STOP_WORDS'])
            return summary + " " + " ".join(words)

        def save_data():
            import logging
            pages = []
            for lang in kw["translations"]:
                for post in posts:
                    # Don't index drafts (Issue #387)
                    if post.is_draft:
                        continue
                    text = summarise_text(post.text(lang, strip_html=True))
                    text = text.replace('^', '')
                    logging.error("Text length is %s for %s" % (len(text), post.title(lang)))

                    data = {}
                    data["title"] = post.title(lang)
                    data["text"] = text
                    data["tags"] = ",".join(post.tags)
                    data["loc"] = post.permalink(lang)
                    pages.append(data)
            output = json.dumps({"pages": pages}, indent=2)
            try:
                os.makedirs(os.path.dirname(dst_path))
            except:
                pass
            with codecs.open(dst_path, "wb+", "utf8") as fd:
                fd.write(output)

        yield {
            "basename": str(self.name),
            "name": dst_path,
            "targets": [dst_path],
            "actions": [(save_data, [])],
            'uptodate': [config_changed(kw)],
            'task_dep': ['render_pages']
        }

        # Copy all the assets to the right places
        asset_folder = os.path.join(os.path.dirname(__file__), "files")
        for task in copy_tree(asset_folder, kw["output_folder"]):
            task["basename"] = str(self.name)
            yield task
