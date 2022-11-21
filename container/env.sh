#!/bin/bash
#Set some env vars
#export SOURCE_DIR=$FURHOME/src
export CUSER="roaduser"
export PID=$(id -u $USER)
export GID=$(id -g $USER)

#for bare bones python
#export IMAGE="devhub.dmi.dk/cap/shadows_basic"
#for grass image
export IMAGE="devhub.dmi.dk/cap/shadows_grass"

alias docker_clean_images='docker rmi $(docker images -a --filter=dangling=true 
-q)'
alias brute_force_clean='docker rmi $(docker images -a)'
alias docker_clean_ps='docker rm $(docker ps --filter=status=exited --filter=status=created -q)'

