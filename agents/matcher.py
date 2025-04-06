import json
from models.llm_client import LLMClient

class ResumeJDMatcher:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def match_resume_to_job(self, resume_text, job_description):
        if not resume_text or not job_description:
            raise ValueError("Both resume text and job description are required")

        prompt = f"""You are a resume matching assistant. Your task is to analyze how well a resume matches a job description and return a JSON response.

IMPORTANT: You must ONLY return a JSON object. No other text, explanations, or code blocks.

Resume to analyze:
{resume_text}

Job Description:
{job_description}

Return a single JSON object with these exact fields:
{{
    "skills_match": (number 0-100),
    "experience_match": (number 0-100),
    "education_match": (number 0-100),
    "certifications_match": (number 0-100),
    "summary": "Brief analysis of the match"
}}"""

        try:
            response = self.llm.generate_text(
                prompt,
                temperature=0.3
            )

            # Log raw response for debugging
            print(f"[DEBUG] Raw response: {response}")
            with open("llm_raw_output.txt", "w") as f:
                f.write(response)

            parsed = self._clean_and_parse_response(response)

            required_fields = ["skills_match", "experience_match", "education_match", "certifications_match", "summary"]
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")
                if field != "summary":
                    if not isinstance(parsed[field], (int, float)):
                        raise ValueError(f"Invalid value type for {field}: {parsed[field]}")
                    if parsed[field] < 0 or parsed[field] > 100:
                        raise ValueError(f"Score out of range for {field}: {parsed[field]}")

            return parsed

        except Exception as e:
            print(f"[ERROR] Matching failed: {str(e)}")
            return {
                "skills_match": 0,
                "experience_match": 0,
                "education_match": 0,
                "certifications_match": 0,
                "summary": f"Error during matching: {str(e)}"
            }

    def _clean_and_parse_response(self, response: str) -> dict:
        """Clean and parse the LLM response into a JSON object."""
        try:
            response = response.strip()

            # Remove known prefixes that LLM might include
            for prefix in ["Example:", "Response:", "Answer:", "Here's the JSON:"]:
                if response.startswith(prefix):
                    response = response[len(prefix):].strip()

            # Find the JSON object boundaries
            start_idx = response.find('{')
            end_idx = response.rfind('}')

            if start_idx == -1 or end_idx == -1:
                raise ValueError("No JSON object found in response")

            json_str = response[start_idx:end_idx + 1].strip()

            # Log the sanitized string before parsing
            print("[DEBUG] JSON to parse:", json_str)

            # Parse into dict
            result = json.loads(json_str)

            # Convert numeric fields safely
            for key in ["skills_match", "experience_match", "education_match", "certifications_match"]:
                if key in result:
                    try:
                        result[key] = float(result[key])
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid numeric value for {key}: {result[key]}")

            return result

        except Exception as e:
            raise ValueError(f"Failed to parse response: {str(e)}")
