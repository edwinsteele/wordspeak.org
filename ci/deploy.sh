#!/bin/bash

DEPLOY_KEY="ci/deploy-id_rsa"
SSH_STANDARD_ARGS="-l esteele -o StrictHostKeyChecking=no -o BatchMode=yes"

touch $DEPLOY_KEY
chmod 600 $DEPLOY_KEY

if [ "$1" = "staging" ]; then
  echo "Deploying to staging";
  ENCRYPTED_KEY="ci/staging-sync-id_rsa.enc"
  TARGET_SITE="staging.wordspeak.org"
elif [ "$1" = "prod" ]; then
  echo "Deploying to prod";
  ENCRYPTED_KEY="ci/prod-sync-id_rsa.enc"
  TARGET_SITE="www.wordspeak.org"
else
  echo "Unknown deployment target. Exiting";
  exit 1;
fi

openssl aes-256-cbc \
  -K $encrypted_68de9d9be834_key \
  -iv $encrypted_68de9d9be834_iv \
  -in $ENCRYPTED_KEY \
  -out $DEPLOY_KEY \
  -d

rsync -av \
  -e "ssh $SSH_STANDARD_ARGS -i $DEPLOY_KEY" \
  --delete \
  --filter="protect language_explorer" \
  --filter="exclude *.md" \
  --filter="exclude *.md.gz" \
  output/ \
  origin.wordspeak.org:/home/esteele/Sites/$TARGET_SITE/

exit $?
