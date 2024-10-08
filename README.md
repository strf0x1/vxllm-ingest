# vxllm

LLM's aren't often trained on hacking and redteam data, but they're great at systems knowledge and writing code. A RAG 
helps augment an LLM with new information that it wasn't previously trained on. It can then blend the new information with its
existing knowledge to produce interesting results.
  
VX Underground has a huge archive of papers and malware code examples, but no search engine.
  
vxllm uses [ColBERTv2](https://arxiv.org/abs/2112.01488) for embedding, retrieval and reranking. The 
[Ragatouille](https://github.com/AnswerDotAI/RAGatouille) project makes implementation much simpler than the original project.

## installation
[mac](docs/mac.md)  
[linux](docs/linux.md)  

## usage
[usage](docs/usage.md)
  
## architecture explanation
[architecture](docs/architecture.md)
  
## writeup
[writeup](docs/writeup.md)
  
## evaluations
BERTScore evaluation:  

[evals](docs/evals.md)
