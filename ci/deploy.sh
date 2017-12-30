#!/bin/bash

deploy_to_staging( ) {
  echo "Deploying to staging"; 
  rsync -av -e 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -i ci/wordspeak-sync-id_rsa' --delete --filter="protect language_explorer" --filter="exclude *.md" --filter="exclude *.md.gz" output/ origin.wordspeak.org:/home/esteele/Sites/staging.wordspeak.org/
}

deploy_to_prod( ) {
  echo "Deploying to prod";
}

if [ "$1" = "staging" ]; then
  deploy_to_staging
fi

if [ "$1" = "master" ]; then
  deploy_to_prod
fi
