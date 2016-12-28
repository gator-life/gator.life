#!/bin/bash

# kill gcloud and free port if needed
pkill ^gcloud$
fuser -k 33001/tcp