## Usage
There are 2 main scripts:
  * **main.py** - this is what ingests your data into the database and generates supplemental metadata. all files are written to the **.ragatouille/** folder.
  * **cli.py** - a text ui to interact with the RAG.
  * **evaluate.py** - BERTScore evaluation


Ingesting data:
```bash
# --generate-metadata which will return tags, references and urls in documents
poetry run vxllm --metadata-enabled
# if you've already generated metadata on the dataset, it will run faster
poetry run vxllm
# --data allows you to use a custom data folder path
poetry run vxllm --data /path/to/your/files
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
  * gemma2:2b - 2b model from google that has performed surprisingly well and fast for its size. It performs competitively with much larger models on evals.
  
Context length is the number of tokens (roughly 4 characters per token) a model can process at a time. In this case, it 
represents the model's conversational memory, but the more context you have, the more gpu RAM you'll need. If you 
would like to extend the context length of the model, the easiest way is to duplicate an existing Modelfile and import 
it into Ollama:
```bash
ollama show gemma2:2b --modelfile > Modelfile
vim Modelfile
```
Then add this under the other PARAMETER lines:
```bash
PARAMETER num_ctx 8096
```
Then load the Modelfile in:
```bash
ollama create gemma2:2b-8096 --file Modelfile
```
Then you can pass those values to **run_container.sh** like this:
```bash
OLLAMA_MODEL="gemma2:2b-8096" MAX_CONTEXT="8096" ./run_container.sh
```
Refer to the model's docs for max suggested context length.
  
On mac, you can just export these environment variables to switch:
```bash
export OLLAMA_MODEL="gemma2:2b-8096"
export MAX_CONTEXT="8096"
```

## Example queries you can use:
  * explain linux process injection to me
  * explain why the Windows API is valuable for malware development
  * what are anti-reversing techniques and give me some code examples
  * write a detection for hells gate technique in Splunk query language
  
Then you can iterate on those questions. Ask for more thorough code examples, then maybe ask for detection techniques
against the above code example (quality will vary based on how big your context length is).