#!/bin/bash

STAGING_DEPLOY_KEY_ENC="ci/staging-sync-id_rsa.enc"
PROD_DEPLOY_KEY_ENC="ci/prod-sync-id_rsa.enc"
DEPLOY_KEY="ci/deploy-id_rsa"

SSH_STANDARD_ARGS="-l esteele -o StrictHostKeyChecking=no -o BatchMode=yes"

touch $DEPLOY_KEY
chmod 600 $DEPLOY_KEY

if [ "$1" = "staging" ]; then
  echo "Deploying to staging";
  encrypted_key=$STAGING_DEPLOY_KEY_ENC
  target_site="staging.wordspeak.org"
elif [ "$1" = "prod" ]; then
  echo "Deploying to prod";
  encrypted_key=$PROD_DEPLOY_KEY_ENC
  target_site="www.wordspeak.org"
else
  echo "Unknown deployment target. Exiting";
  exit 1;
fi

openssl aes-256-cbc \
  -K $encrypted_68de9d9be834_key \
  -iv $encrypted_68de9d9be834_iv \
  -in $encrypted_key \
  -out $DEPLOY_KEY \
  -d

rsync -av \
  -e "ssh $SSH_STANDARD_ARGS -i $DEPLOY_KEY" \
  --delete \
  --filter="protect language_explorer" \
  --filter="exclude *.md" \
  --filter="exclude *.md.gz" \
  output/ \
  origin.wordspeak.org:/home/esteele/Sites/$target_site/

exit $?
