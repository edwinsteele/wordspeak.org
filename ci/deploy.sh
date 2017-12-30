#!/bin/bash

STAGING_DEPLOY_KEY="ci/staging-sync-id_rsa"
PROD_DEPLOY_KEY="ci/prod-sync-id_rsa"
SSH_STANDARD_ARGS="-l esteele -o StrictHostKeyChecking=no -o BatchMode=yes"

deploy_to_staging( ) {
  echo "Deploying to staging";
  rsync -av \
    -e "ssh $SSH_STANDARD_ARGS -i $STAGING_DEPLOY_KEY" \
    --delete \
    --filter="protect language_explorer" \
    --filter="exclude *.md" \
    --filter="exclude *.md.gz" \
    output/ \
    origin.wordspeak.org:/home/esteele/Sites/staging.wordspeak.org/
}

deploy_to_prod( ) {
  echo "Deploying to prod";
  rsync -av \
    -e "ssh $SSH_STANDARD_ARGS -i $PROD_DEPLOY_KEY" \
    --delete \
    --filter="protect language_explorer" \
    --filter="exclude *.md" \
    --filter="exclude *.md.gz" \
    output/ \
    origin.wordspeak.org:/home/esteele/Sites/www.wordspeak.org/
}

if [ "$1" = "staging" ]; then
  touch $STAGING_DEPLOY_KEY
  chmod 600 $STAGING_DEPLOY_KEY
  openssl aes-256-cbc \
    -K $encrypted_68de9d9be834_key \
    -iv $encrypted_68de9d9be834_iv \
    -in $STAGING_DEPLOY_KEY.enc \
    -out $STAGING_DEPLOY_KEY \
    -d
  deploy_to_staging
  rm $STAGING_DEPLOY_KEY
fi

if [ "$1" = "prod" ]; then
  touch $PROD_DEPLOY_KEY
  chmod 600 $PROD_DEPLOY_KEY
  openssl aes-256-cbc \
    -K $encrypted_68de9d9be834_key \
    -iv $encrypted_68de9d9be834_iv \
    -in $PROD_DEPLOY_KEY.enc \
    -out $PROD_DEPLOY_KEY \
    -d
  deploy_to_prod
  rm $PROD_DEPLOY_KEY
fi
