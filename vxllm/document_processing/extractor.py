import pymupdf4llm


def extract_text_from_pdf(pdf_path):
    md_text = pymupdf4llm.to_markdown(pdf_path)
    return md_text
