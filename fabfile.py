import urllib
from fabric.api import abort, local, settings
from fabric.colors import green, red, yellow
from fabric.contrib.console import confirm
from fabric.context_managers import cd, hide, quiet, warn_only
from fabric.operations import prompt
import csv
from email.mime.text import MIMEText
import glob
import os
import re
import enchant
import enchant.checker
import enchant.tokenize
import smtplib
import socket
import sys
import tempfile
import requests
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
REL_NIKOLA = os.path.join(TILDE, ".virtualenvs/wordspeak_n7/bin/nikola")
SITE_BASE = os.path.join(TILDE, "Code/wordspeak.org")
OUTPUT_BASE = conf.OUTPUT_FOLDER
CACHE_BASE = conf.CACHE_FOLDER
SPELLCHECK_EXCEPTIONS = os.path.join(SITE_BASE, "spellcheck_exceptions.txt")
UNWANTED_BUILD_ARTIFACTS = []
# An update of these files will abort a fab deploy operation
KEY_FILES = ["conf.py", "fabfile.py"]
ORPHAN_WHITELIST = [
    'd3-projects/basic_au_map/basic_au_map.html',
    'd3-projects/census_nt_indig_lang/nt_sla_map.html',
    'd3-projects/census_nt_indig_lang/nt_sla_scatter.html',
    'd3-projects/index_time_series/index-line.html',
    'd3-projects/stacked-column-ex/stacked-column-ex.html',
    'pages/404.html',
]
W3C_HTML_VALIDATION_URL = 'http://validator.w3.org/check?uri=%s&' \
                          'charset=%%28detect+automatically%%29&' \
                          'doctype=Inline&group=0&output=%s'
W3C_HTML_VALIDATION_TARGETS = [
    'https://www.wordspeak.org/index.html',
    'https://www.wordspeak.org/pages/about.html',
    'https://www.wordspeak.org/posts/write-because-you-want-to.html',
]
W3C_CSS_VALIDATION_URL = 'http://jigsaw.w3.org/css-validator/validator?' \
                         'uri=%s&profile=css3&usermedium=all&warning=1&' \
                         'vextwarning=&lang=en&output=%s'
W3C_CSS_VALIDATION_TARGETS = [
    'https://www.wordspeak.org/assets/css/all-nocdn.css',
]
W3C_RSS_VALIDATION_URL = 'http://validator.w3.org/feed/check.cgi?url=%s'
W3C_RSS_VALIDATION_TARGETS = [
    'https://www.wordspeak.org/rss.xml',
]


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
    # If the dns_name resolves to 127.0.0.1, then whatever machine we're
    #  on definitely answers for the hostname
    return socket.gethostbyname(socket.gethostbyaddr(
        socket.gethostbyname(dns_name))[0]) in (my_main_ip, '127.0.0.1')


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
        if result.stderr:
            print "%s actions performed\n" % \
                  (len(result.stderr.splitlines()) - 1),
        else:
            print "No output from command."


def build():
    """Build the site using nikola"""
    with quiet():
        if local("test '$(showvirtualenv)' == 'nikola-dev'").succeeded:
            nikola = DEV_NIKOLA
        else:
            nikola = REL_NIKOLA

    with cd(SITE_BASE):
        _quietly_run_nikola_cmd(nikola, "build")
        _quietly_run_nikola_cmd(nikola, "mincss")
        # Need to recompress css after yuicompressor has run
        #  Can't run post_render_gzip in N7, so let's just do build again
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
        local("rsync "
              "--delete "
              "--delete-excluded "
              "--exclude-from rsync_exclusion_list.txt "
              "-a %s/ %s" % (OUTPUT_BASE, destination_path))


def staging_sync():
    """Sync the site to the staging server"""
    if _does_this_machine_answer_for_this_hostname(STAGING_FQDN):
        destination = STAGING_RSYNC_DESTINATION_LOCAL
    else:
        destination = STAGING_RSYNC_DESTINATION_REMOTE

    _sync_site(destination)
    local("rsync --delete -a %s/staging_robots.txt %s/robots.txt" %
          (SITE_BASE, destination))


def prod_sync():
    """Sync the site to the prod server"""
    with cd(SITE_BASE):
        local("rsync --delete -a %s/prod_robots.txt %s/robots.txt" %
              (SITE_BASE, OUTPUT_BASE))
    if _does_this_machine_answer_for_this_hostname(PROD_FQDN):
        _sync_site(PROD_RSYNC_DESTINATION_LOCAL)
    else:
        _sync_site(PROD_RSYNC_DESTINATION_REMOTE)


