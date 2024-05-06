#!/bin/bash

docker build -t sim .
if [ "$(docker container inspect -f '{{.State.Running}}' sim)" = "true" ]; then
    docker container stop sim
    docker container rm sim
fi
docker run -p 5000-5010:5000-5010 -d --name sim sim
docker container exec -it sim bash