#!/bin/bash
# script must be executed from root git directory

# copy local package dependencies to server folder
{ cat src/server/local_deps.txt; echo; } | while read line; do cp -R "src/$line/$line" src/server; done

# build production-ready web app (minified...) under client and copy it to server
(cd src/client && npm run build)
cp -R src/client/build/** src/server/server