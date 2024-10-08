import os
import time
import ollama
import json
from langchain.schema import Document
from .extractor import extract_text_from_pdf
from ..utils.file_utils import load_meta_file, compute_document_hash
from .text_splitter import split_documents, extension_to_language
import re


PLAIN_TEXT_EXTENSIONS = ['.txt', '.md']
SPECIALIZED_DOCUMENT_EXTENSIONS = ['.pdf']
CODE_FILE_EXTENSIONS = list(extension_to_language.keys())
SUPPORTED_EXTENSIONS = PLAIN_TEXT_EXTENSIONS + SPECIALIZED_DOCUMENT_EXTENSIONS + CODE_FILE_EXTENSIONS


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

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    if ext in PLAIN_TEXT_EXTENSIONS:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    elif ext in CODE_FILE_EXTENSIONS:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    elif ext in SPECIALIZED_DOCUMENT_EXTENSIONS:
        if ext == '.pdf':
            text = extract_text_from_pdf(file_path)
        else:
            raise NotImplementedError(f"Extraction for {ext} is not implemented yet")
    else:
        raise ValueError(f"Unexpected file type: {ext}")

    metadata = {
        "source": file_path,
        "filepath": os.path.abspath(file_path)
    }

    meta_data = load_meta_file(file_path)
    metadata.update(meta_data)

    return Document(page_content=text, metadata=metadata)


def process_documents(directory, should_generate_metadata=False, model="gemma2:2b", chunk_size=500, chunk_overlap=0):
    print("Processing documents...")
    documents = []
    processed_files = 0
    duplicate_files = 0
    document_hashes = set()
    start_time = time.time()

    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                file_path = os.path.join(root, file)
                try:
                    doc = load_document(file_path)
                    print(f"Doc {file_path} has a type of {type(doc)}")
                    doc_hash = compute_document_hash(doc.page_content)

                    if doc_hash not in document_hashes:
                        if should_generate_metadata:
                            print(f"Processing {file_path}...")
                            metadata = generate_metadata(doc)
                            doc.metadata.update(metadata)
                            meta_file_path = f"{os.path.splitext(file_path)[0]}.meta"
                            with open(meta_file_path, 'w', encoding='utf-8') as meta_file:
                                json.dump(metadata, meta_file, indent=2)

                        documents.append(doc)
                        document_hashes.add(doc_hash)
                        processed_files += 1
                    else:
                        duplicate_files += 1
                        print(f"Duplicate found and skipped: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

    # Split documents after processing
    split_docs = split_documents(documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    processing_time = time.time() - start_time
    return split_docs, processed_files, duplicate_files, processing_time


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
            metadata = json.loads(metadata_str)

            # handle case of valid json returned, but schema does not conform
            if not all(key in metadata for key in ['title', 'slug', 'desc', 'tags', 'urls']):
                raise ValueError("Missing required fields in metadata")
            if not isinstance(metadata['tags'], list) or not isinstance(metadata['urls'], list):
                raise ValueError("'tags' and 'urls' must be lists")

            return metadata
        except json.JSONDecodeError:
            print(f"Attempt {attempt + 1}: Failed to parse JSON")
            if attempt < max_retries - 1:
                continue
        except Exception as e:
            print(f"Attempt {attempt + 1}: An error occurred: {str(e)}")
            if attempt < max_retries - 1:
                continue

    print(f"All {max_retries} attempts failed. Unable to generate valid metadata.")
    return None
