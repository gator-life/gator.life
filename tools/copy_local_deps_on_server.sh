#!/bin/bash

# script must be executed from root git directory

{ cat src/server/local_deps.txt; echo; } | while read line; do cp -R "src/$line/$line" src/server; done