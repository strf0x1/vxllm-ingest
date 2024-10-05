#!/bin/bash
DATA_DIR='/home/brandon/Documents/vxllm_docs/maldev_academy_markdown/'
RAG_DB_DIR='.ragatouille'
ipaddress=$(ip -4 addr show scope global | grep inet | awk '{print $2}' | cut -d/ -f1 | head -n 1)
echo "OLLAMA_HOST=$ipaddress" > .env

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

docker run --env-file .env --rm -it --gpus all --network host -v "./"$RAG_DB_DIR:/app/.ragatouille -v $DATA_DIR:/app/data \
-v ./vxllm:/app/vxllm -v ./pyproject.toml:/app/pyproject.toml vxllm
