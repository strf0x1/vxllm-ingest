# Evaluation

Due to the complex nature of the dataset, BERTScore seemed like the appropriate evaluation method. It has better semantic 
comparison and can detect paraphrasing. It also uses BERT for semantic comparison, so meshes well with ColBERTv2.
  
The eval script can take a long time because it ingests the data and generates the qa pairs all in one shot for consistency. To run:
```bash
poetry run evaluate
```
By default, it will generate and evaluate against 10 QA pairs. This is good for a quick test, but a couple hundred will 
be more accurate:
```bash
poetry run evaluate --qa-pairs 200
```
  
You can tweak number of docs and rerank docs returned:
```bash
poetry run evaluate --qa-pairs 10 --k 20 --rerank 3
```
Just remember that your rerank docs returned affect context limit:
  * 3  docs x 256(chunks) = 768 tokens
  * 10 docs x 256(chunks) = 2560 tokens
  * 20 docs x 256(chunks) = 5120 tokens
  * 30 docs x 256(chunks) = 7680 tokens
  
Evals of different models + settings with the VX Underground dataset:

| Model | Context | QA Pairs | k | Rerank | Average BERTScore F1 |
|-------|---------|----------|---|--------|----------------------|
| gemma2 2b | 8096 | 200 | 10 | 3 | 0.8539141273498535 |
| gemma2 2b | 8096 | 200 | 20 | 10 | 0.8524665939807892 |
| mistral-nemo 12b | 8096 | 200 | 10 | 3 | 0.8378271526098251 |
| mistral-nemo 12b | 8096 | 200 | 20 | 10 | 0.8410642120242119 |
| qwen-2.5-coder 7b | 8096 | 200 | 10 | 3 | 0.8369064947962761 |
| qwen-2.5-coder 7b | 8096 | 200 | 20 | 10 | 0.841939592063427 |

What's interesting is that gemma2:2b is achieving slightly better scores than the 12b mistral-nemo. This might have to
do with gemma2's strength in summarization, which comes down to model purpose and training. Mistral-nemo is the better
overall coder.
  
As someone deeply interested in malware development, the responses from mistral-nemo did seem subjectively higher quality.
For example, mistral-nemo would seem to prefer writing detailed code responses, while gemma2 would tend to summarize more. 
This isn't something BERTScore really evaluates, so some sort of custom evaluation targeting code development might be 
needed to test this.
  
## References:
[BERTScore in 5 Minues](https://medium.com/@abonia/bertscore-explained-in-5-minutes-0b98553bfb71)


