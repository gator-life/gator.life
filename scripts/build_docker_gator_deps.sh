#!/bin/bash
set -e
cp requirements.txt docker_images/gator_deps/requirements.txt 
cd docker_images/gator_deps
docker build -t gator_deps .

rm requirements.txt

cd ../..