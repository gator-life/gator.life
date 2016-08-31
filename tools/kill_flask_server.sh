#!/bin/bash

# cf. http://stackoverflow.com/questions/3510673/find-and-kill-a-process-in-one-line-using-bash-and-regex 
kill $(ps aux | grep '[p]ython src/server/main.py' | awk '{print $2}')
fuser -k 8080/tcp