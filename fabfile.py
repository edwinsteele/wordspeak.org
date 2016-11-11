from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import map
import csv
import glob
import os
import re
import smtplib
import socket
import sys
import tempfile
import urllib.request, urllib.parse, urllib.error
from email.mime.text import MIMEText
from fabric.api import abort, local, settings
from fabric.colors import green, red, yellow
from fabric.contrib.console import confirm
from fabric.context_managers import cd, hide, quiet, warn_only
from fabric.operations import prompt
import enchant
import enchant.checker
import enchant.tokenize
import requests
import conf
from chump import Application

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
W3C_HTML_VALIDATION_URL = 'https://validator.w3.org/nu/?doc=%s&out=%s'
W3C_HTML_VALIDATION_TARGETS = [
    'https://origin.wordspeak.org/index.html',
    'https://origin.wordspeak.org/pages/about.html',
    'https://origin.wordspeak.org/posts/write-because-you-want-to.html',
    'https://origin.wordspeak.org/posts/nsw-fires.html',
]
W3C_CSS_VALIDATION_URL = 'http://jigsaw.w3.org/css-validator/validator?' \
                         'uri=%s&profile=css3&usermedium=all&warning=1&' \
                         'vextwarning=&lang=en&output=%s'
W3C_CSS_VALIDATION_TARGETS = [
    'https://origin.wordspeak.org/assets/css/all-nocdn.css',
]
W3C_RSS_VALIDATION_URL = 'http://validator.w3.org/feed/check.cgi?url=%s'
W3C_RSS_VALIDATION_TARGETS = [
    'https://origin.wordspeak.org/rss.xml',
]
LANGUAGE_EXPLORER_DIRNAME = "language_explorer"


