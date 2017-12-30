#!/bin/bash

STAGING_DEPLOY_KEY="ci/wordspeak-sync-id_rsa"

deploy_to_staging( ) {
  echo "Deploying to staging"; 
  rsync -av -e "ssh -l esteele -o StrictHostKeyChecking=no -o BatchMode=yes -i $STAGING_DEPLOY_KEY" --delete --filter="protect language_explorer" --filter="exclude *.md" --filter="exclude *.md.gz" output/ origin.wordspeak.org:/home/esteele/Sites/staging.wordspeak.org/
}

deploy_to_prod( ) {
  echo "Deploying to prod";
}

if [ "$1" = "staging" ]; then
  touch $STAGING_DEPLOY_KEY
  chmod 600 $STAGING_DEPLOY_KEY
  openssl aes-256-cbc -K $encrypted_68de9d9be834_key -iv $encrypted_68de9d9be834_iv -in $STAGING_DEPLOY_KEY.enc -out $STAGING_DEPLOY_KEY -d
  deploy_to_staging
  rm $STAGING_DEPLOY_KEY
fi

if [ "$1" = "master" ]; then
  deploy_to_prod
fi
