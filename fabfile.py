#!/usr/bin/env python3
"""Wordspeak build and deploy helper"""

import glob
import os
import re
from subprocess import DEVNULL, Popen, PIPE
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from fabric.api import abort, local
from fabric.colors import green, yellow
from fabric.context_managers import cd
import enchant
import enchant.checker
import enchant.tokenize
import requests
from chump import Application
import conf


TILDE = os.path.expanduser("~")
STAGING_FQDN = "staging.wordspeak.org"
STAGING_FILESYSTEM_ROOT = "Sites/staging.wordspeak.org"
STAGING_RSYNC_DESTINATION_LOCAL = os.path.join(TILDE, STAGING_FILESYSTEM_ROOT)
STAGING_RSYNC_DESTINATION_REMOTE = "%s:/home/esteele/%s" % \
                                   (STAGING_FQDN, STAGING_FILESYSTEM_ROOT)
PROD_FQDN = "origin.wordspeak.org"
PROD_FILESYSTEM_ROOT = "Sites/www.wordspeak.org"
PROD_RSYNC_DESTINATION_LOCAL = os.path.join(TILDE, PROD_FILESYSTEM_ROOT)
PROD_RSYNC_DESTINATION_REMOTE = "%s:/home/esteele/%s" % \
                                (PROD_FQDN, PROD_FILESYSTEM_ROOT)
# i.e. the directory containing this file
SITE_BASE = os.path.dirname(__file__)
OUTPUT_BASE = conf.OUTPUT_FOLDER
CACHE_BASE = conf.CACHE_FOLDER
SPELLCHECK_EXCEPTIONS = os.path.join(SITE_BASE, "spellcheck_exceptions.txt")
UNWANTED_BUILD_ARTIFACTS = [
    'd3-projects/basic_au_map/basic_au_map.html',
    'd3-projects/census_nt_indig_lang/nt_sla_map.html',
    'd3-projects/census_nt_indig_lang/nt_sla_scatter.html',
    'd3-projects/index_time_series/index-line.html',
    'd3-projects/stacked-column-ex/stacked-column-ex.html',
]
# An update of these files will abort a fab deploy operation
KEY_FILES = ["conf.py", "fabfile.py"]
W3C_HTML_VALIDATION_URL = 'https://validator.w3.org/nu/?doc=%s&out=%s'
W3C_HTML_VALIDATION_TARGETS = [
    'https://staging.wordspeak.org/index.html',
    'https://staging.wordspeak.org/pages/about.html',
    'https://staging.wordspeak.org/posts/write-because-you-want-to.html',
    'https://staging.wordspeak.org/posts/nsw-fires.html',
]
W3C_CSS_VALIDATION_URL = 'http://jigsaw.w3.org/css-validator/validator?' \
                         'uri=%s&profile=css3&usermedium=all&warning=1&' \
                         'vextwarning=&lang=en&output=%s'
W3C_CSS_VALIDATION_TARGETS = [
    'https://staging.wordspeak.org/assets/css/all-nocdn.css',
]
W3C_RSS_VALIDATION_URL = 'http://validator.w3.org/feed/check.cgi?url=%s'
W3C_RSS_VALIDATION_TARGETS = [
    'https://staging.wordspeak.org/rss.xml',
]
LANGUAGE_EXPLORER_DIRNAME = "language_explorer"


def _quietly_run_nikola_cmd(nikola, cmd):
    result = local("%s %s" % (nikola, cmd), capture=True)
    if "TaskFailed" in result.stdout or \
            "WARNING" in result.stderr:
        print("Stdout:")
        print(result.stdout)
        print("Stderr:")
        print(result.stderr)
        abort("Nikola command '%s' failed." % (cmd,))
    else:
        if result.stderr:
            print("%s actions performed" %
                  (len(result.stderr.splitlines()) - 1,))
        else:
            print("No output from command.")


def build():
    """Build the site using nikola"""
    with cd(SITE_BASE):
        _quietly_run_nikola_cmd("nikola", "build")
        # _quietly_run_nikola_cmd("nikola", "mincss")
        # Need to recopy the leaflet.css file as mincss optimises it away
        #  because it can't find any leaflet classes in use (they're inserted
        #  at runtime by the js library
        local("cp %s/files/assets/leaflet-0.7.3/leaflet.css "
              "%s/assets/leaflet-0.7.3/leaflet.css" % (SITE_BASE, OUTPUT_BASE))
        # Need to recompress css after yuicompressor has run
        #  Can't run post_render_gzip in N7, so let's just do build again
        _quietly_run_nikola_cmd("nikola", "build")

    post_build_cleanup()


