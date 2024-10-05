## Usage
There are 2 main scripts:
  * **main.py** - this is what ingests your data into the database. all files are written to the **.ragatouille/** folder.
  * **cli.py** - a text ui to interact with the RAG. **max_context** should be adjusted to the context settings in ollama. the conversation memory will be a sliding window based on the conversation length.
  
Additionally, there are some optional flags: 
  * **--metadata-enabled**: enrich the RAG data further, but it is optional. It will use Ollama to crawl the dataset 
and summarize, extract tags and urls from the content, which will be provided if available when running user queries. 
It's a little time-consuming to run!
  * **--evaluate**:  run a BERTScore evaluation on the data you've ingested


Ingesting data:
```bash
# if using data/ directory in root of this project:
poetry run vxllm
# --data allows you to use a custom data folder path for ingestion
poetry run vxllm --data /path/to/your/files
# --generate-metadata which will return tags, references and urls in documents
poetry run vxllm --metadata-enabled
```

Searching:
```bash
poetry run cli
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
  
