# models/llm_client.py

from huggingface_hub import InferenceClient

class LLMClient:
    def __init__(self, api_key: str, model_name: str = "google/gemma-7b"):
        if not api_key:
            raise ValueError("API key is required")
            
        self.client = InferenceClient(
            model=model_name,
            token=api_key
        )

    def generate_text(self, prompt: str, max_tokens: int = 300, temperature: float = 0.7) -> str:
        """Generate text using the Hugging Face model.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for sampling (higher = more random)
            
        Returns:
            str: The generated text response
        """
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                return_full_text=False  # Only return the generated text, not the prompt
            )
            
            # Handle the response based on its type
            if hasattr(response, 'generated_text'):
                # It's a TextGenerationResponse object
                generated_text = response.generated_text
            elif isinstance(response, str):
                # It's already a string
                generated_text = response
            else:
                # Try to convert to string as fallback
                generated_text = str(response)
                
            if not generated_text:
                raise ValueError("Empty response from LLM API")
                
            return generated_text.strip()
            
        except Exception as e:
            raise RuntimeError(f"LLM API error: {str(e)}")
