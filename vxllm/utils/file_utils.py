import os
import json
import hashlib


def load_meta_file(file_path):
    meta_file_path = f"{os.path.splitext(file_path)[0]}.meta"
    if os.path.exists(meta_file_path):
        with open(meta_file_path, 'r', encoding='utf-8') as meta_file:
            return json.load(meta_file)
    return {}


def compute_document_hash(document):
    return hashlib.md5(document.page_content.encode()).hexdigest()


def check_directory_empty(directory):
    if not os.path.exists(directory):
        raise FileNotFoundError(f"The specified directory does not exist: {directory}")
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"The specified path is not a directory: {directory}")
    if not os.listdir(directory):
        raise ValueError(f"The specified directory is empty: {directory}")