from fabric.api import abort, local, settings
from fabric.contrib.console import confirm
from fabric.context_managers import cd, quiet

STAGING_RSYNC_DESTINATION = "/Users/esteele/Sites/staging.wordspeak.org"
PROD_RSYNC_DESTINATION = "wordspeak.org:/users/home/esteele/web/public"
DEV_NIKOLA = "/Users/esteele/Code/nikola-edwinsteele/nikola/scripts/nikola"
REL_NIKOLA = "/Users/esteele/.virtualenvs/wordspeak/bin/nikola"
SITE_BASE = "/Users/esteele/Code/wordspeak.org"


def nikola_build():
    with quiet():
        if local("test '$(showvirtualenv)' == 'nikola-dev'").succeeded:
            nikola = DEV_NIKOLA
        else:
            nikola = REL_NIKOLA

    with cd(SITE_BASE):
        result = local("%s build" % (nikola,), capture=True)
        print "%s actions performed\n" % \
              (len(result.stdout.splitlines()) - 1),


def repo_status():
    result = local("git status --porcelain", capture=True)
    if result.stdout:
        print result.stdout
        if not confirm("Repo has uncommitted/untracked files. Continue?"):
            abort("Aborting at user request.")


def sync(destination_path):
    with cd(SITE_BASE):
        local("rsync --del -a output/ %s" % (destination_path,))
        local("rsync --del -a output/.htaccess %s" %
              (destination_path,))


def linkchecker():
    with settings(warn_only=True):
        result = local("linkchecker"
                       " --config linkcheckerrc"
                       " --no-status"
                       " http://staging.wordspeak.org",
                       capture=True)
    if result.failed:
        if not confirm("Failures with Linkchecker. %s Continue anyway?" %
                      ("\n".join(result.stdout.splitlines()[9:]))):
            abort("Aborting at user request.")
    else:
        # Summary is the second to last line
        print result.stdout.splitlines()[-2]


def repo_push():
    local("git push")


def deploy():
    nikola_build()
    repo_status()
    sync(STAGING_RSYNC_DESTINATION)
    linkchecker()
    if confirm("Push to live site?"):
        sync(PROD_RSYNC_DESTINATION)
        repo_push()
    else:
        print "Not pushing to live site."

if __name__ == '__main__':
    deploy()