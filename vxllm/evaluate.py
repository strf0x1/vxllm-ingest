import os
import time
import json
import hashlib
from ragatouille import RAGPretrainedModel
import pymupdf4llm
from langchain.schema import Document
import argparse
import ollama
from bert_score import score
from vxllm.document_processing.loader import process_documents, generate_metadata

ollama_model = os.environ.get('OLLAMA_MODEL', 'mistral-nemo')
max_context = int(os.environ.get('MAX_CONTEXT', '2000'))

print(f"Ollama model: {ollama_model}")
print(f"Context length: {max_context}")


def calculate_bertscore(reference, hypothesis):
    P, R, F1 = score([hypothesis], [reference], lang='en', verbose=False)
    return P.item(), R.item(), F1.item()


def query_ollama(prompt, model, client=None):
    # start timer for Ollama response time
    start_time = time.time()
    if client:
        response = client.generate(model=model, prompt=prompt)
    else:
        response = ollama.generate(model=model, prompt=prompt)
    ollama_time_ms = (time.time() - start_time) * 1000  # Convert to milliseconds
    return response['response'], ollama_time_ms


def generate_qa_pairs_with_ollama(documents, num_pairs, model, client=None):
    qa_pairs = []
    prompt_template = """
Given the following document content, generate a question and answer pair that reflects important information from the text.

Document Content:
{content}

Please provide the output in the following format:

Question:
[Your question here]

Answer:
[Your answer here]
"""
    for doc in documents:
        content = doc.page_content.strip()
        # prepare the prompt for Ollama
        prompt = prompt_template.format(content=content)

        try:
            output, _ = query_ollama(prompt, model=model, client=client)
            output = output.strip()

            # parse the generated QA pair
            if "Question:" in output and "Answer:" in output:
                q_text = output.split("Question:")[1].split("Answer:")[0].strip()
                a_text = output.split("Answer:")[1].strip()
                qa_pairs.append({'query': q_text, 'ground_truth': a_text})
            else:
                print("Failed to parse QA pair from Ollama output.")
                print(output)  # print for debugging
        except Exception as e:
            print(f"Error generating QA pair: {str(e)}")

        # break the loop if we have enough qa pairs
        if len(qa_pairs) >= num_pairs:
            break

    return qa_pairs


def generate_answer_with_ollama(query, context, model="mistral-nemo", client=None):
    prompt_template = """You are an assistant helping with cybersecurity queries. When providing code examples, format them
as Markdown code blocks with the appropriate language specified for syntax highlighting.

Context:
{context}

Question:
{query}

Answer:"""

    prompt = prompt_template.format(context=context, query=query)

    try:
        output, _ = query_ollama(prompt, model=model, client=client)
        return output.strip()
    except Exception as e:
        print(f"Error generating answer with Ollama: {str(e)}")
        return ""


def evaluate_rag_system(rag, evaluation_dataset, docs_num=10, model="mistral-nemo", client=None, rerank_num=3):
    results = []
    for data in evaluation_dataset:
        query = data['query']
        ground_truth = data['ground_truth']

        # retrieve initial documents
        initial_docs = rag.search(query, k=docs_num)
        # extract document contents
        doc_contents = [doc['content'] for doc in initial_docs]

        reranked_docs = rag.rerank(query=query, documents=doc_contents, k=rerank_num)

        # extract document contents from reranked_docs
        reranked_doc_contents = [doc['content'] for doc in reranked_docs]

        # prepare prompt context from reranked document contents
        context = "\n".join(reranked_doc_contents)

        # generate response using Ollama
        generated_answer = generate_answer_with_ollama(query, context, model=model, client=client)

        # calculate BERTScore
        P, R, F1 = calculate_bertscore(ground_truth, generated_answer)

        # record the result
        results.append({
            'query': query,
            'ground_truth': ground_truth,
            'generated_answer': generated_answer,
            'bert_score_P': P,
            'bert_score_R': R,
            'bert_score_F1': F1
        })
    return results


def main():
    # --client allows remote Ollama server or separate container env
    parser = argparse.ArgumentParser(description="rag bertscore eval script")
    parser.add_argument("--client", help="Ollama client URL (e.g., https://1.2.3.4:11434)")
    parser.add_argument("--data", help="Directory path containing documents to process", default="data/")
    parser.add_argument("--qa-pairs", type=int, default=10, help="how many QA pairs you'd like to generate")
    parser.add_argument("--k", type=int, default=10, help="how many QA pairs you'd like to generate")
    parser.add_argument("--rerank", type=int, default=3, help="how many QA pairs you'd like to generate")
    args = parser.parse_args()

    ollama_client = None

    directory = args.data

    if args.client:
        ollama_client = ollama.Client(host=args.client)
        print(f"Connected to Ollama at {args.client}")
    else:
        ollama_client = None  # use default Ollama settings

    qa_pairs = args.qa_pairs
    docs_num = args.k
    rerank_num = args.rerank

    # process documents
    documents, processed_files, duplicate_files, processing_time = process_documents(directory)

    print(f"Number of unique files processed: {processed_files}")
    print(f"Number of duplicate files skipped: {duplicate_files}")
    print(f"Total processing time: {processing_time:.2f} seconds")
    print(f"Average time per file: {processing_time / (processed_files + duplicate_files):.2f} seconds")

    # extract text content and metadata from documents
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]

    rag = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")

    indexing_start_time = time.time()
    try:
        rag.index(
            collection=texts,
            document_metadatas=metadatas,
            index_name="document_collection",
            max_document_length=256,
            split_documents=True
        )
    except AssertionError as e:
        print(f"AssertionError during FAISS KMeans training: {e}")
    except Exception as e:
        print(f"Unexpected error during indexing: {e}")

    indexing_time = time.time() - indexing_start_time

    print(f"Indexing time: {indexing_time:.2f} seconds")
    print(f"Average time per unique document: {indexing_time / len(documents):.2f} seconds")

    total_time = processing_time + indexing_time
    print(f"Total ingestion time: {total_time:.2f} seconds")
    print(f"Average time per original document: {total_time / (processed_files + duplicate_files):.2f} seconds")

    print("Generating QA pairs using Ollama...")
    evaluation_dataset = generate_qa_pairs_with_ollama(documents, num_pairs=qa_pairs, model=ollama_model, client=ollama_client)

    with open('evaluation_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(evaluation_dataset, f, ensure_ascii=False, indent=4)

    print(f"Generated {len(evaluation_dataset)} QA pairs for evaluation.")

    print("Evaluating the RAG system...")
    results = evaluate_rag_system(rag, evaluation_dataset, docs_num=docs_num, model=ollama_model, client=ollama_client, rerank_num=rerank_num)

    # calculate average BERTScore F1
    f1_scores = [result['bert_score_F1'] for result in results if result['bert_score_F1'] is not None]
    average_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0

    # print results
    for result in results:
        print(f"Query: {result['query']}")
        print(f"Ground Truth: {result['ground_truth']}")
        print(f"Generated Answer: {result['generated_answer']}")
        print(f"BERTScore P: {result['bert_score_P']}")
        print(f"BERTScore R: {result['bert_score_R']}")
        print(f"BERTScore F1: {result['bert_score_F1']}\n")

    print(f"Average BERTScore F1: {average_f1}")


if __name__ == "__main__":
    main()
