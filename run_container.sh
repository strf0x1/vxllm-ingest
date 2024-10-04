#!/bin/bash
DATA_DIR=/home/brandon/Documents/vxllm_docs/maldev_academy_markdown

# check for vxllm docker image, build if not present
if [[ "$(docker images -q vxllm 2> /dev/null)" == "" ]]; then
    echo "Image 'vxllm' does not exist. Building the image..."
    docker build -t vxllm .
else
    echo "Docker image 'vxllm' already exists."
fi


# check if rag db dir exists, so data always persists across container restarts
RAG_DB_DIR=./.ragatouille
if [ ! -d "$DATA_DIR" ]; then
    mkdir -p "$DATA_DIR"
    echo "Directory created: $dir_path"
fi

docker run --rm -it --gpus all --network host -v $RAG_DB_DIR/app/.ragatouille -v $DATA_DIR:/app/data -v ./extract_metadata.py:/app/extract_metadata.py  -v ./loader.py:/app/loader.py -v ./cli.py:/app/cli.py -v ./evaluate_bertscore.py:/app/evaluate_bertscore.py vxllm