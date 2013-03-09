from fabric.api import abort, local, settings
from fabric.contrib.console import confirm
from fabric.context_managers import cd, quiet
import glob
import os
import re
import enchant
import enchant.checker
from enchant.tokenize import EmailFilter, URLFilter, Filter


STAGING_RSYNC_DESTINATION = "/Users/esteele/Sites/staging.wordspeak.org"
PROD_RSYNC_DESTINATION = "wordspeak.org:/users/home/esteele/web/public"
DEV_NIKOLA = "/Users/esteele/Code/nikola-edwinsteele/nikola/scripts/nikola"
REL_NIKOLA = "/Users/esteele/.virtualenvs/wordspeak/bin/nikola"
SITE_BASE = "/Users/esteele/Code/wordspeak.org"


class RstURLFilter(Filter):
    """Filter skipping over URLs.
    This filter skips any words matching the following regular expression:

           ^<[a-zA-z]+:\/\/[^\s].*>`_

    That is, any words that are RST defined URLs.
    """
    _DOC_ERRORS = ["zA"]
    _pattern = re.compile(r"^<([a-zA-z]+:\/)?\/[^\s].*>`_")
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
                       " http://staging.wordspeak.org",
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
    rst_posts = glob.glob(os.path.join(SITE_BASE, "posts", "*.rst"))
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
                    print "%s (line %s): Not in dictionary: %s (suggestions: %s)" % \
                          (os.path.basename(rst_file),
                           lines.index(line) + 1,
                           err.word,
                           ", ".join(en_spellchecker.suggest(err.word)))

    if has_errors:
        if not confirm("Spell check errors. Continue?"):
            abort("Aborting at user request")


if __name__ == '__main__':
    spellchecker()