def linkchecker(output_fd=sys.stdout):
    """Checks for broken links on the staging site

    Ignores posts because the links all appear in the index pages
    Returns whether the task found any 404s
    """
    args = [
        "nikola",
        "check",
        "-l",
        "-r",
        "--find-sources"
    ]

    with Popen(args, stderr=PIPE, stdout=DEVNULL) as proc:
        while proc.poll() is None:
            # Print something to indicate progress to the build
            print(".", end="", flush=True)
            time.sleep(5)

        err = proc.stderr.read()

    broken_links = [line for line in err.splitlines()
                    if 'Error 404' in line]
    # Broken links will appear in both lists, but that's ok, excluding
    #  INFO lines means we make sure we see other errors that aren't
    #  404.
    warning_lines = [line for line in err.splitlines()
                     if ' INFO: ' not in line]

    def print_warning_lines(lines, output_fd=output_fd):
        output_fd.write(yellow("Warnings found:\n"))
        for line in lines:
            output_fd.write(line + "\n")

    # We want to fail on broken links, but not on 500 errors or timeouts
    # The rationale is that they're most likely to be transient, and not
    #  something indicative of a failure on our end, so we wouldn't want
    #  to fail the build
    if broken_links:
        output_fd.write(yellow("Broken links found:\n"))
        for line in broken_links:
            output_fd.write(line + "\n")
        print_warning_lines(warning_lines, output_fd)
        sys.exit(1)
    else:
        output_fd.write(green("No broken links found.\n"))
        print_warning_lines(warning_lines, output_fd)
        sys.exit(0)


def clean():
    """Remove files generated by Nikola"""
    with cd(SITE_BASE):
        local("rm -rf %s %s" % (OUTPUT_BASE, CACHE_BASE))


def _get_spellcheck_exceptions(lines):
    for line in lines:
        if line.startswith(".. spellcheck_exceptions:"):
            # Use filter(None so that we don't crash if there aren't any
            #  words specified, even though the tag is there
            word_list = [s.strip() for s in
                         line.split(":")[1].strip().split(",")]
            return [_f for _f in word_list if _f]
    return []


def _non_directive_lines(lines):
    """filters out all the rst/markdown directives

    so the spell checker doesn't get confused"""
    in_code_directive = False
    for line in lines:
        if line.startswith("```"):
            if in_code_directive:
                in_code_directive = False
            else:
                in_code_directive = True

        if in_code_directive:
            continue

        if line.startswith("..") and not line.startswith(".. title:"):
            # rst directive starts with ^.. but these are only single-line
            #  directives used in the header
            continue

        if line.startswith("{{%"):
            # is a Nikola shortcode... ignore
            continue

        yield line


def _add_to_spellcheck_exceptions(input_file, word):
    with open(input_file) as f:
        contents = f.read()

    # A trailing comma is acceptable on the spellcheck_exceptions line
    contents = contents.replace(".. spellcheck_exceptions: ",
                                ".. spellcheck_exceptions: %s," % (word,))

    with open(input_file, "w") as f:
        f.write(contents)
    print("Added '%s' to spell check exception list for file %s" %
          (word, input_file))


def _replace_in_file(input_file, old_word, new_word):
    with open(input_file) as f:
        contents = f.read()
        contents = re.sub(r'(\s)%s(\s)' % (old_word,),
                          r'\1%s\2' % (new_word,),
                          contents)  # word on its own
        contents = re.sub(r'(\s)%s' % (old_word,),
                          r'\1%s' % (new_word,),
                          contents)  # word at end of file
        contents = re.sub(r'%s(\s)' % (old_word,),
                          r'%s\1' % (new_word,),
                          contents)  # word at start of file
    with open(input_file, "w") as f:
        f.write(contents)
    print("Replaced %s with %s in %s" % (old_word, new_word, input_file))


def strip_markdown_directives(line):
    line = line.strip()
    if line.startswith("<") and line.endswith(">"):
        # Let's assume it's inline HTML and skip it
        return ""

    # Remove URLs (assume remote starts with http and local ends with html)
    line = re.sub(r'\[(.+?)]\(http[^\)]+\)', r'\1', line)
    line = re.sub(r'\[(.+?)]\(.+?html\)', r'\1', line)
    line = re.sub(r'<http:.+?>', r'', line)
    return line


