# Architecture
There is a data processing pipeline, which handles classifying the type of doc and its processor, and a splitting/embedding
process that prepares the data for ingestion into the database.

![ingestion](images/ingest.png)
  
During the user search, the cli tool will retrieve x amount of documents, then it uses a reranker to provide the best docs
to Ollama. A query is rendered for Ollama that contains the docs, the user query, and a prompt instructing Ollama to 
synthesize its own data with the provided data when responding.

![search](images/user_search.png)
  
Colbert works differently than tradition RAG methods that use naive chunking. Naive chunking uses a combination of 
splitting + chunking to break up the documents before ingesting them into a vector database.
