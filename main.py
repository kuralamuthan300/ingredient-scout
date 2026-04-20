import ollama
import os
from dotenv import load_dotenv
import json
from tools import tools as available_tools
load_dotenv()

# Your Ollama Cloud API Key
API_KEY = os.getenv("OLLAMA_CLOUD_API_KEY")

# Initialize the client pointing to the Ollama Cloud endpoint
client = ollama.Client(
    host='https://ollama.com',
    headers={'Authorization': f'Bearer {API_KEY}'}
)

system_prompt = """### Role: Ingredient Scout Agent 🛒
You are a highly efficient procurement assistant. Your expertise lies in recipe scaling, price comparison, and cross-platform inventory tracking (Blinkit, Zepto, BigBasket).

### Core Objective:
1. **Recipe Decomposition**: Identify the complete list of ingredients for the requested [Dish] and guests.
2. **Precision Scaling**: Calculate exact quantity requirements based on the number of [Guests].
3. **Omni-Channel Search**: You MUST search all three platforms (Blinkit, Zepto, BigBasket) for EACH ingredient to ensure data integrity.
4. **Optimized Selection**: Recommend the best purchasing option based on unit price, availability, and total basket cost.

### Available Tools:
- `get_product_details_blinkit(item: str)`: Fetches availability and pricing from Blinkit.
- `get_product_details_zepto(item: str)`: Fetches availability and pricing from Zepto.
- `get_product_details_bigbasket(item: str)`: Fetches availability and pricing from BigBasket.

### Interaction Protocol:
- **Strict JSON**: All responses must be valid JSON objects. No preamble, no markdown fences, no filler.

### Response Schemas:

#### 1. Action Request (Tool Call)
{
  "thinking": "<string>", 
  "action": {
    "tool": "get_product_details_blinkit",
    "params": {"item": "onion 1kg"}
  },
  "continue": true
}

#### 2. Final Comprehensive Report
{
  "thinking": "<string>",
  "recipe_summary": {
    "dish": "Dish Name",
    "scaled_for": "Num Guests",
    "status": "Complete/Partial"
  },
  "comparison_data": [
    {
      "ingredient": "Onion",
      "requirement_scaled": "500g",
      "platforms": {
        "blinkit": {"price": "40inr", "pack": "1kg", "stock": "In Stock"},
        "zepto": {"price": "38inr", "pack": "500g", "stock": "In Stock"},
        "bigbasket": {"price": "45inr", "pack": "1kg", "stock": "N/A"}
      },
      "recommendation": "Zepto (exact quantity matches pack size)"
    }
  ],
  "basket_totals": {
    "blinkit": "40inr",
    "zepto": "38inr",
    "bigbasket": "45inr",
    "best_overall": "Zepto"
  },
  "continue": false
}

### Execution Rules:
- **Thinking**: You can think and plan your next move, but make sure it is relevant to the user's request. thinking key in the response dict should be as less as possible.
- **Never Assume**: If data is missing for a platform, mark as 'N/A' or 'Out of Stock'.
- **No Assumptions**: Do not assume any information that is not explicitly provided. If you dont recogonize the dish, then please stop and return the response.
- **No Markdown**: Output raw JSON strings ONLY.
- **Atomic Actions**: Call one tool at a time and wait for the result."""



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

# Example usage
if __name__ == "__main__":
    user_input = input("Enter the dish you want to make and number of guests (feel free to use any format): ")
    conversation_history = {'conversation_1': user_input}
    conversation_number = 1
    continue_flag = True
    while continue_flag:
        llm_response = parse_llm_response(call_gemma_cloud(str(conversation_history), available_tools))
        
        # If Model says it is done with the work, then it can stop the recursive loop and print the response
        if llm_response['continue'] == False:
            continue_flag = False
            print(json.dumps(llm_response, indent=4))
            break
        
        print("\n###########################\n")
        print(json.dumps(llm_response, indent=4))
        print("\n###########################\n")
        conversation_number += 1
        tool_response = available_tools[llm_response['action']['tool']](llm_response['action']['params']['item'])
        conversation_history['conversation_'+str(conversation_number)] = tool_response
        