#!/usr/bin/env python3
"""Wordspeak build and deploy helper"""

import glob
import os
import re
import platform
import shutil
import subprocess
import time
import urllib.request
import urllib.parse
import urllib.error
import click
import cloudinary
import cloudinary.uploader
import enchant
import enchant.checker
import enchant.tokenize
import requests
from geopy.geocoders import Nominatim
import conf


# i.e. the directory containing this file
SITE_BASE = os.path.dirname(__file__)
OUTPUT_BASE = conf.OUTPUT_FOLDER
CACHE_BASE = conf.CACHE_FOLDER
UNWANTED_BUILD_ARTIFACTS = [
    'd3-projects/basic_au_map/basic_au_map.html',
    'd3-projects/census_nt_indig_lang/nt_sla_map.html',
    'd3-projects/census_nt_indig_lang/nt_sla_scatter.html',
    'd3-projects/index_time_series/index-line.html',
    'd3-projects/stacked-column-ex/stacked-column-ex.html',
]
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
SINGLE_ORIGIN_DEF_FILE = "files/assets/single_origin_coffee_data.txt"


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise RuntimeError(error_msg)


class SingleOriginCoffee:
    def __init__(self, country, title, region, varietal, lat, lon):
        self.country = country
        self.title = title
        self.region = region
        self.varietal = varietal
        self.lat = lat
        self.lon = lon

    def as_statement(self):
        return '  L.marker([%s, %s]).addTo(map).bindPopup("%s (%s, %s)");' % \
                (self.lat, self.lon, self.title, self.region, self.country)


def extract_coffee_definitions(filename):
    soc_list = []

    with open(filename) as fd:
        lines = fd.readlines()

    for line in lines:
        # Country is always first
        country_str = line.partition(" ")[0].strip()
        title_str = line.partition(".")[0].strip()
        # Optional region after the first period
        dot_sep = line.split(".")
        if len(dot_sep) > 1:
            full_region_str = dot_sep[1].partition("(")[0].strip()
            end_of_region_data_idx = full_region_str.lower().find("region")
            if end_of_region_data_idx != -1:
                region_str = full_region_str[:end_of_region_data_idx-1]
            else:
                region_str = full_region_str
        else:
            region_str = ""

        soc = SingleOriginCoffee(country_str, title_str, region_str, "", 0, 0)
        soc_list.append(soc)

    return soc_list


@click.group()
def cli():
    click.echo("Starting wordspeak tool")


@cli.command()
def coffee_defs():
    """Convert coffee csv to leaflet javascript"""
    soc_list = extract_coffee_definitions(SINGLE_ORIGIN_DEF_FILE)
    geolocator = Nominatim(timeout=10)

    unable_to_resolve = []

    print("function addPoints() {")
    for soc in soc_list:
        location_str = "%s, %s" % (soc.region, soc.country)
        loc = geolocator.geocode(location_str)
        if loc:
            soc.lat = loc.latitude
            soc.lon = loc.longitude
            print(soc.as_statement())
        else:
            unable_to_resolve.append("Unable to resolve %s" % (location_str,))

    print("};")

    print()
    for utr in unable_to_resolve:
        print("// %s" % (utr,))


@cli.command()
def build():
    """Build the site using nikola"""
    subprocess.check_call(["nikola", "build"], cwd=SITE_BASE)
    # Get rid of the stuff that we don't want to push but was built
    #  (and can't easily be disabled)
    #
    # XXXXXXXXXXXXXXXXXXXX uncomment
    #for uba in UNWANTED_BUILD_ARTIFACTS:
    #    os.remove(os.path.join(OUTPUT_BASE, uba))


@cli.command()
def linkchecker():
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

    with subprocess.Popen(args,
                          stderr=subprocess.PIPE,
                          stdout=subprocess.DEVNULL,
                          universal_newlines=True) as proc:
        while proc.poll() is None:
            # Print something to indicate progress to the build
            print(".", end="", flush=True)
            time.sleep(5)

        # universal_newlines means this is text, not bytes
        err = proc.stderr.read()

    broken_links = [line for line in err.splitlines()
                    if 'Error 404' in line]
    # Broken links will appear in both lists, but that's ok, excluding
    #  INFO lines means we make sure we see other errors that aren't
    #  404.
    warning_lines = [line for line in err.splitlines()
                     if ' INFO: ' not in line]

    def print_warning_lines(lines):
        """extract warning lines from nikola check output"""
        print("Warnings found:")
        for line in lines:
            print(line)

    # We want to fail on broken links, but not on 500 errors or timeouts
    # The rationale is that they're most likely to be transient, and not
    #  something indicative of a failure on our end, so we wouldn't want
    #  to fail the build
    if broken_links:
        print("Broken links found:")
        for line in broken_links:
            print(line)
        print_warning_lines(warning_lines)
        raise click.ClickException("Broken links found. Exiting with failure")
    else:
        print("No broken links found.")
        print_warning_lines(warning_lines)


@cli.command()
def clean():
    """Remove files generated by Nikola"""
    shutil.rmtree(OUTPUT_BASE, ignore_errors=True)
    shutil.rmtree(CACHE_BASE, ignore_errors=True)


