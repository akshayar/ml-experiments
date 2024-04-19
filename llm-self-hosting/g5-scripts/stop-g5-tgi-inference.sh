#!/bin/bash
## Find the id of container created above
container_id=$(docker ps -q --filter ancestor=ghcr.io/huggingface/text-generation-inference:1.4)

docker kill $container_id
