# utils/pdf_utils.py

import PyPDF2

def extract_text_from_pdf(uploaded_file):
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        resume_text = " ".join(
            [page.extract_text() for page in reader.pages if page.extract_text()]
        )
        return resume_text.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to extract PDF text: {e}")
