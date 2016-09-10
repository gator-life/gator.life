#!/bin/bash

# Retrieve the docker host ip on docker0 interface. This interface is described as the
# "virtual Ethernet bridge that... lets containers communicate both with the host machine and with each other."
export HOST_IP_DOCKER0=`ip route show | grep docker0 | awk '{print $9}'`

export DATASTORE_HOST_PORT=$HOST_IP_DOCKER0:33001
export DATASTORE_HOST=http://$DATASTORE_HOST_PORT