def _does_this_machine_answer_for_this_hostname(dns_name):
    """Looks at DNS and local interfaces to see if this host answers for the
     DNS name in question

    Caveats:
    - Won't work reliably if the DNS entry resolves to more than one address
    - Won't work if there are no PTR entries
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
    try:
        ptr_lookup_result = socket.gethostbyaddr(
            socket.gethostbyname(dns_name))[0]
    except socket.herror:
        # No PTR records available and nothing in local /etc/hosts to help.
        # Let's be conservative and say that we don't answer for it.
        return False

    return socket.gethostbyname(ptr_lookup_result) in (my_main_ip, '127.0.0.1')


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
            print("%s actions performed\n" %
                  (len(result.stderr.splitlines()) - 1), end=' ')
        else:
            print("No output from command.")


def build():
    """Build the site using nikola"""
    with cd(SITE_BASE):
        _quietly_run_nikola_cmd("nikola", "build")
        _quietly_run_nikola_cmd("nikola", "mincss")
        # Need to recopy the leaflet.css file as mincss optimises it away
        #  because it can't find any leaflet classes in use (they're inserted
        #  at runtime by the js library
        local("cp %s/files/assets/leaflet-0.7.3/leaflet.css "
              "%s/assets/leaflet-0.7.3/leaflet.css" % (SITE_BASE, OUTPUT_BASE))
        # Need to recompress css after yuicompressor has run
        #  Can't run post_render_gzip in N7, so let's just do build again
        _quietly_run_nikola_cmd("nikola", "build")

    post_build_cleanup()


def requirements_dump():
    """pip freeze the package requirements"""
    with cd(SITE_BASE):
        # pyinotify and MacFSEvents only build on their particular platform
        #  so exclude them. They'll get pulled in when a pip install doit
        #  is done so there's no loss.
        # bsddb3 is only necessary on MacOS and is a pain to build, so we
        #  don't use it. This requires a quick change in doit.
        #
        # Uncomment the following line in site-packages/doit/dependency.py
        #
        # import gdbm as ddbm
        #
        # It might be necessary to nuke the doit db file after this change:
        local("pip freeze | "
              "egrep -v '(pyinotify|MacFSEvents|bsddb3)' | "
              "sort -f "
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
                print("Adding untracked file '%s' during non-interactive"
                      " deploy" % (line[3:],))

            with cd(SITE_BASE):
                local("git add '%s'" % (line[3:],))


def repo_status(is_interactive_deploy):
    """Check whether there are any uncommitted/untracked files in the repo"""
    with cd(SITE_BASE):
        result = local("git status --porcelain", capture=True)
    if result.stdout:
        print(result.stdout)
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
        local('rsync '
              '--delete '
              '--filter="protect %s" '
              '--filter="exclude *.md" '
              '--filter="exclude *.md.gz" '
              '-a %s/ %s' %
              (LANGUAGE_EXPLORER_DIRNAME, OUTPUT_BASE, destination_path))


def staging_sync():
    """Sync the site to the staging server"""
    if _does_this_machine_answer_for_this_hostname(STAGING_FQDN):
        destination = STAGING_RSYNC_DESTINATION_LOCAL
    else:
        destination = STAGING_RSYNC_DESTINATION_REMOTE

    _sync_site(destination)
    local("rsync -a %s/staging_robots.txt %s/robots.txt" %
          (SITE_BASE, destination))


def prod_sync():
    """Sync the site to the prod server"""
    with cd(SITE_BASE):
        local("rsync -a %s/prod_robots.txt %s/robots.txt" %
              (SITE_BASE, OUTPUT_BASE))
    if _does_this_machine_answer_for_this_hostname(PROD_FQDN):
        _sync_site(PROD_RSYNC_DESTINATION_LOCAL)
    else:
        _sync_site(PROD_RSYNC_DESTINATION_REMOTE)


def linkchecker(output_fd=sys.stdout):
    """Checks for broken links on the staging site

    Ignores posts because the links all appear in the index pages
    Returns whether the task found any 404s
    """
    with cd(SITE_BASE):
        output = local("nikola check -l -r --find-sources", capture=True)

    # Filter out info lines
    output = [line for line in output.stderr.splitlines()
              if b'INFO: requests.packages.urllib3.connectionpool' not in line]
    # Notification about problems in index files are duplicates
    # Let's go with the notifications in the files themselves, as they will
    #  likely have the md source location.
    is_an_index_page = re.compile(b'index-[0-9]+.html:')
    output = [line for line in output
              if not is_an_index_page.search(line)]
    broken_links = [line for line in output
                    if b'Error 404' in line]
    # We're interested in the remaining text, regardless of whether it's
    #  formally categorised as warning by nikola or not
    warning_lines = [line for line in output
                     if b'Error 404' not in line]

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
        return False
    else:
        output_fd.write(green("No broken links found.\n"))
        print_warning_lines(warning_lines, output_fd)
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
    print(result.stderr)
    print(result.stdout)
    # Something like:
    #
    # Updating 815b459..d9a508d
    # Fast-forward
    # fabfile.py       | 2 +-
    # requirements.txt | 1 -
    # 2 files changed, 1 insertion(+), 2 deletions(-)

    # return something that evaluates to true if we updated a key file
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

        e = _get_spellcheck_exceptions(lines)
        list(map(pwl_dictionary.add_to_session, e))
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
                    if is_interactive_deploy:
                        action = prompt("Add '%s' to dictionary [add] or "
                                        "replace [type replacement]?"
                                        % (err.word,), default="add").strip()
                        if action == "add":
                            _add_to_spellcheck_exceptions(file_to_check,
                                                          err.word)
                            pwl_dictionary.add(err.word)
                        else:
                            _replace_in_file(file_to_check, err.word, action)
                    else:
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
            output_fd.write("Full details: %s\n" % (W3C_RSS_VALIDATION_URL %
                                                    (urllib.parse.quote_plus(url))))
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
        import rcssmin  # for css minifaction
    except ImportError as e:
        # noinspection PyUnusedLocal
        webassets = rcssmin = None
        abort(red("Missing module: %s" % (e,)))
    get_env_variable("WORDSPEAK_PUSHOVER_USER")
    get_env_variable("WORDSPEAK_PUSHOVER_API_TOKEN")


def _send_pushover_summary(message, title):
    app = Application(get_env_variable("WORDSPEAK_PUSHOVER_API_TOKEN"))
    user = app.get_user(get_env_variable("WORDSPEAK_PUSHOVER_USER"))
    return user.send_message(message=message, title=title)


def post_deploy():
    """Runs time consuming tasks, or those that don't need to be run inline"""
    _initialise()
    scratch = tempfile.TemporaryFile()
    ran_successfully = linkchecker(scratch)
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
        print("Sending summary mail... ", end=' ')
        try:
            mail_server = smtplib.SMTP('localhost')
            mail_server.sendmail(conf.BLOG_EMAIL, [conf.BLOG_EMAIL],
                                 msg.as_string())
            mail_server.quit()
        except smtplib.SMTPException as e:
            print(red("Failed.\n%s", (e,)))
        else:
            print(green("Success."))


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
        print(red("Not pushing to live site."))

    post_deploy()


def non_interactive_deploy():
    """Helper method to trigger non-interactive deployment"""
    if sys.stdin.isatty():
        if not confirm("Simulate a non-interactive deploy?", default=False):
            abort("Aborting")
    else:
        print("Running non-interactive deploy")

    deploy(is_interactive_deploy=False)
