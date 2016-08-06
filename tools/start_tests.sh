#!/bin/bash
# script must be executed from root git directory

. tools/set_env_vars.sh

tools/start_server.sh

if [ "$1" = "cover" ]; then
	coverage run --source=src --omit=*tests* -m py.test src
else
	py.test src
fi

#the if was quite painfull to get right, for memory:
#http://stackoverflow.com/questions/9727695/bash-scripting-if-arguments-is-equal-to-this-string-define-a-variable-like-thi