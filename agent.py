import ollama
import json
from config import API_KEY, system_prompt

# Initialize the client pointing to the Ollama Cloud endpoint
client = ollama.Client(
    host='https://ollama.com',
    headers={'Authorization': f'Bearer {API_KEY}'}
)

def call_gemma_cloud(prompt:str, available_tools:dict):
    try:
        # Requesting the cloud version of Gemma 4 31B
        response = client.chat(
            model='gemma4:31b-cloud',
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt,
                },
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
            stream=False,
        )

        return response['message']['content']
            
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        return None

def parse_llm_response(response_text: str) -> dict:
    """Parse the LLM's response, handling common formatting issues"""
    text = response_text.strip()
    
    # Remove markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (the fences)
        lines = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        text = "\n".join(lines).strip()
        # Remove language identifier (e.g., "json")
        if text.startswith("json"):
            text = text[4:].strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Last resort: try to find JSON in the response
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError(f"Could not parse LLM response: {text}")
