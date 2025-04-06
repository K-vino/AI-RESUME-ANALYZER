# agents/resume_extractor.py

from utils.pdf_utils import extract_text_from_pdf

class ResumeExtractor:
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file

    def get_resume_text(self):
        return extract_text_from_pdf(self.uploaded_file)
