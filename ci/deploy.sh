#!/bin/bash

SSH_STANDARD_ARGS="-l esteele -o StrictHostKeyChecking=no -o BatchMode=yes"

if [ "$1" = "staging" ]; then
  echo "Deploying to staging";
  DEPLOY_KEY="ci/staging-sync-id_rsa"
  TARGET_SITE="staging.wordspeak.org"
elif [ "$1" = "prod" ]; then
  echo "Deploying to prod";
  DEPLOY_KEY="ci/prod-sync-id_rsa"
  TARGET_SITE="www.wordspeak.org"
else
  echo "Unknown deployment target. Exiting";
  exit 1;
fi

rsync -av \
  -e "ssh $SSH_STANDARD_ARGS -i $DEPLOY_KEY" \
  --delete \
  --filter="protect language_explorer" \
  --filter="exclude *.md" \
  --filter="exclude *.md.gz" \
  output/ \
  origin.wordspeak.org:/home/esteele/Sites/$TARGET_SITE/
rsync_exit=$?

exit $rsync_exit
