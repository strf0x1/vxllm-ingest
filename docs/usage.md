## Usage
There are 2 main scripts:
  * **main.py** - this is what ingests your data into the database. all files are written to the **.ragatouille/** folder.
  * **cli.py** - a text ui to interact with the RAG.
  * **evaluate.py** - BERTScore evaluation


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
After a fresh ingest, the first query you make will be slower because Ragatouille does some initialization. It improves 
for subsequent queries:
  
## Models
There are some really great local models available now. I used the default q4 models from Ollama. My favorites have been:
  * mistral-nemo - 12b model. It writes excellent code, so its responses are subjectively better than a lot of the other reasonably-sized models.
  * qwen2.5 - New model on the block that performs really well and a little bit faster than nemo. On evals, it actually tends to perform a little better than nemo.
  * gemma2b - 2b model from google that has performed surprisingly well and fast for its size. It performs competitively with much larger models on code evals.
  
If you would like to extend the context length of the model, the easiest way is to duplicate an existing Modelfile and
import it into Ollama:
```bash
ollama show gemma2:2b --modelfile > Modelfile
vim Modelfile
# in vim, add this below the other parameters: PARAMETER num_ctx 8096
ollama create gemma2:2b-8096 --file Modelfile
```
Then you'll want to tweak cli.py at the top for these values:
```
console = Console()
ollama_model="gemma2:2b-8096"
max_context=8096
```
Refer to the model's docs for max suggested context length.

## Example queries you can use:
  * explain linux process injection to me
  * what are anti-reversing techinques and give me some code examples
  * help me write a detection in Splunk for Hell's Gate

