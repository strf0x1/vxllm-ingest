from ragatouille import RAGPretrainedModel


class RAGIndexer:
    def __init__(self):
            self.rag = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")

    def index_documents(self, documents):
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        try:
            self.rag.index(
                collection=texts,
                document_metadatas=metadatas,
                index_name="document_collection",
                max_document_length=2000,  # this should be rare cases where med to large functions are returned
                split_documents=False    # now handled by text_splitter
            )
        except AssertionError as e:
            print(f"AssertionError during FAISS KMeans training: {e}")
        except Exception as e:
            print(f"Unexpected error during indexing: {e}")
