#!/bin/bash

docker build -t sim .
if [ "$(docker container inspect -f '{{.State.Running}}' sim)" = "true" ]; then
    docker container stop sim
fi
docker container rm sim
docker run -p 5000-5010:5000-5010 -d --name sim sim
docker container logs sim