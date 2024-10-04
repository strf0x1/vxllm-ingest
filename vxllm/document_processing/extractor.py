import pymupdf4llm


def extract_text_from_pdf(pdf_path):
    return pymupdf4llm.to_markdown(pdf_path)
