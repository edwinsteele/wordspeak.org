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
import shutil
import smtplib
import socket
import sys
import tempfile
import requests
import conf
from pushover import Client

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
UNWANTED_BUILD_ARTIFACTS = [
    'd3-projects/basic_au_map/basic_au_map.html',
    'd3-projects/census_nt_indig_lang/nt_sla_map.html',
    'd3-projects/census_nt_indig_lang/nt_sla_scatter.html',
    'd3-projects/index_time_series/index-line.html',
    'd3-projects/stacked-column-ex/stacked-column-ex.html',
]
# An update of these files will abort a fab deploy operation
KEY_FILES = ["conf.py", "fabfile.py"]
W3C_HTML_VALIDATION_URL = 'https://validator.w3.org/nu/?doc=%s&' \
                          'useragent=Validator.nu%2FLV+http%3A%2F%2Fvalidator.w3.org%2Fservices'
W3C_HTML_VALIDATION_TARGETS = [
    'https://www.wordspeak.org/index.html',
    'https://www.wordspeak.org/pages/about.html',
    'https://www.wordspeak.org/posts/write-because-you-want-to.html',
    'https://www.wordspeak.org/posts/nsw-fires.html',
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
        # Need to recopy the leaflet.css file as mincss optimises it away
        #  because it can't find any leaflet classes in use (they're inserted
        #  at runtime by the js library
        local("cp %s/files/assets/leaflet-0.7.3/leaflet.css %s/assets/leaflet-0.7.3/leaflet.css" % (SITE_BASE, OUTPUT_BASE))
        # Need to recompress css after yuicompressor has run
        #  Can't run post_render_gzip in N7, so let's just do build again
        _quietly_run_nikola_cmd(nikola, "build")

    post_build_cleanup()


def requirements_dump():
    """pip freeze the package requirements"""
    with cd(SITE_BASE):
        # pyinotify and MacFSEvents only build on their particular platform
        #  so exclude them. They'll get pulled in when a pip install doit
        #  is done so there's no loss.
        # bsddb3 is only necessary on MacOS and is a pain to build, so we
        #  don't list it as a global dependency.
        # To build on MacOS, read http://marc-abramowitz.com/archives/2007/11/28/hacking-os-xs-python-dbhash-and-bsddb-modules-to-work/ 
        # make sure berkeley-db has been installed with brew, download the
        # module from pip, unpack and then from that directory run:
        # python setup.py --berkeley-db=/usr/local/Cellar/berkeley-db/5.3.28 install
        local("pip freeze | egrep -v '(pyinotify|MacFSEvents|bsddb3)'"
              "> requirements.txt")


def maybe_add_untracked_files(is_interactive_deploy):
    """Look for untracked files in the repo and give option to add"""
    with cd(SITE_BASE):
        result = local("git status --porcelain", capture=True)

    for line in result.stdout.splitlines():
        if line[0:2] == "??":
            if is_interactive_deploy:
                if not confirm("Add untracked file '%s'?" % (line[3:],)):
                    continue
            else:
                print "Adding untracked file '%s' during non-interactive" \
                      " deploy" % (line[3:],)

            with cd(SITE_BASE):
                local("git add '%s'" % (line[3:],))


def repo_status(is_interactive_deploy):
    """Check whether there are any uncommitted/untracked files in the repo"""
    with cd(SITE_BASE):
        result = local("git status --porcelain", capture=True)
    if result.stdout:
        print result.stdout
        if is_interactive_deploy:
            response = prompt("Repo has uncommitted/untracked files. "
                              "'abort' to abort or type a commit message",
                              default="abort").strip()
            if response == "abort":
                abort("Aborting at user request.")
        else:
            response = "Auto-commit during non-interactive deploy"

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

    Ignores posts because the links all appear in the index pages
    Returns whether the task ran successfully i.e. found no problems
    """
    with settings(hide('warnings'), warn_only=True):
        result = local("linkchecker"
                       " --check-extern"
                       " --ignore-url .*posts.*"
                       " --config linkcheckerrc"
                       " http://" + STAGING_FQDN,
                       capture=True)
    # Summary is the second to last line
    summary_line = result.stdout.splitlines()[-2].replace(
        "That's it.", "Linkchecker summary:")
    if result.failed:
        print yellow(summary_line)
        # Failures are listed from the tenth line
        output_fd.write("Failures with linkchecker:\n%s\n" %
                       ("\n".join(result.stdout.splitlines()[9:])))
        return False
    else:
        print green(summary_line)
        output_fd.write(summary_line)
        output_fd.write("\n")
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
        output_fd.write("Failures with mixed content check: %s\n" %
                        (result.stdout,))
        return False
    else:
        output_fd.write("No problems with mixed HTTP/HTTPS content\n")
        return True


def repo_push():
    """Push the wordspeak repo to github"""
    local("git push")


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


def _get_spellcheck_exceptions(lines):
    for line in lines:
        if line.startswith(".. spellcheck_exceptions:"):
            # Use filter(None so that we don't crash if there aren't any
            #  words specified, even though the tag is there
            return filter(None, [s.strip() for s in line.split(":")[1].strip().split(",")])
    return []


def _is_tagged_as_orphan(filename):
    """takes an html filename and checks whether the markdown identifies the
    page as an orphan. Assumes slug and filename (sans suffix) are the same"""
    md_file = ".".join([filename.rsplit(".")[0], "md"])
    # Source for pages lives in stories
    md_file = md_file.replace("pages/", "stories/")
    # Check if there's a markdown equivalent, given the transpositions
    #  that we're aware of
    if os.path.exists(md_file):
        with open(md_file, "r") as w:
            for line in w:
                if line.startswith(".. is_orphan:"):
                    return line.split(":")[1].strip().lower() == "true"

    # Nasty hack because post_build_cleanup doesn't seem to remove d3 stuff
    # Change this to "return False" once that's cleaned up, or d3 stuff has
    #  been removed from the tree
    return filename in UNWANTED_BUILD_ARTIFACTS


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
        filters=[enchant.tokenize.EmailFilter,
                 enchant.tokenize.URLFilter,
                 _RstURLFilter,
                 _RstEmailFilter]
    )
    md_posts = glob.glob(os.path.join(SITE_BASE, "posts", "*.md"))
    md_pages = glob.glob(os.path.join(SITE_BASE, "stories", "*.md"))

    for files_to_check in md_pages + md_posts:
        with open(files_to_check, 'r') as f:
            lines = f.readlines()

        e = _get_spellcheck_exceptions(lines)
        map(pwl_dictionary.add_to_session, e)
        for line in _non_directive_lines(lines):
            en_spellchecker.set_text(strip_markdown_directives(line))
            for err in en_spellchecker:
                if not pwl_dictionary.check(err.word):
                    spelling_errors_found = True
                    print "Not in dictionary: %s (file: %s line: %s)" % \
                          (err.word,
                           os.path.basename(files_to_check),
                           lines.index(line) + 1)
                    print "  Suggestions: " + \
                        ", ".join(en_spellchecker.suggest(err.word))
                    if is_interactive_deploy:
                        action = prompt("Add '%s' to dictionary [add] or "
                                        "replace [type replacement]?"
                                        % (err.word,), default="add").strip()
                        if action == "add":
                            _add_to_spellcheck_exceptions(err.word)
                        else:
                            _replace_in_file(files_to_check, err.word, action)
                    else:
                        print "Not doing spellcheck substitutions during" \
                              " non-interactive deploy"

    return spelling_errors_found


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
            if not _is_tagged_as_orphan(path_beneath_output):
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
        output_fd.write("No orphans found.\n")
        return True


def w3c_checks(output_fd=sys.stdout):
    all_checks_pass = True
    for url in W3C_HTML_VALIDATION_TARGETS:
        r = requests.get(W3C_HTML_VALIDATION_URL % (urllib.quote_plus(url),
                                                    "json"))
        if r.json()["messages"]:
            output_fd.write("HTML has W3C validation errors (%s):\n" % (url,))
            for message in r.json()["messages"]:
                output_fd.write("- %s" % (message,))
            output_fd.write("\n")
            output_fd.write("Full details: %s\n" % (W3C_HTML_VALIDATION_URL %
                                                    (urllib.quote_plus(url),
                                                     "html")))
            all_checks_pass = False
        else:
            output_fd.write("HTML validates (%s)\n" % (url,))

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
            all_checks_pass = False
    for url in W3C_RSS_VALIDATION_TARGETS:
        r = requests.get(W3C_RSS_VALIDATION_URL % (urllib.quote_plus(url),))
        # UGLY, and fragile but there's no machine readable output available
        if "This is a valid RSS feed" in r.text:
            output_fd.write("RSS validates (%s)\n" % (url,))
        else:
            output_fd.write("RSS validation failures for %s\n")
            output_fd.write("Full details: %s\n" % (W3C_RSS_VALIDATION_URL %
                                                    (urllib.quote_plus(url))))
            all_checks_pass = False

    return all_checks_pass


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
    try:
        import webassets  # for bundle creation
        import rcssmin # for css minifaction
    except ImportError as e:
        # noinspection PyUnusedLocal
        webassets = rcssmin = None
        abort(red("Missing module: %s" % (e,)))
    get_env_variable("WORDSPEAK_PUSHOVER_USER")
    get_env_variable("WORDSPEAK_PUSHOVER_API_TOKEN")


def _send_pushover_summary(message, title):
    client = Client(get_env_variable("WORDSPEAK_PUSHOVER_USER"),
                    api_token=get_env_variable("WORDSPEAK_PUSHOVER_API_TOKEN"))
    return client.send_message(message, title=title)


def post_deploy():
    """Runs time consuming tasks, or those that don't need to be run inline"""
    _initialise()
    scratch = tempfile.TemporaryFile()
    ran_successfully = linkchecker(scratch)
    ran_successfully = orphans(scratch) and ran_successfully
    ran_successfully = check_mixed_content(scratch) and ran_successfully
    ran_successfully = w3c_checks(scratch) and ran_successfully

    # Re-read the file and mail it
    scratch.seek(os.SEEK_SET)
    text = scratch.read()
    subject = "Wordspeak deployment complete "
    if ran_successfully:
        subject += "(no errors) "
    else:
        subject += "(with errors) "
    subject += "from %s" % (socket.gethostname().split(".")[0],)

    _send_pushover_summary(text[:1000], subject)
    if not ran_successfully:
        # Also send an email
        msg = MIMEText(text)
        msg["Subject"] = subject
        msg["To"] = conf.BLOG_EMAIL
        msg["From"] = "%s Deployment <%s>" % (conf.BLOG_TITLE, conf.BLOG_EMAIL,)
        print "Sending summary mail... ",
        try:
            mail_server = smtplib.SMTP('localhost')
            mail_server.sendmail(conf.BLOG_EMAIL, [conf.BLOG_EMAIL],
                                 msg.as_string())
            mail_server.quit()
        except smtplib.SMTPException, e:
            print red("Failed.\n%s", (e,))
        else:
            print green("Success.")


def deploy(is_interactive_deploy=True):
    """Runs all the pre-deployment checks, pushing to staging and then prod"""
    spellcheck_needed = True
    key_files_changed = repo_pull()
    if key_files_changed:
        abort(red("Aborting as the following key files changed: %s" %
              (",".join(key_files_changed),)))
    maybe_add_untracked_files(is_interactive_deploy)
    _initialise()
    while spellcheck_needed:
        # Re-run spellchecker if changes were found, but only if we're doing
        #  an interactive deployment
        spellcheck_needed = spellchecker(is_interactive_deploy)
        if spellcheck_needed and not is_interactive_deploy:
            abort("Spellcheck errors during non-interactive deploy."
                  " Unable to proceed")
    build()
    requirements_dump()
    repo_status(is_interactive_deploy)
    staging_sync()
    if not is_interactive_deploy or confirm("Push to live site?"):
        prod_sync()
        repo_push()
    else:
        print red("Not pushing to live site.")

    post_deploy()


def non_interactive_deploy():
    """Helper method to trigger non-interactive deployment"""
    if sys.stdin.isatty():
        if not confirm("Simulate a non-interactive deploy?", default=False):
            abort("Aborting")
    else:
        print "Running non-interactive deploy"

    deploy(is_interactive_deploy=False)
