# Evaluation

Due to the complex nature of the dataset, BERTScore seemed like to appropriate evaluation method. It has better semantic 
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
  
You can tweak number of docs returned and rerank returned:
```bash
poetry run evaluate --qa-pairs 10 --k 20 --rerank 3
```
  
Here's an example score using the VX Underground dataset with 200 QA pairs:
  
```bash
Average BERTScore F1: 0.8424883899092674
```

## References:
[BERTScore in 5 Minues](https://medium.com/@abonia/bertscore-explained-in-5-minutes-0b98553bfb71)
  



