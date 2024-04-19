#!/bin/bash
## Find the id of container created above
container_id=$(docker ps -q --filter ancestor=ghcr.io/huggingface/text-generation-inference:1.4)
if  [ -z "$container_id" ]; then
    echo "Container not found"
    exit 1
fi
## Find file name starting with $container_id
file_name=$(find . -name "$container_id*")
docker logs -f ${container_id} | tee $file_name
