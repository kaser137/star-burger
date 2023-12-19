#!/bin/bash

set -e

echo start change directory
cd /opt/star-burger
echo change directory done

echo start git pull
git pull
echo git pull done

echo start renew requirements
./venv/bin/pip3 install -r requirements.txt
echo renew requirements done

echo start mount  packages of NodeJS
npm ci --include=dev 
echo mount  packages of NodeJS done

echo start parcel
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
echo parcel has been executed

echo start collectstatic
./venv/bin/python3 manage.py collectstatic --noinput
echo collectstatic done

echo start migrate
./venv/bin/python3 manage.py migrate --noinput
echo migrate done

echo start restart gunicorn
systemctl restart star-burger.service
echo restart gunicorn done

echo start reload nginx
systemctl reload nginx.service
echo reload nginx done

source .env

COMMENT="$(date) deploy" 
COMMIT=$(git rev-parse --short HEAD)
 
curl -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "'"$ENV_NAME"'", "revision": "'"$COMMIT"'", "rollbar_name": "buzhyn", "local_username": "'"$USER"'", "comment": "'"$COMMENT"'", "status": "succeeded"}'

echo code has been successfully renewed
