#!/bin/bash
#Set some env vars
#export SOURCE_DIR=$FURHOME/src
export CUSER="roaduser"
export PID=$(id -u $USER)
export GID=$(id -g $USER)

export IMAGE="devhub.dmi.dk/cap/shadows_basic"
alias docker_clean_images='docker rmi $(docker images -a --filter=dangling=true 
-q)'
alias brute_force_clean='docker rmi $(docker images -a)'
alias docker_clean_ps='docker rm $(docker ps --filter=status=exited --filter=sta
tus=created -q)'

