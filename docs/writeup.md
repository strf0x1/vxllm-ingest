# Writeup
Several RAG methods were evaluated based on the vx underground dataset. Due to the noisy nature of the data 
(e.g., PDFs, blog exports, PowerPoint presentations, and code), many RAG methods struggled to effectively retrieve 
relevant information. A significant reason for this is the challenge of handling diverse formats and extracting 
meaningful context, which can be lost during document chunking. Chunking strategies used in RAG can lead to a loss of 
context, especially when fixed chunk sizes are used without regard to semantic boundaries.  

ColBERT takes a different approach by representing documents at a more granular level, embedding each token in context 
using late interaction. Instead of embedding entire documents or fixed chunks, it allows for efficient semantic 
similarity comparison with user queries using MaxSim, which has shown to perform better than many 
traditional RAG methods in benchmarks, particularly in cases where retaining token-level contextual information is 
important.

Ideally, in RAG, you want to retrieve and use as much relevant information as possible. However, practical constraints 
arise due to the model's fixed context length and performance considerations. If you embed an entire document that is 
10,000 tokens, and later retrieve it to a model that has a maximum context length of 2,000 tokens, the data will be
truncated by 8,000 tokens, which could lead to the loss of important information. To mitigate this, tools like Ragatouille provide 
parameters such as max_document_length and split_documents to optimize the retrieval, ensuring that the most relevant 
parts of the document are accessible without exceeding limits.

```bash
 self.rag.index(
                collection=texts,
                document_metadatas=metadatas,
                index_name="document_collection",
                max_document_length=256,
                split_documents=True
            )
```
There is still the risk of losing context due to the document splitting and retrieval process, but this is a 
technological tradeoff where we compromise based on the capabilities of current models. One lever we can pull to 
mitigate this is to optimize the RAG retrieval and reranking functions.  
  
The search function is the initial query made after the user asks a question. It will search the ColBERTv2 
database and return x documents. By default, I use 10, but increasing this number can theoretically improve 
response quality because the model will have more contextual information to work with.
  
The reranking function takes the set of documents returned by the search function and reorders them based on 
their similarity to the user query, typically using token-level interactions to fine-tune the ranking. By 
setting the rerank to return 3 documents, we ensure that only the most relevant information reaches the next 
stage. Increasing the number of returned documents might improve the model's output quality by including more 
context, but this must be weighed against the model's fixed context length.
  
For example:
```bash
max_document_length=256
num_docs_returned=10
rerank_docs_returned=3
3 x 256 = 768 tokens
# for history retention, all tokens in the conversation have to be accounted for, so:
user_query=100 + reranked_docs=768 + model_response=2000 = 2868 tokens
```
One conversation turn can already exceed the default settings in Ollama. As context length increases 
with language model innovations, this will be less of a problem. For this reason, I think I would 
prefer a smaller parameter, quantized model for regular consumer hardware. However, if the chunks 
that you're getting back are highly relevant and all you need, you can get away with larger models 
as well.
  
There is another way we can optimize the results returned, but it has more to do with the types of docs 
we're ingesting. The VX Underground dataset contains several pure code examples or copies pf Github repos. 
These are pure code files, with little descriptive content besides a few comments. Let's take the  function 
**ExtractDataXML_BruteForce** in WDExtract, a utility in the VX Underground dataset that extracts the Windows Defender 
database:
```cpp
UINT ExtractDataXML_BruteForce(
    _In_ LPWSTR szCurrentDirectory,
    _In_ PVOID Container,
    _In_ LPCWSTR OpenElement,
    _In_ LPCWSTR CloseElement,
    _Out_ PULONG ExtractedChunks
)
{
    ULONG ctr = 0;
    
... *snip* ...

                }

                CurrentPosition++;
            }

        }
    }

    *ExtractedChunks = ctr;

    return ERROR_SUCCESS;
}
```
The token count using OpenAI's gpt4o estimator reports 2668 characters, or 576 tokens. If we keep the default
chunk size of 256 tokens, the code will be chopped in half. This will break some of the context we'd get with
the full code example. Traditional splitters are meant to split sentences or clusters of words semantically, 
not split code.
  
To solve this problem, I researched different splitting techniques for code and came across a 
[great blog post](https://docs.sweep.dev/blogs/chunking-2m-files). The idea is to use[tree-sitter](https://tree-sitter.github.io/tree-sitter/) to intelligently split by things like classes and 
functions. This is implemented in langchain's **RecursiveCharacterTextSplitter** using **Language** parsers:
```python
    code_splitter = RecursiveCharacterTextSplitter.from_language(
        language=code_language,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
```
[how to split code](https://python.langchain.com/docs/how_to/code_splitter/)
  
The effect is that our code is now split into more logical chunks preserving context. In the sweep.dev blog 
post, they also did an analysis of average function length in tokens and found the ideal size for med-large 
functions is around 1500, but for the average function, it's closer to <500. Testing on chunks of 1000 often broke
the embedding model, so I chose a max chunk of 500. In reality the chunks should be much smaller.
  
Traditionally, RAG's have a fixed chunk size, and on average keep the chunks somewhere between 100 - 500. This
is to reduce the performance impact of user queries. In this implementation, we don't have to worry about a few 
500 token chunks when the average for things like markdown files are still around 256.
  
There are several other improvements that could be made, but I haven't been researched thoroughly enough yet:
  * Data quality is really important, and I haven't cleaned the docs much yet. There are also several commercial pdf
parsers that would probably do a better job than pymupdf4llm that could do things like image to text parsing.
  * More robust testing - BERTScore and other similar tests are really insufficient for understanding how well
a more complex RAG performs in the real world. I'd like to mplement a testing suite with more advanced capabilities.
  * Hybrid Search - there are ways to combine the strengths of keyword-based search with contextual retrieval, 
or possibly use a graph database to enhance the query workflow.
  * RAG workflow - to keep performance reasonable, I kept my workflow simple, but a more robust workflow that
implements several Ollama queries to refine the results might help. For instance, people are not usually great
about asking questions on topics they're not well versed in. A workflow could be introduced to help the user
narrow in on what they really want to know.

