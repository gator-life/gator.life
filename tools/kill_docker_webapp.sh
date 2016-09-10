#!/bin/bash

# cf. http://stackoverflow.com/questions/3510673/find-and-kill-a-process-in-one-line-using-bash-and-regex 
docker stop $(sudo docker ps | grep '[g]ator.life:dev-webapp' | awk '{print $1}')