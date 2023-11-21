#!/bin/bash

set -e

echo start update

cd /opt/devman/star-burger/
echo redirect in star-burger directoty

git pull
echo renew repository

source ./venv/bin/activate
echo start virtual enviroment

pip3 install -r requirements.txt
echo renew packages of python

npm ci --dev
echo renew packages of Node.js

./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
echo mount frontend and start parcel for watching changes JS code

./manage.py collectstatic --noinput
echo collecting static files

./manage.py migrate
echo migrate database

systemctl daemon-reload
echo reload daemon services

echo update is finished
