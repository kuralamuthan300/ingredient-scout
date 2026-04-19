import ollama
import os
from dotenv import load_dotenv

load_dotenv()

# Your Ollama Cloud API Key
API_KEY = os.getenv("OLLAMA_CLOUD_API_KEY")

# Initialize the client pointing to the Ollama Cloud endpoint
client = ollama.Client(
    host='https://ollama.com',
    headers={'Authorization': f'Bearer {API_KEY}'}
)

def call_gemma_cloud(prompt):
    try:
        # Requesting the cloud version of Gemma 4 31B
        # Removed 'await' here because client.chat is synchronous
        response = client.chat(
            model='gemma4:31b-cloud',
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
            stream=True, 
        )

        print("Gemma 4 (Cloud): ", end="", flush=True)
        for chunk in response:
            print(chunk['message']['content'], end="", flush=True)
            
    except Exception as e:
        print(f"\nAn error occurred: {e}")

# Example usage
if __name__ == "__main__":
    user_input = "say hello"
    # Call the function directly without asyncio.run
    call_gemma_cloud(user_input)