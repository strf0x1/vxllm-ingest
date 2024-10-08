import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document as LangchainDocument
from langchain.text_splitter import Language

# mapping of file extensions to languages for langchain
extension_to_language = {
    '.py': Language.PYTHON,
    '.md': Language.MARKDOWN,
    '.c': Language.C,
    '.cpp': Language.CPP,
    '.h': Language.CPP,
    '.go': Language.GO,
    '.rs': Language.RUST,
}


def split_document(document, chunk_size=256, chunk_overlap=0):
    _, ext = os.path.splitext(document.metadata['source'])
    ext = ext.lower()

    if ext in extension_to_language:
        return split_code_document(document, chunk_size, chunk_overlap)
    else:
        return split_text_document(document, chunk_size, chunk_overlap)


def split_text_document(document, chunk_size=256, chunk_overlap=0):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    splits = text_splitter.split_text(document.page_content)

    return [
        LangchainDocument(
            page_content=split,
            metadata={
                **document.metadata,
                "chunk_index": i,
                "total_chunks": len(splits)
            }
        )
        for i, split in enumerate(splits)
    ]


# Split code with tree-sitter syntax trees
# from: https://docs.sweep.dev/blogs/chunking-2m-files
# average chunk size of function < 500 tokens
def split_code_document(document, chunk_size=1000, chunk_overlap=0):
    _, ext = os.path.splitext(document.metadata['source'])
    ext = ext.lower()

    code_language = extension_to_language.get(ext)
    if not code_language:
        return split_text_document(document, chunk_size, chunk_overlap)

    code_splitter = RecursiveCharacterTextSplitter.from_language(
        language=code_language,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    splits = code_splitter.split_text(document.page_content)

    return [
        LangchainDocument(
            page_content=split,
            metadata={
                **document.metadata,
                "chunk_index": i,
                "total_chunks": len(splits),
                "is_code": True,
                "language": code_language.name
            }
        )
        for i, split in enumerate(splits)
    ]


def split_documents(documents, chunk_size=256, chunk_overlap=0):
    all_splits = []
    for doc in documents:
        all_splits.extend(split_document(doc, chunk_size, chunk_overlap))
    return all_splits
