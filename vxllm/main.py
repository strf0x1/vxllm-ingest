import argparse
import time
import sys
from vxllm.document_processing.loader import process_documents, generate_metadata
from vxllm.indexing.rag_indexer import RAGIndexer
from vxllm.utils.file_utils import check_directory_exists


def main():
    print(f"Command line arguments: {sys.argv}")

    parser = argparse.ArgumentParser(description="Process and index documents.")
    parser.add_argument("--data", help="Directory path containing documents to process", default="data/")
    parser.add_argument("--metadata-enabled", action="store_true", help="Generate or regenerate metadata for documents")
    args = parser.parse_args()

    directory = args.data
    print(f"Using directory: {directory}")
    metadata_enabled = args.metadata_enabled
    print(f"Generate metadata: {metadata_enabled}")

    try:
        check_directory_exists(directory)
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        print(f"Error: {str(e)}")
        return


    documents, processed_files, duplicate_files, processing_time = process_documents(directory, should_generate_metadata=metadata_enabled)

    print(f"Number of unique files processed: {processed_files}")
    print(f"Number of duplicate files skipped: {duplicate_files}")
    print(f"Total processing time: {processing_time:.2f} seconds")
    print(f"Average time per file: {processing_time / (processed_files + duplicate_files):.2f} seconds")

    indexer = RAGIndexer()
    indexing_start_time = time.time()
    indexer.index_documents(documents)
    indexing_time = time.time() - indexing_start_time

    print(f"Indexing time: {indexing_time:.2f} seconds")
    print(f"Average time per unique document: {indexing_time / len(documents):.2f} seconds")

    total_time = processing_time + indexing_time
    print(f"Total ingestion time: {total_time:.2f} seconds")
    print(f"Average time per original document: {total_time / (processed_files + duplicate_files):.2f} seconds")


# debug poetry refactor
if __name__ == "__main__":
    print("Script is being run directly")
    main()
else:
    print(f"Script is being imported as a module: {__name__}")