def spellchecker(is_interactive_deploy=True):
    """Spellcheck the Markdown and ReST files on the site"""

    spelling_errors_found = False

    # aspell is available on mac by default, and I don't want to manage custom
    #  word lists for both aspell and myspell so we'll just use aspell
    enchant._broker.set_ordering("en_GB", "aspell")
    pwl_dictionary = enchant.request_pwl_dict(SPELLCHECK_EXCEPTIONS)
    en_spellchecker = enchant.checker.SpellChecker(
        "en_GB",
        filters=[enchant.tokenize.EmailFilter, enchant.tokenize.URLFilter]
    )
    md_posts = glob.glob(os.path.join(SITE_BASE, "posts", "*.md"))
    md_pages = glob.glob(os.path.join(SITE_BASE, "stories", "*.md"))

    for file_to_check in md_pages + md_posts:
        with open(file_to_check, 'r', encoding="utf-8") as f:
            lines = f.readlines()

        for exc in _get_spellcheck_exceptions(lines):
            pwl_dictionary.add_to_session(exc)

        for line in _non_directive_lines(lines):
            en_spellchecker.set_text(strip_markdown_directives(line))
            for err in en_spellchecker:
                if not pwl_dictionary.check(err.word):
                    spelling_errors_found = True
                    spelling_error = \
                        "Not in dictionary: %s (file: %s " \
                        "line: %s). Suggestions: %s" % \
                        (err.word,
                         os.path.basename(file_to_check),
                         lines.index(line) + 1,
                         ", ".join(en_spellchecker.suggest(err.word))
                         )
                    print(spelling_error)
                    _send_pushover_summary(
                        spelling_error, "Spelling error: %s" % (err.word,))

    return spelling_errors_found


def w3c_checks(output_fd=sys.stdout):
    all_checks_pass = True
    for url in W3C_HTML_VALIDATION_TARGETS:
        r = requests.get(W3C_HTML_VALIDATION_URL %
                         (urllib.parse.quote_plus(url), "json"))
        # messages key in JSON output always exists
        error_messages = [m["message"] for m in r.json()["messages"]
                          if m["type"] != "info"]
        if error_messages:
            output_fd.write("HTML has W3C validation errors (%s):\n" % (url,))
            for message in error_messages:
                output_fd.write("- %s" % (message.encode('utf-8'),))
            output_fd.write("\n")
            output_fd.write(
                "Full details: %s\n" %
                (W3C_HTML_VALIDATION_URL %
                 (urllib.parse.quote_plus(url), "html"),)
            )
            all_checks_pass = False
        else:
            output_fd.write("HTML validates (%s)\n" % (url,))

    for url in W3C_CSS_VALIDATION_TARGETS:
        r = requests.get(W3C_CSS_VALIDATION_URL %
                         (urllib.parse.quote_plus(url), "text"))
        summary = [l.strip() for l in r.text.split('\n') if l.strip()][1]
        if "Congratulations" in summary:
            output_fd.write("CSS validates (%s)\n" % (url,))
        else:
            output_fd.write("CSS validation failures for %s\n" % (url,))
            output_fd.write("%s\n" % (summary.encode('utf-8'),))
            output_fd.write(
                "Full details: %s\n" % (W3C_CSS_VALIDATION_URL %
                                        (urllib.parse.quote_plus(url),
                                         "html")
                                        )
            )
            all_checks_pass = False
    for url in W3C_RSS_VALIDATION_TARGETS:
        r = requests.get(W3C_RSS_VALIDATION_URL %
                         (urllib.parse.quote_plus(url),)
                         )
        # UGLY, and fragile but there's no machine readable output available
        if "This is a valid RSS feed" in r.text:
            output_fd.write("RSS validates (%s)\n" % (url,))
        else:
            output_fd.write("RSS validation failures for %s\n" % (url,))
            output_fd.write(
                "Full details: %s\n" %
                (W3C_RSS_VALIDATION_URL % (urllib.parse.quote_plus(url)))
            )
            all_checks_pass = False

    if all_checks_pass:
        sys.exit(0)
    else:
        sys.exit(1)


def post_build_cleanup():
    """Get rid of the stuff that we don't want to push but was built
    (and can't easily be disabled"""
    with cd(OUTPUT_BASE):
        for f in UNWANTED_BUILD_ARTIFACTS:
            local("rm -f %s" % (f,))


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise RuntimeError(error_msg)


def _initialise():
    """Make sure we have all the python modules needed for the build"""
    get_env_variable("WORDSPEAK_PUSHOVER_USER")
    get_env_variable("WORDSPEAK_PUSHOVER_API_TOKEN")


def _send_pushover_summary(message, title):
    app = Application(get_env_variable("WORDSPEAK_PUSHOVER_API_TOKEN"))
    user = app.get_user(get_env_variable("WORDSPEAK_PUSHOVER_USER"))
    return user.send_message(message=message, title=title)
