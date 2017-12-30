#!/bin/bash

deploy_to_staging( ) {
  echo "Deploying to staging"; 
}

deploy_to_prod( ) {
  echo "Deploying to prod";
}

echo "Running with TRAVIS_BRANCH = $TRAVIS_BRANCH"
deploy_to_staging

if [ "$TRAVIS_BRANCH" = "master" ]; then
  deploy_to_prod
fi
