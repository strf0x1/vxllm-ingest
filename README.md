# vxllm

LLM's aren't often trained on hacking and redteam data, but they're great at systems knowledge and writing code. A RAG 
helps augment an LLM with new information it wasn't previously trained on. It can then blend the new information with its
existing knowledge to produce interesting results, especially if jailbroken:  
```bash

```
  
VX Underground is a wealth of information and they have a huge archive of papers and malware code examples,
but no search engine or way to semantically retrieve from this vast wealth of knowledge.
  
vxllm uses [ColBERTv2](https://arxiv.org/abs/2112.01488) for embedding, retrieval and reranking. The 
[Ragatouille](https://github.com/AnswerDotAI/RAGatouille) project makes implementation much simpler than the original project.

## installation
[mac](docs/mac.md)  
[linux](docs/linux.md)  

## usage
[usage](docs/usage.md)
  
## architecture explanation
[architecture](docs/architecture.md)
  
## evaluations
BERTScore evaluation:  

[evals](docs/evals.md)
