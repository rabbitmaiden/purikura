#!/bin/bash -e

if [ -z "$1" ]
  then
    echo "Usage: ./deploy.sh {hostname}"
    exit 1
fi

echo "Pushing latest to $1"
cd ..
tar -czf purikura.tar purikura/* --exclude=psd --exclude=.tar --exclude=.git --exclude=deploy.sh
scp purikura.tar pi@$1:purikura.tar
ssh pi@$1 tar -xzf purikura.tar

rm purikura.tar
