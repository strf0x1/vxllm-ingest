from ragatouille import RAGPretrainedModel


class RAGIndexer:
    def __init__(self):
        self.rag = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")

    def index_documents(self, documents):
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        try:
            # Set the maximum sequence length
            max_length = 512  # this is the default for many transformer models

            # truncate or pad the texts to the maximum length
            truncated_texts = [text[:max_length] for text in texts]

            self.rag.index(
                collection=truncated_texts,
                document_metadatas=metadatas,
                index_name="document_collection",
                max_document_length=max_length,
                split_documents=False
            )
        except AssertionError as e:
            print(f"AssertionError during FAISS KMeans training: {e}")
        except Exception as e:
            print(f"Unexpected error during indexing: {e}")
            raise  # Re-raise the exception for debugging purposes

