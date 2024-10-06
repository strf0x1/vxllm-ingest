#!/bin/bash
OLLAMA_MODEL=""
MAX_CONTEXT=""
# default to this directory, data folder. replace with your own data dir
DATA_DIR="$PWD/data/"
# this should not change
RAG_DB_DIR="$PWD/.ragatouille"
# attempt to fetch the primary adapter's ip, pass it over to the container via .env import
ipaddress=$(ip -4 addr show scope global | grep inet | awk '{print $2}' | cut -d/ -f1 | head -n 1)

# check for vxllm docker image, build if not present
if [[ "$(docker images -q vxllm 2> /dev/null)" == "" ]]; then
    echo "Image 'vxllm' does not exist. Building the image..."
    docker build -t vxllm .
else
    echo "Docker image 'vxllm' already exists."
fi

# persist ragatouille db
if [ ! -d "$RAG_DB_DIR" ]; then
    mkdir -p "$RAG_DB_DIR"
    echo "Directory created: $RAG_DB_DIR"
fi

# create data directory
if [ ! -d "data/" ]; then
    mkdir -p "data"
    echo "Directory created: data"
fi

# init env vars for container
echo "OLLAMA_HOST=$ipaddress" > .env

if [ ! -z "$OLLAMA_MODEL" ]; then
    echo "OLLAMA_MODEL=$OLLAMA_MODEL" >> .env
fi

# Append MAX_CONTEXT to .env if not blank
if [ ! -z "$MAX_CONTEXT" ]; then
    echo "MAX_CONTEXT=$MAX_CONTEXT" >> .env
fi

docker run --env-file .env --rm -it --gpus all --network host -v $RAG_DB_DIR:/app/.ragatouille -v $DATA_DIR:/app/data \
-v ./vxllm:/app/vxllm -v ./pyproject.toml:/app/pyproject.toml vxllm
