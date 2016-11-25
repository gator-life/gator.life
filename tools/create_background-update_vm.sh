#!/bin/bash

#This script create compute engine VM to host background_update docker container  

#we use gci image (--image-family gci-stable --image-project google-containers)
#because it comes with docker installed and configured to access gcr

#--scopes takes all services enables by dedault + access to datastore

#To access VM:
#gcloud compute ssh LOGIN@INSTANCE_NAME

gcloud compute instances create background-update --image-family gci-stable --image-project google-containers --machine-type "g1-small" --scopes default="https://www.googleapis.com/auth/datastore","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring.write","https://www.googleapis.com/auth/trace.append","https://www.googleapis.com/auth/devstorage.read_only"
