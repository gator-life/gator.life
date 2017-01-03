#!/bin/bash
# script must be executed from root git directory
. scripts/set_env_vars.sh

scripts/start_server.sh

if [ "$1" = "cover" ]; then
	export COVERAGE='True'
	coverage run --source=src --omit=*tests* -m py.test src
	( cd src/client && npm test -- --coverage )

else
	py.test src
	( cd src/client && npm test )
fi

#the if was quite painfull to get right, for memory:
#http://stackoverflow.com/questions/9727695/bash-scripting-if-arguments-is-equal-to-this-string-define-a-variable-like-thi