#!/bin/bash

# cf. http://stackoverflow.com/questions/3510673/find-and-kill-a-process-in-one-line-using-bash-and-regex 
kill $(ps aux | grep '[g]unicorn -b 127.0.0.1:8080' | awk '{print $2}')
fuser -k 8080/tcp