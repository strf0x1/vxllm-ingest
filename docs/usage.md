## Usage
There are 3 main scripts:
  * **loader.py** - this is what ingests your data into the database. all files are written to the **.ragatouille/** folder.
    * the **documents** variable points to **data/** by default in the root folder. You can symlink some data in there or change the path with **--data**. The crawl is recursive.
  * **cli.py** - a text ui to interact with the RAG. **max_context** should be adjusted to the context settings in ollama. the conversation memory will be a sliding window based on the conversation length.
  * **evaluate_bertscore.py** - an evaluation script using BERTScore
  
Additionally, there is an **extract_metadata.py** script to enrich the RAG data further, but it is optional. It will use 
Ollama to crawl the dataset and summarize, extract tags and urls from the content, which will be provided if available
when running user queries. It's a little time-consuming to run, so I left it out of the main project.

Optional: generating metadata:
```bash
# if using data/ directory in root of this project:
poetry run python extract_metadata.py
# or
poetry run python extract_metadata.py --data /path/to/your/files
```

Ingesting data (same command in container):
```bash
# if using data/ directory in root of this project:
poetry run vxllm
# --data allows you to use a custom data folder path for ingestion
poetry run vxllm --data /path/to/your/files
```

Searching:
```bash
poetry run cli
```
On linux, you will need to pass the **--client** parameter because ollama will be hosted on your primary 
adapter, not within the container:
```bash
# on your host, get your primary ip:
$ ip a
# in the container:
$ ./run_container.sh
$ poetry run cli --client http://your_ip:11434
```
  
## Models
There are some really great local models available now. I used the default q4 models from Ollama. My favorites have been:
  * mistral-nemo - 12b model. It writes excellent code, so its responses have been subjectively better than a lot of the other reasonably-sized models.
  * qwen2.5 - New model on the block that performs really well and a little bit faster than nemo. On evals, it actually tends to perform a little better than nemo.
  * gemma2b - 2b model from google that has performed surprisingly well and fast for its size. It performs competitively with much larger models on code evals.
  
If you would like to extend the context length of the model, the easiest way is to duplicate an existing Modelfile, and
load it in to Ollama:
```bash

```
  
## Example queries you can use:
  