def linkchecker(output_fd=sys.stdout):
    """Checks for broken links on the staging site

    Returns whether the task ran successfully i.e. found no problems
    """
    with settings(hide('warnings'), warn_only=True):
        result = local("linkchecker"
                       " --check-extern"
                       " --config linkcheckerrc"
                       " http://" + STAGING_FQDN,
                       capture=True)
    # Summary is the second to last line
    summary_line = "Summary: %s" % (result.stdout.splitlines()[-2],)
    if result.failed:
        print yellow(summary_line)
        # Failures are listed from the tenth line
        output_fd.write("Failures with linkchecker:\n%s\n" %
                       ("\n".join(result.stdout.splitlines()[9:])))
        return False
    else:
        print green(summary_line)
        output_fd.write(result.stdout.splitlines()[-2])
        return True


def check_mixed_content(output_fd=sys.stdout):
    """looks for mixed http/https content"""
    with quiet():
        if local("test '$(showvirtualenv)' == 'nikola-dev'").succeeded:
            nikola = DEV_NIKOLA
        else:
            nikola = REL_NIKOLA

    result = local("%s check -l" % (nikola,))
    if result.failed:
        output_fd.write("Failures with mixed content check: %s" %
                        (result.stdout,))
        return False
    else:
        output_fd.write("No problems with mixed HTTP/HTTPS content")
        return True


def repo_push():
    """Push the wordspeak repo to github if there's anything to push"""
    with quiet():
        head_result = local(
            "git --no-pager log -1 --oneline HEAD", capture=True)
        orig_head_result = local(
            "git --no-pager log -1 --oneline origin/master", capture=True)
    # As we did a pull at the start of the deployment process, we can
    #  be sure that the ORIG_HEAD reflects the upstream repo.
    # If head_result and orig_head_result are the same, we don't need
    #  to do a push (and can thus save being prompted for the password
    #  on any keys that aren't already known
    if head_result.stdout != orig_head_result.stdout:
        local("git push")
    else:
        print "No git push necessary (no local commits need pushing)"


def repo_pull():
    """Get changes from git in this repo.
     Deliberately uses https to avoid needing keys"""
    result = local(
        "git pull https://github.com/edwinsteele/wordspeak.org.git master",
        capture=True)
    print result.stderr
    print result.stdout
    # Something like:
    #
    # Updating 815b459..d9a508d
    # Fast-forward
    # fabfile.py       | 2 +-
    # requirements.txt | 1 -
    # 2 files changed, 1 insertion(+), 2 deletions(-)

    # return something that evaluates to true if we updated one of the key files
    return [k for k in KEY_FILES if k in result.stdout]


def clean():
    """Remove files generated by Nikola"""
    with cd(SITE_BASE):
        local("rm -rf %s %s" % (OUTPUT_BASE, CACHE_BASE))


def _non_directive_lines(lines):
    """filters out all the rst/markdown directives

    so the spell checker doesn't get confused"""
    blank_lines_til_spellcheck_starts = 0
    in_code_directive = False
    for line in lines:
        if line.startswith("```"):
            if in_code_directive:
                in_code_directive = False
            else:
                in_code_directive = True

        if in_code_directive:
            continue
                
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


def strip_markdown_directives(line):
    line = line.strip()
    if line.startswith("<") and line.endswith(">"):
        # Let's assume it's inline HTML and skip it
        return ""

    # Remove URL
    line = re.sub(r'\[(.+?)]\(http[^\)]+\)', r'\1', line)
    line = re.sub(r'<http:.+?>', r'', line)
    return line


def spellchecker():
    """Spellcheck the Markdown and ReST files on the site"""

    replacements_performed = False

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
            en_spellchecker.set_text(strip_markdown_directives(line))
            for err in en_spellchecker:
                if not pwl_dictionary.check(err.word):
                    replacements_performed = True
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

    return replacements_performed


def orphans(output_fd=sys.stdout):
    """Find html files that exist on the filesystem but aren't accessible
    via hyperlinks

    Returns whether the task ran successfully i.e. found no problems
    """
    SIZE_OF_URL_CRUFT = len("http:///")
    URL_FIELD = 7
    LINKCHECKER_OUTPUT = "linkchecker-output.csv"
    html_files_on_filesystem = set()

    with warn_only():
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
            if path_beneath_output not in ORPHAN_WHITELIST:
                html_files_on_filesystem.add(path_beneath_output)

    orphan_list = html_files_on_filesystem.difference(html_files_checked)
    if orphan_list:
        print yellow("Orphans found (%s)." % (len(orphan_list),))
        output_fd.write("Orphaned html files exist "
                        "(are on disk but aren't linked).\n")
        for orphan in sorted(list(orphan_list)):
            output_fd.write("Orphaned file: " + orphan + "\n")
        return False
    else:
        print green("No orphans found.")
        return True


