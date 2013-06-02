from fabric.api import abort, local, settings
from fabric.contrib.console import confirm
from fabric.context_managers import cd, quiet
import csv
import glob
import os
import re
import enchant
import enchant.checker
import enchant.tokenize
import conf

TILDE = os.path.expanduser("~")
STAGING_FQDN = "staging.wordspeak.org"
STAGING_RSYNC_DESTINATION = os.path.join(TILDE, "Sites/staging.wordspeak.org")
PROD_RSYNC_DESTINATION = "wordspeak.org:/users/home/esteele/web/public"
DEV_NIKOLA = os.path.join(TILDE,
                          "Code/nikola-edwinsteele/nikola/scripts/nikola")
REL_NIKOLA = os.path.join(TILDE, ".virtualenvs/wordspeak/bin/nikola")
SITE_BASE = os.path.join(TILDE, "Code/wordspeak.org")
OUTPUT_BASE = conf.OUTPUT_FOLDER
CACHE_BASE = conf.CACHE_FOLDER


class _RstURLFilter(enchant.tokenize.Filter):
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


class _RstEmailFilter(enchant.tokenize.Filter):
    """Filter skipping over restructure text directives
    """
    _DOC_ERRORS = ["zA"]
    _pattern = re.compile(r"^<mailto:.+@[^\.].*\.[a-z]{2,}>`_$")

    def _skip(self, word):
        if self._pattern.match(word):
            return True
        return False


def _quietly_run_nikola_cmd(nikola, cmd):
    result = local("%s %s" % (nikola, cmd), capture=True)
    if "TaskFailed" in result.stdout or \
            "WARNING" in result.stderr:
        print "Stdout:"
        print result.stdout
        print "Stderr:"
        print result.stderr
        abort("Nikola command '%s' failed." % (cmd,))
    else:
        print "%s actions performed\n" % \
              (len(result.stdout.splitlines()) - 1),


def nikola_build():
    """Build the site using nikola"""
    with quiet():
        if local("test '$(showvirtualenv)' == 'nikola-dev'").succeeded:
            nikola = DEV_NIKOLA
        else:
            nikola = REL_NIKOLA

    with cd(SITE_BASE):
        # local_search should run before build bundles, but isn't in 5.4.4
        _quietly_run_nikola_cmd(nikola, "render_pages")
        _quietly_run_nikola_cmd(nikola, "local_search")
        _quietly_run_nikola_cmd(nikola, "build_bundles")
        _quietly_run_nikola_cmd(nikola, "build")


def requirements_dump():
    """pip freeze the package requirements"""
    with cd(SITE_BASE):
        # pyinotify and MacFSEvents only build on their particular platform
        #  so exclude them. They'll get pulled in when a pip install doit
        #  is done so there's no loss.
        local("pip freeze | egrep -v '(pyinotify|MacFSEvents)'"
              "> requirements.txt")


def maybe_add_untracked_files():
    """Look for untracked files in the repo and give option to add"""
    with cd(SITE_BASE):
        result = local("git status --porcelain", capture=True)

    for line in result.stdout.splitlines():
        if line[0:2] == "??" and \
                confirm("Add untracked file '%s'?" % (line[3:],)):
            with cd(SITE_BASE):
                local("git add '%s'" % (line[3:],))


def repo_status():
    """Check whether there are any uncommitted/untracked files in the repo"""
    result = local("git status --porcelain", capture=True)
    if result.stdout:
        print result.stdout
        if not confirm("Repo has uncommitted/untracked files. Continue?"):
            abort("Aborting at user request.")


def _sync(destination_path):
    with cd(SITE_BASE):
        local("rsync --delete-after -a %s/ %s" %
              (OUTPUT_BASE, destination_path))
        local("rsync --delete-after -a %s/.htaccess %s" %
              (OUTPUT_BASE, destination_path))


def staging_sync():
    """Sync the site to the staging server"""
    _sync(STAGING_RSYNC_DESTINATION)


def prod_sync():
    """Sync the site to the prod server"""
    _sync(PROD_RSYNC_DESTINATION)


def linkchecker():
    """Checks for broken links on the staging site"""
    with settings(warn_only=True):
        result = local("linkchecker"
                       " --config linkcheckerrc"
                       " http://" + STAGING_FQDN,
                       capture=True)
    if result.failed:
        if not confirm("Failures with linkchecker:\n%s\nContinue anyway?" %
                      ("\n".join(result.stdout.splitlines()[9:]))):
            abort("Aborting at user request.")
    else:
        # Summary is the second to last line
        print result.stdout.splitlines()[-2]


def repo_push():
    """Push the wordspeak repo to github"""
    local("git push")


def deploy():
    """Runs all the pre-deployment checks, pushing to staging and then prod"""
    maybe_add_untracked_files()
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
    """Remove files generated by Nikola"""
    with cd(SITE_BASE):
        local("rm -rf %s %s" % (OUTPUT_BASE, CACHE_BASE))


def spellchecker():
    """Spellcheck the ReST files on the site"""

    has_errors = False
    # aspell is available on mac by default, and I don't want to manage custom
    #  word lists for both aspell and myspell so we'll just use one
    enchant._broker.set_ordering("en_GB", "aspell")
    pwl_dictionary = enchant.request_pwl_dict(
        os.path.join(SITE_BASE, "spellcheck_exceptions.txt"))
    en_spellchecker = enchant.checker.SpellChecker(
        "en_GB",
        filters=[enchant.tokenize.EmailFilter,
                 enchant.tokenize.URLFilter,
                 _RstURLFilter,
                 _RstEmailFilter]
    )
    rst_posts = glob.glob(os.path.join(SITE_BASE, "posts", "*.rst"))
    rst_pages = glob.glob(os.path.join(SITE_BASE, "stories", "*.rst"))
    blank_lines_til_spellcheck_starts = 0

    for rst_file in rst_posts + rst_pages:
        with open(rst_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            # Wrong place for this, but meh
            if blank_lines_til_spellcheck_starts > 0:
                if len(line.strip()) == 0:
                    # rst directive ends with blank line
                    blank_lines_til_spellcheck_starts -= 1

                continue

            if line.startswith("..") and not line.startswith(".. title:"):
                # rst directive starts with ^.. and is terminated with one
                #  blank line
                # except code-block which has a blank line after the directive
                #  and is terminated with one blank line
                # we want to spellcheck the title directive
                if line.startswith(".. code-block"):
                    blank_lines_til_spellcheck_starts = 2
                else:
                    blank_lines_til_spellcheck_starts = 1
                continue

            if line.startswith("::"):
                # block directive starts with ^::
                # it's immediately followed by a blank line and is terminated
                #  by another blank line
                blank_lines_til_spellcheck_starts = 2
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
    """Find html files that exist on the filesystem but aren't accessible
    via hyperlinks
    """
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
        'pages/404.html',
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
            for d, _, f in os.walk(STAGING_RSYNC_DESTINATION)]:
        for f in file_list:
            path_beneath_output = \
                os.path.join(dirname[len(STAGING_RSYNC_DESTINATION) + 1:], f)
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
    spellchecker()
