#!/bin/bash
model=$1
usecase=$2
volume=$PWD/data

## Check if HF_TOKEN is set, if not error and exit
if [ -z "${HF_TOKEN}" ]; then
    echo "Error: HF_TOKEN is not set"
    exit 1
fi
## Check if model is set, if not set default model
if [ -z "$model" ]; then
    model=meta-llama/Llama-2-7b-chat-hf
    echo "Error: model is not set using $model"
fi

## parse text of $model varriable after '/'
model_name=$(echo $model | cut -d'/' -f2)

## Find current time in DD_MM_YYYY_mm_ss format
current_time=$(date "+%d_%m_%Y_%H_%M_%S")

## Check if CUDA_VISIBLE_DEVICES is set
if [ -z "${CUDA_VISIBLE_DEVICES}" ]; then
    echo "Error: CUDA_VISIBLE_DEVICES is not set"
    echo "$model_name without explicit CUDA_VISIBLE_DEVICES "
    docker run --gpus all --shm-size 1g -p 8080:80 -d \
    -v $volume:/data \
    -e HF_TOKEN=${HF_TOKEN} $ADD_ENVS\
    ghcr.io/huggingface/text-generation-inference:1.4 \
    --model-id $model $ADD_PARMS
    ## Find the id of container created above
    container_id=$(docker ps -q --filter ancestor=ghcr.io/huggingface/text-generation-inference:1.4)
else
    echo "Error: CUDA_VISIBLE_DEVICES is set to $CUDA_VISIBLE_DEVICES "
    ## Count number of GPU from CUDA_VISIBLE_DEVICES variable
    num_gpus=$(echo $CUDA_VISIBLE_DEVICES | tr ',' '\n' | wc -l)
    echo "$model_name with CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES and shards =$num_gpus "

    docker run --gpus all --shm-size 1g -p 8080:80 -d \
    -v $volume:/data \
    -e HF_TOKEN=${HF_TOKEN} $ADD_ENVS\
    -e CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES \
    ghcr.io/huggingface/text-generation-inference:1.4 \
    --model-id $model\
     --num-shard $num_gpus $ADD_PARMS
    ## Find the id of container created above
    container_id=$(docker ps -q --filter ancestor=ghcr.io/huggingface/text-generation-inference:1.4)
fi
## write code to iterate through a file list


echo "Started $container_id"
file_name="$container_id"_"shards"$num_gpus"_"$model_name"_"$current_time"_"$usecase".txt"
docker logs $container_id >> $file_name
