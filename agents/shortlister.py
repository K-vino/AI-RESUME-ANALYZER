# agents/shortlister.py

import re

class Shortlister:
    def __init__(self, threshold=70):
        self.threshold = threshold

    def compute_final_score(self, scores):
        return round(
            0.4 * scores.get("skills_match", 0) +
            0.3 * scores.get("experience_match", 0) +
            0.2 * scores.get("education_match", 0) +
            0.1 * scores.get("certifications_match", 0),
            2
        )

    def is_shortlisted(self, final_score, threshold=60.0):
        return final_score >= threshold

