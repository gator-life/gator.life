#!/bin/bash
set -e
docker build -f docker_images/background_update/Dockerfile -t background_update .