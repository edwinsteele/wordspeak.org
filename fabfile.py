from fabric.api import abort, local, settings
from fabric.contrib.console import confirm
from fabric.context_managers import cd, quiet
import csv
import glob
import os
import re
import enchant
import enchant.checker
from enchant.tokenize import EmailFilter, URLFilter, Filter


STAGING_FQDN = "staging.wordspeak.org"
STAGING_RSYNC_DESTINATION = "/Users/esteele/Sites/staging.wordspeak.org"
PROD_RSYNC_DESTINATION = "wordspeak.org:/users/home/esteele/web/public"
DEV_NIKOLA = "/Users/esteele/Code/nikola-edwinsteele/nikola/scripts/nikola"
REL_NIKOLA = "/Users/esteele/.virtualenvs/wordspeak/bin/nikola"
SITE_BASE = "/Users/esteele/Code/wordspeak.org"
OUTPUT_DIR = os.path.join(SITE_BASE, "output")


class RstURLFilter(Filter):
    """Filter skipping over URLs.
    This filter skips any words matching the following regular expression:

           ^<[a-zA-z]+:\/\/[^\s].*>`_

    That is, any words that are RST defined URLs.
    """
    _DOC_ERRORS = ["zA"]
    _pattern = re.compile(r"^<([a-zA-z]+:/)?/[^\s].*>`_")

    def _skip(self, word):
        if self._pattern.match(word):
            return True
        return False


class RstEmailFilter(Filter):
    """Filter skipping over restructure text directives
    """
    _DOC_ERRORS = ["zA"]
    _pattern = re.compile(r"^<mailto:.+@[^\.].*\.[a-z]{2,}>`_$")

    def _skip(self, word):
        if self._pattern.match(word):
            return True
        return False


def nikola_build():
    with quiet():
        if local("test '$(showvirtualenv)' == 'nikola-dev'").succeeded:
            nikola = DEV_NIKOLA
        else:
            nikola = REL_NIKOLA

    with cd(SITE_BASE):
        result = local("%s build" % (nikola,), capture=True)
        if "TaskFailed" in result.stdout or \
                "WARNING" in result.stderr:
            print "Stdout:"
            print result.stdout
            print "Stderr:"
            print result.stderr
            abort("Build failed.")
        else:
            print "%s actions performed\n" % \
                  (len(result.stdout.splitlines()) - 1),


def requirements_dump():
    with cd(SITE_BASE):
        local("pip freeze > requirements.txt")


def repo_status():
    result = local("git status --porcelain", capture=True)
    if result.stdout:
        print result.stdout
        if not confirm("Repo has uncommitted/untracked files. Continue?"):
            abort("Aborting at user request.")


def sync(destination_path):
    with cd(SITE_BASE):
        local("rsync --delete-after -a output/ %s" % (destination_path,))
        local("rsync --delete-after -a output/.htaccess %s" %
              (destination_path,))


def staging_sync():
    sync(STAGING_RSYNC_DESTINATION)


def prod_sync():
    sync(PROD_RSYNC_DESTINATION)


def linkchecker():
    with settings(warn_only=True):
        result = local("linkchecker"
                       " --config linkcheckerrc"
                       " " + STAGING_FQDN,
                       capture=True)
    if result.failed:
        if not confirm("Failures with linkchecker:\n%s\nContinue anyway?" %
                      ("\n".join(result.stdout.splitlines()[9:]))):
            abort("Aborting at user request.")
    else:
        # Summary is the second to last line
        print result.stdout.splitlines()[-2]


def repo_push():
    local("git push")


def deploy():
    nikola_build()
    requirements_dump()
    spellchecker()
    repo_status()
    staging_sync()
    linkchecker()
    orphans()
    if confirm("Push to live site?"):
        prod_sync()
        repo_push()
    else:
        print "Not pushing to live site."


def clean():
    with cd(SITE_BASE):
        local("rm -rf output cache")


def spellchecker():
    has_errors = False
    pwl_dictionary = enchant.request_pwl_dict(
        os.path.join(SITE_BASE, "spellcheck_exceptions.txt"))
    en_spellchecker = enchant.checker.SpellChecker(
        "en_GB",
        filters=[EmailFilter, URLFilter, RstURLFilter, RstEmailFilter])
    rst_posts = glob.glob(os.path.join(SITE_BASE, "posts", '*.rst'))
    rst_pages = glob.glob(os.path.join(SITE_BASE, "stories", "*.rst"))
    for rst_file in rst_posts + rst_pages:
        with open(rst_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            # Wrong place for this, but meh
            if len(line) > 2 and line[0] == "." and line[1] == ".":
                # rst directive
                continue

            en_spellchecker.set_text(line)
            for err in en_spellchecker:
                if not pwl_dictionary.check(err.word):
                    has_errors = True
                    print "%s (line %s): Not in dictionary:"\
                          "%s (suggestions: %s)" % \
                          (os.path.basename(rst_file),
                           lines.index(line) + 1,
                           err.word,
                           ", ".join(en_spellchecker.suggest(err.word)))

    if has_errors:
        if not confirm("Spell check errors. Continue?"):
            abort("Aborting at user request")


def orphans():
    SIZE_OF_URL_CRUFT = len("http:///")
    URL_FIELD = 7
    LINKCHECKER_OUTPUT = "linkchecker-output.csv"
    FILESYSTEM_FILES_TO_IGNORE = [
        'd3-projects/basic_au_map/basic_au_map.html',
        'd3-projects/census_nt_indig_lang/nt_sla_map.html',
        'd3-projects/census_nt_indig_lang/nt_sla_scatter.html',
        'd3-projects/index_time_series/index-line.html',
        'd3-projects/stacked-column-ex/stacked-column-ex.html',
        'galleries/index.html',
    ]

    html_files_on_filesystem = set()

    with settings(warn_only=True):
        local("linkchecker"
              " --config linkcheckerrc"
              " --verbose"
              " --file-output=csv/" + LINKCHECKER_OUTPUT + ""
              " --no-status"
              " --ignore-url '!(" + STAGING_FQDN + ")'"
              " http://" + STAGING_FQDN,
              capture=True)

    with open(LINKCHECKER_OUTPUT) as f:
        linkchecker_output = csv.reader(f, delimiter=";")
        html_files_checked = set(
            [row[URL_FIELD][SIZE_OF_URL_CRUFT + len(STAGING_FQDN):]
             for row in linkchecker_output
             if row[0][0] != "#" and  # comments start with a hash
             len(row) == 17 and  # legit check rows have 17 fields
             row[URL_FIELD][-5:] == ".html"]
        )

    os.remove(LINKCHECKER_OUTPUT)
    for dirname, file_list in \
        [(d, filter(lambda x: x[-5:] == ".html", f))
         for d, _, f in os.walk(SITE_BASE)]:
        if dirname.startswith(OUTPUT_DIR):
            for f in file_list:
                path_beneath_output = \
                    os.path.join(dirname[len(OUTPUT_DIR) + 1:], f)
                if path_beneath_output not in FILESYSTEM_FILES_TO_IGNORE:
                    html_files_on_filesystem.add(path_beneath_output)

    orphan_list = html_files_on_filesystem.difference(html_files_checked)
    for orphan in sorted(list(orphan_list)):
        print "Orphaned file: " + orphan

    if orphan_list:
        if not confirm("Orphaned html files exist"
                       " (are on disk but aren't linked). Continue?"):
            abort("Aborting at user request")


if __name__ == '__main__':
    orphans()
