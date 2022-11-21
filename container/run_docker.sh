source ./env.sh
#server
#docker run -it --rm -p 9696:9696 $IMAGE

#just bash
docker run -it --name testroad --rm -p 0.0.0.0:9696:9696 $IMAGE
#docker exec -ti $IMAGE bash
