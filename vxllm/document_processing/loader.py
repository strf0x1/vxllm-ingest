import os
import time
import ollama
import json
from langchain.schema import Document
from .extractor import extract_text_from_pdf
from ..utils.file_utils import load_meta_file, compute_document_hash
import re

def strip_markdown_code_blocks(text):
    # markdown code blocks with optional json specifier
    pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return text

def load_document(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    elif ext == '.md':
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    elif ext == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif ext in ['.c', '.cpp', '.go']:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    metadata = {
        "source": file_path,
        "filepath": os.path.abspath(file_path)
    }

    meta_data = load_meta_file(file_path)
    metadata.update(meta_data)

    return Document(page_content=text, metadata=metadata)


def process_documents(directory, should_generate_metadata=False, model="gemma2:2b"):
    print("Processing documents...")
    supported_extensions = ['.txt', '.md', '.c', '.cpp', '.go', '.pdf']
    documents = []
    processed_files = 0
    duplicate_files = 0
    document_hashes = set()
    start_time = time.time()

    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in supported_extensions):
                file_path = os.path.join(root, file)
                try:
                    doc = load_document(file_path)

                    # generate metadata with ollama
                    if should_generate_metadata:
                        print(f"Processing {file_path}...")
                        metadata = generate_metadata(doc)
                        doc.metadata.update(metadata)
                        meta_file_path = f"{os.path.splitext(file_path)[0]}.meta"
                        with open(meta_file_path, 'w', encoding='utf-8') as meta_file:
                            json.dump(metadata, meta_file, indent=2)

                    # hashing for deduping documents
                    doc_hash = compute_document_hash(doc)
                    if doc_hash not in document_hashes:
                        documents.append(doc)
                        document_hashes.add(doc_hash)
                        processed_files += 1
                    else:
                        duplicate_files += 1
                        print(f"Duplicate found and skipped: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

    processing_time = time.time() - start_time
    return documents, processed_files, duplicate_files, processing_time


def generate_metadata(document, max_retries=4, model='gemma2:2b'):
    metadata_prompt = f"""
    Based on the following document, generate a JSON object with the following fields:
    1. title: Extract or generate a concise title for the document (string)
    2. slug: Create a very short summary of just a few words (string)
    3. desc: A 2-3 sentence description of overall content (string)
    4. tags: Include a list of relevant tags to help categorize the content (array of strings)
    5. urls: Include a list of any urls for reference (array of strings)

    Ensure that the JSON object strictly follows this structure:
    {{
        "title": "string",
        "slug": "string",
        "desc": "string",
        "tags": ["string", "string", ...],
        "urls": ["string", "string", ...]
    }}
    
    Document summary:
    {document.page_content[:1200]}

    Respond only with the valid JSON object, no additional text.
    """

    for attempt in range(max_retries):
        try:
            metadata_response = ollama.generate(model=model, prompt=metadata_prompt)
            metadata_str = metadata_response['response']
            # a lot of llms cant resist the urge to put json in md code blocks. have tried prompt engineering it away
            metadata_str = strip_markdown_code_blocks(metadata_str)
            print(f"metadata_str {metadata_str}")
            metadata = json.loads(metadata_str)

            # handle case of valid json returned, but schema does not conform
            if not all(key in metadata for key in ['title', 'slug', 'desc', 'tags', 'urls']):
                raise ValueError("Missing required fields in metadata")
            if not isinstance(metadata['tags'], list) or not isinstance(metadata['urls'], list):
                raise ValueError("'tags' and 'urls' must be lists")

            return metadata
        except json.JSONDecodeError:
            print(f"Attempt {attempt + 1}: Failed to parse JSON")
            print(metadata_str)
            if attempt < max_retries - 1:
                continue
        except Exception as e:
            print(f"Attempt {attempt + 1}: An error occurred: {str(e)}")
            if attempt < max_retries - 1:
                continue

    print(f"All {max_retries} attempts failed. Unable to generate valid metadata.")
    return None