@cli.command()
@click.argument('file_to_upload')
def cloudinary_upload(file_to_upload):
    cloudinary.config(
        cloud_name=get_env_variable("CLOUDINARY_CLOUD_NAME"),
        api_key=get_env_variable("CLOUDINARY_API_KEY"),
        api_secret=get_env_variable("CLOUDINARY_API_SECRET")
    )
    expected_public_id = os.path.splitext(os.path.basename(file_to_upload))[0]
    response = cloudinary.api.resources_by_ids(expected_public_id)
    if response["resources"]:
        raise click.ClickException("Resource already exists named %s: %s" % \
                                   (expected_public_id, response["resources"]))

    if not os.path.isfile(file_to_upload):
        raise click.ClickException("'%s' is not a file." % (file_to_upload,))

    click.echo("Upon successful upload this will be available as "
               "cloudinary_id='%s' for the wordspeak_image shortcode" \
               % (expected_public_id,))
    click.echo("Uploading file %s as %s" % \
               (file_to_upload, expected_public_id))
    response = cloudinary.uploader.upload(
        file_to_upload,
        public_id=expected_public_id,
        tags="wordspeak"
    )
    click.echo("Upload complete: %s" % (response,))


def _get_spellcheck_exceptions(lines):
    for line in lines:
        if line.startswith(".. spellcheck_exceptions:"):
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


def strip_markdown_directives(line):
    """strips markdown directives from a line"""
    line = line.strip()
    if line.startswith("<") and line.endswith(">"):
        # Let's assume it's inline HTML and skip it
        return ""

    # Remove URLs (assume remote starts with http and local ends with html)
    line = re.sub(r'\[(.+?)]\(http[^\)]+\)', r'\1', line)
    line = re.sub(r'\[(.+?)]\(.+?html\)', r'\1', line)
    line = re.sub(r'<http:.+?>', r'', line)
    return line


@cli.command()
def spellchecker():
    """Spellcheck the Markdown and ReST files on the site"""

    if platform.system() == "Darwin":
        # Mac seems to use ispell as a default, but openbsd and linux
        #  use aspell. No need to maintain exceptions for multiple
        #  dictionaries.
        raise click.ClickException(
            "Spellchecker not supported on Mac due to different "
            "enchant backends"
        )

    spelling_errors_found = False

    md_posts = glob.glob(os.path.join(SITE_BASE, "posts", "*.md"))
    md_pages = glob.glob(os.path.join(SITE_BASE, "stories", "*.md"))

    for file_to_check in md_pages + md_posts:
        en_spellchecker = enchant.checker.SpellChecker(
            "en_GB",
            filters=[enchant.tokenize.EmailFilter, enchant.tokenize.URLFilter]
        )
        with open(file_to_check, 'r', encoding="utf-8") as f:
            lines = f.readlines()

        for exc in _get_spellcheck_exceptions(lines):
            en_spellchecker.add(exc)

        file_text = " ".join([strip_markdown_directives(l)
                              for l in _non_directive_lines(lines)])
        en_spellchecker.set_text(file_text)
        for err in en_spellchecker:
            spelling_errors_found = True
            context = "%s%s%s" % (
                en_spellchecker.leading_context(30),
                en_spellchecker.word,
                en_spellchecker.trailing_context(30),
            )
            spelling_error = \
                "Not in dictionary: %s (file: %s " \
                "context: %s). Suggestions: %s" % \
                (err.word,
                 os.path.basename(file_to_check),
                 context,
                 ", ".join(en_spellchecker.suggest(err.word))
                )
            print(spelling_error)

    if spelling_errors_found:
        raise click.ClickException("Spelling errors found.")


@cli.command()
def w3c_checks():
    """validate staging with w3c html css and rss validators"""
    all_checks_pass = True
    for url in W3C_HTML_VALIDATION_TARGETS:
        r = requests.get(W3C_HTML_VALIDATION_URL %
                         (urllib.parse.quote_plus(url), "json"))
        # messages key in JSON output always exists
        error_messages = [m["message"] for m in r.json()["messages"]
                          if m["type"] != "info"]
        if error_messages:
            print("HTML has W3C validation errors (%s):" % (url,))
            for message in error_messages:
                print("- %s" % (message.encode('utf-8'),), end=" ")
            print()
            print(
                "Full details: %s" %
                (W3C_HTML_VALIDATION_URL %
                 (urllib.parse.quote_plus(url), "html"),)
            )
            all_checks_pass = False
        else:
            print("HTML validates (%s)" % (url,))

    for url in W3C_CSS_VALIDATION_TARGETS:
        r = requests.get(W3C_CSS_VALIDATION_URL %
                         (urllib.parse.quote_plus(url), "text"))
        summary = [l.strip() for l in r.text.split('\n') if l.strip()][1]
        if "Congratulations" in summary:
            print("CSS validates (%s)" % (url,))
        else:
            print("CSS validation failures for %s" % (url,))
            print("%s" % (summary.encode('utf-8'),))
            print(
                "Full details: %s" %
                (W3C_CSS_VALIDATION_URL % (urllib.parse.quote_plus(url),
                                           "html"))
            )
            all_checks_pass = False
    for url in W3C_RSS_VALIDATION_TARGETS:
        r = requests.get(W3C_RSS_VALIDATION_URL %
                         (urllib.parse.quote_plus(url),)
                        )
        # UGLY, and fragile but there's no machine readable output available
        if "This is a valid RSS feed" in r.text:
            print("RSS validates (%s)" % (url,))
        else:
            print("RSS validation failures for %s" % (url,))
            print(
                "Full details: %s" %
                (W3C_RSS_VALIDATION_URL % (urllib.parse.quote_plus(url)))
            )
            all_checks_pass = False

    if not all_checks_pass:
        raise click.ClickException("Checks failed. Exiting with failure.")


if __name__ == "__main__":
    cli()
