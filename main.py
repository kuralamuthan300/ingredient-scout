import ollama
import os
from dotenv import load_dotenv
import json
load_dotenv()

# Your Ollama Cloud API Key
API_KEY = os.getenv("OLLAMA_CLOUD_API_KEY")

# Initialize the client pointing to the Ollama Cloud endpoint
client = ollama.Client(
    host='https://ollama.com',
    headers={'Authorization': f'Bearer {API_KEY}'}
)

system_prompt = """Role: "Ingredient Scout"
Goal: Find ingredients for [Dish] for [Guests], scale quantities, and compare availability/pricing across Blinkit, Zepto, and BigBasket.

Operational Logic:
1. Scale: Determine exact ingredient names and quantities needed for the specified number of guests.
2. Search: Use all tools (Blinkit, Zepto, BigBasket) for every ingredient to ensure a full comparison.
3. Map: Match the 'required quantity' against 'available pack sizes' (e.g., if 200g is needed, find the closest 250g or 500g pack).
4. Consolidate: Compare prices per unit to find the best value across platforms.

Tools:
- get_product_details_blinkit(item: str)
- get_product_details_zepto(item: str)
- get_product_details_bigbasket(item: str)
- scrape_website(url: str)

Response Formats:
1. Tool Call: {"tool_name": "name", "tool_arguments": {"arg": "val"}}
2. Final Answer: {"answer": "A table or list showing: [Ingredient] | [Required Qty for X Guests] | [Blinkit Price/Availability] | [Zepto Price/Availability] | [BigBasket Price/Availability] | [Best Option]"}

Strict Rules:
- Output ONLY raw JSON. 
- No markdown code fences (```). 
- No conversational filler. 
- If a product is out of stock, mark as 'N/A'."""



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
            stream=False , 
        )

        print("Gemma 4 (Cloud): ", end="", flush=True)
        return response['message']['content']
            
    except Exception as e:
        print(f"\nAn error occurred: {e}")

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

# Example usage
if __name__ == "__main__":
    user_input = "do you have access to internet ? - what is temperature in bangalore kasvanahalli"
    # Call the function directly without asyncio.run
    call_gemma_cloud(user_input)