from fabric.api import abort, local, settings
from fabric.contrib.console import confirm
from fabric.context_managers import cd, quiet
from fabric.operations import prompt
import csv
import glob
import os
import re
import enchant
import enchant.checker
import enchant.tokenize
import socket
import conf

TILDE = os.path.expanduser("~")
STAGING_FQDN = "staging.wordspeak.org"
STAGING_FILESYSTEM_ROOT = "Sites/staging.wordspeak.org"
STAGING_RSYNC_DESTINATION_LOCAL = os.path.join(TILDE, STAGING_FILESYSTEM_ROOT)
STAGING_RSYNC_DESTINATION_REMOTE = "%s:/home/esteele/%s" % \
                                   (STAGING_FQDN, STAGING_FILESYSTEM_ROOT)
PROD_FQDN = "www.wordspeak.org"
PROD_FILESYSTEM_ROOT = "Sites/www.wordspeak.org"
PROD_RSYNC_DESTINATION_LOCAL = os.path.join(TILDE, PROD_FILESYSTEM_ROOT)
PROD_RSYNC_DESTINATION_REMOTE = "%s:/home/esteele/%s" % \
                                (PROD_FQDN, PROD_FILESYSTEM_ROOT)
DEV_NIKOLA = os.path.join(TILDE,
                          "Code/nikola-edwinsteele/nikola/scripts/nikola")
REL_NIKOLA = os.path.join(TILDE, ".virtualenvs/wordspeak/bin/nikola")
SITE_BASE = os.path.join(TILDE, "Code/wordspeak.org")
OUTPUT_BASE = conf.OUTPUT_FOLDER
CACHE_BASE = conf.CACHE_FOLDER
SPELLCHECK_EXCEPTIONS = os.path.join(SITE_BASE, "spellcheck_exceptions.txt")
UNWANTED_BUILD_ARTIFACTS = [os.path.join(OUTPUT_BASE, "tipue_search.html"),
                            os.path.join(OUTPUT_BASE, "tipue_search.html.gz")]


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


def _does_this_machine_answer_for_this_hostname(dns_name):
    """Looks at DNS and local interfaces to see if this host answers for the
     DNS name in question

    Caveats:
    - Won't work reliably if the DNS entry resolves to more than one address
    - Assumes the interface configured with the IP associated with the host's
      hostname is actually the interface that accepts public traffic
      associated with DNS name in question
    """
    try:
        my_main_ip = socket.gethostbyname(socket.getfqdn())
    except socket.gaierror:
        # Can't resolve hostname to a public IP, so we're probably going to
        #  be referring to ourselves by localhost, so let's allocate an
        #  IP address accordingly.
        my_main_ip = "127.0.0.1"

    # do a round-trip to so that we match when the host is behind a load
    #  balancer and doesn't have a public IP address (assumes split-horizon
    #  DNS is configured to resolve names to internal addresses) e.g. AWS
    return my_main_ip == socket.gethostbyname(
        socket.gethostbyaddr(socket.gethostbyname(dns_name))[0])


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


def build():
    """Build the site using nikola"""
    with quiet():
        if local("test '$(showvirtualenv)' == 'nikola-dev'").succeeded:
            nikola = DEV_NIKOLA
        else:
            nikola = REL_NIKOLA

    with cd(SITE_BASE):
        # local_search should run before build bundles, but isn't in 5.4.4
        _quietly_run_nikola_cmd(nikola, "local_search")
        _quietly_run_nikola_cmd(nikola, "build")
        _quietly_run_nikola_cmd(nikola, "mincss")


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
    with cd(SITE_BASE):
        result = local("git status --porcelain", capture=True)
    if result.stdout:
        print result.stdout
        response = prompt("Repo has uncommitted/untracked files. "
                          "'abort' to abort or type a commit message",
                          default="abort").strip()

        if response == "abort":
            abort("Aborting at user request.")
        else:
            with cd(SITE_BASE):
                local("git commit -a -m'%s'" % (response,))


def _sync_site(destination_path):
    with cd(SITE_BASE):
        local("rsync --delete-after -a %s/ %s" %
              (OUTPUT_BASE, destination_path))


def staging_sync():
    """Sync the site to the staging server"""
    if _does_this_machine_answer_for_this_hostname(STAGING_FQDN):
        destination = STAGING_RSYNC_DESTINATION_LOCAL
    else:
        destination = STAGING_RSYNC_DESTINATION_REMOTE

    _sync_site(destination)
    local("rsync --delete-after -a %s/staging_robots.txt %s/robots.txt" % (SITE_BASE, destination))


def prod_sync():
    """Sync the site to the prod server"""
    with cd(SITE_BASE):
        local("rsync --delete-after -a %s/prod_robots.txt %s/robots.txt" % (SITE_BASE, OUTPUT_BASE))
    if _does_this_machine_answer_for_this_hostname(PROD_FQDN):
        _sync_site(PROD_RSYNC_DESTINATION_LOCAL)
    else:
        _sync_site(PROD_RSYNC_DESTINATION_REMOTE)


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


