#!/bin/bash
ARG1=${1:-apply}
echo "Attempting to $ARG1"
echo "If you meant otherwise please specify input argument."
echo "Options are: replace (default) or apply"
source env.sh
#kubectl --v=0 --namespace=$NAMESPACE $ARG1 -f shadows.yml

#this one works
kubectl --namespace=glattesting apply -f shadows.yml 
#kubectl -n glattesting port-forward 