def w3c_checks(output_fd=sys.stdout):
    for url in W3C_HTML_VALIDATION_TARGETS:
        r = requests.get(W3C_HTML_VALIDATION_URL % (urllib.quote_plus(url),
                                                    "json"))
        if r.json()["messages"]:
            print "messages is ->%s<-" % (r.json()["messages"],)
            output_fd.write("HTML has W3C validation errors (%s):\n" % (url,))
            for message in r.json()["messages"]:
                output_fd.write("- %s" % (message,))
            output_fd.write("\n")
            output_fd.write("Full details: %s\n" % (W3C_HTML_VALIDATION_URL %
                                                    (urllib.quote_plus(url),
                                                     "html")))
        else:
            output_fd.write("HTML validates (%s)\n" % (url,))
    output_fd.write("\n")
    for url in W3C_CSS_VALIDATION_TARGETS:
        r = requests.get(W3C_CSS_VALIDATION_URL % (urllib.quote_plus(url),
                                                   "text"))
        summary = [l.strip() for l in r.text.split('\n') if l.strip()][1]
        if "Congratulations" in summary:
            output_fd.write("CSS validates (%s)\n" % (url,))
        else:
            output_fd.write("CSS validation failures for %s\n" % (url,))
            output_fd.write("%s\n" % (summary,))
            output_fd.write("Full details: %s\n" % (W3C_CSS_VALIDATION_URL %
                                                    (urllib.quote_plus(url),
                                                     "html")))
    output_fd.write("\n")
    for url in W3C_RSS_VALIDATION_TARGETS:
        r = requests.get(W3C_RSS_VALIDATION_URL % (urllib.quote_plus(url),))
        # UGLY, and fragile but there's no machine readable output available
        if "This is a valid RSS feed" in r.text:
            output_fd.write("RSS validates (%s)\n" % (url,))
        else:
            output_fd.write("RSS validation failures for %s\n")
            output_fd.write("Full details: %s\n" % (W3C_RSS_VALIDATION_URL %
                                                    (urllib.quote_plus(url))))
    output_fd.write("\n")


def post_build_cleanup():
    """Get rid of the stuff that we don't want to push but was built
    (and can't easily be disabled"""
    with cd(OUTPUT_BASE):
        for f in UNWANTED_BUILD_ARTIFACTS:
            local("rm -f %s" % (f,))


def check_required_modules():
    """Make sure we have all the python modules needed for the build"""
    try:
        import webassets  # for bundle creation
        import squeeze  # for yuicompressor
    except ImportError as e:
        # noinspection PyUnusedLocal
        webassets = squeeze = None
        abort(red("Missing module: %s" % (e,)))


def post_deploy():
    """Runs time consuming tasks, or those that don't need to be run inline"""
    scratch = tempfile.TemporaryFile()
    scratch.write("Linkchecker\n")
    scratch.write("-----------\n")
    ran_successfully = linkchecker(scratch)
    scratch.write("\nOrphans\n")
    scratch.write("-----------\n")
    ran_successfully = orphans(scratch) and ran_successfully
    scratch.write("\nHTTP/HTTPS Mixed Content\n")
    scratch.write("-----------\n")
    ran_successfully = check_mixed_content(scratch) and ran_successfully
    scratch.write("\nW3C Validations\n")
    scratch.write("-----------\n")
    ran_successfully = w3c_checks(scratch) and ran_successfully
    scratch.write("--- Post deploy checks complete ---\n")

    # Re-read the file and mail it
    scratch.seek(os.SEEK_SET)
    text = scratch.read()
    subject = "[Wordspeak] Deployment complete "
    if ran_successfully:
        subject += "(no errors) "
    else:
        subject += "(with errors) "
    subject += "from %s" % (socket.gethostname().split(".")[0],)

    msg = MIMEText(text)
    msg["Subject"] = subject
    msg["To"] = "edwin@wordspeak.org"
    msg["From"] = "Wordspeak Deploys <edwin@wordspeak.org>"
    print "Sending summary mail... ",
    try:
        mail_server = smtplib.SMTP('localhost')
        mail_server.sendmail("edwin@wordspeak.org",
                             ["edwin@wordspeak.org"],
                             msg.as_string())
        mail_server.quit()
    except smtplib.SMTPException, e:
        print red("Failed.\n%s", (e,))
    else:
        print green("Success.")


def deploy():
    """Runs all the pre-deployment checks, pushing to staging and then prod"""
    spellcheck_needed = True
    key_files_changed = repo_pull()
    if key_files_changed:
        abort(red("Aborting as the following key files changed: %s" %
              (",".join(key_files_changed),)))
    maybe_add_untracked_files()
    check_required_modules()
    while spellcheck_needed:
        spellcheck_needed = spellchecker()
    build()
    post_build_cleanup()
    requirements_dump()
    repo_status()
    staging_sync()
    if confirm("Push to live site?"):
        prod_sync()
        repo_push()
    else:
        print red("Not pushing to live site.")

    post_deploy()


if __name__ == '__main__':
    spellchecker()