def repo_pull():
    """Get changes from git in this repo.
     Deliberately uses https to avoid needing keys"""
    local("git pull https://github.com/edwinsteele/wordspeak.org.git master")


def clean():
    """Remove files generated by Nikola"""
    with cd(SITE_BASE):
        local("rm -rf %s %s" % (OUTPUT_BASE, CACHE_BASE))


def _non_directive_lines(lines):
    """filters out all the rst directives

    so the spell checker doesn't get confused"""
    blank_lines_til_spellcheck_starts = 0
    for line in lines:
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

        yield line


def _add_to_spellcheck_exceptions(word):
    with open(SPELLCHECK_EXCEPTIONS, "r+") as exceptions_file:
        exceptions_file_contents = exceptions_file.read()	
        # Make sure we're writing the exception on a new line, and that the file
        #  isn't empty
        if exceptions_file_contents and exceptions_file_contents[-1] != "\n":
            exceptions_file.write("\n")
        exceptions_file.write(word + "\n")
    print "Added '%s' to spell check exception list" % (word,)


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
    print "Replaced %s with %s in %s" % (old_word, new_word, input_file)


def spellchecker():
    """Spellcheck the Markdown and ReST files on the site"""

    # aspell is available on mac by default, and I don't want to manage custom
    #  word lists for both aspell and myspell so we'll just use aspell
    enchant._broker.set_ordering("en_GB", "aspell")
    pwl_dictionary = enchant.request_pwl_dict(SPELLCHECK_EXCEPTIONS)
    en_spellchecker = enchant.checker.SpellChecker(
        "en_GB",
        filters=[enchant.tokenize.EmailFilter,
                 enchant.tokenize.URLFilter,
                 _RstURLFilter,
                 _RstEmailFilter]
    )
    rst_posts = glob.glob(os.path.join(SITE_BASE, "posts", "*.rst"))
    md_posts = glob.glob(os.path.join(SITE_BASE, "posts", "*.md"))
    rst_pages = glob.glob(os.path.join(SITE_BASE, "stories", "*.rst"))

    for files_to_check in rst_posts + rst_pages + md_posts:
        with open(files_to_check, 'r') as f:
            lines = f.readlines()

        for line in _non_directive_lines(lines):
            en_spellchecker.set_text(line)
            for err in en_spellchecker:
                if not pwl_dictionary.check(err.word):
                    print "Not in dictionary: %s (file: %s line: %s)" % \
                          (err.word,
                           os.path.basename(files_to_check),
                           lines.index(line) + 1)
                    print "  Suggestions: " + \
                        ", ".join(en_spellchecker.suggest(err.word))
                    action = prompt("Add '%s' to dictionary [add] or "
                                    "replace [type replacement]?" % (err.word,),
                                    default="add").strip()
                    if action == "add":
                        _add_to_spellcheck_exceptions(err.word)
                    else:
                        _replace_in_file(files_to_check, err.word, action)


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
            for d, _, f in os.walk(STAGING_RSYNC_DESTINATION_LOCAL)]:
        for f in file_list:
            path_beneath_output = os.path.join(
                dirname[len(STAGING_RSYNC_DESTINATION_LOCAL) + 1:], f)
            if path_beneath_output not in FILESYSTEM_FILES_TO_IGNORE:
                html_files_on_filesystem.add(path_beneath_output)

    orphan_list = html_files_on_filesystem.difference(html_files_checked)
    for orphan in sorted(list(orphan_list)):
        print "Orphaned file: " + orphan

    if orphan_list:
        if not confirm("Orphaned html files exist"
                       " (are on disk but aren't linked). Continue?"):
            abort("Aborting at user request")


def post_build_cleanup():
    """Get rid of the stuff that we don't want to push but was built
    (and can't easily be disabled"""
    with cd(OUTPUT_BASE):
        for f in UNWANTED_BUILD_ARTIFACTS:
            local("rm -f %s" % (f,))


def check_required_modules():
    """Make sure we have all the python modules needed for the build"""
    try:
        # noinspection PyUnresolvedReferences
        import webassets
    except ImportError as e:
        abort("Missing module: %s" % (e,))


def deploy():
    """Runs all the pre-deployment checks, pushing to staging and then prod"""
    repo_pull()
    maybe_add_untracked_files()
    check_required_modules()
    spellchecker()
    build()
    post_build_cleanup()
    requirements_dump()
    repo_status()
    staging_sync()
    linkchecker()
    orphans()
    if confirm("Push to live site?"):
        prod_sync()
        repo_push()
    else:
        print "Not pushing to live site."


if __name__ == '__main__':
    spellchecker()
