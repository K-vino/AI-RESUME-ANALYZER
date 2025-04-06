# agents/jd_summarizer.py

class JobDescriptionSummarizer:
    def __init__(self, job_description: str):
        self.job_description = job_description

    def get_summary(self):
        # Placeholder: In future, use LLM to generate a true summary
        return self.job_description.strip()
