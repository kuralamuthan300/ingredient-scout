import gradio as gr
import json
from main import call_gemma_cloud, parse_llm_response
from tools import tools as available_tools

# Override get_more_info_from_user to prevent it from blocking the terminal with input()
def get_more_info_from_user_gradio(arg: str):
    return json.dumps({"result": "Please make your best assumption based on the user's initial input."})

available_tools["get_more_info_from_user"] = get_more_info_from_user_gradio

def run_agent(user_input):
    if not user_input.strip():
        yield "Please enter a valid request.", {"error": "Empty input."}
        return

    conversation_history = {'conversation_1': user_input}
    conversation_number = 1
    
    thinking_log = ""
    yield thinking_log, {"status": "Starting up..."}

    continue_flag = True
    while continue_flag:
        raw_response = call_gemma_cloud(str(conversation_history), available_tools)
        if not raw_response:
            yield thinking_log + "\nError: Received no response from model.", {"error": "No response"}
            break
            
        try:
            llm_response = parse_llm_response(raw_response)
        except Exception as e:
            yield thinking_log + f"\nError parsing response: {e}\nRaw: {raw_response}", {"error": "Parse error"}
            break
            
        if "thinking" in llm_response:
            thinking_log += f"🤔 Thinking:\n{llm_response['thinking']}\n\n"
            
        yield thinking_log, {"status": "Thinking..."}
        
        if llm_response.get('continue') == False:
            continue_flag = False
            yield thinking_log, llm_response
            break
            
        if "action" in llm_response:
            tool_name = llm_response['action'].get('tool')
            params = llm_response['action'].get('params', {})
            tool_arg = params.get('arg', '')
            
            thinking_log += f"🛠️ Using Tool: {tool_name}\n   Argument: {tool_arg}\n\n"
            yield thinking_log, {"status": f"Running {tool_name}..."}
            
            conversation_number += 1
            if tool_name in available_tools:
                try:
                    tool_response = available_tools[tool_name](tool_arg)
                except Exception as e:
                    tool_response = json.dumps({"error": str(e)})
            else:
                tool_response = json.dumps({"error": f"Tool {tool_name} not found."})
                
            thinking_log += f"📥 Received tool response.\n\n"
            conversation_history['conversation_'+str(conversation_number)] = tool_response
            yield thinking_log, {"status": "Processing tool response..."}
        else:
            thinking_log += "⚠️ Unexpected model response format.\n\n"
            yield thinking_log, {"error": "Unexpected format", "raw": llm_response}
            break

css = """
body, .gradio-container {
    background-color: #ffffff !important;
}
.stylized-title {
    font-family: 'Pacifico', 'Brush Script MT', 'Comic Sans MS', cursive !important;
    text-align: center;
    font-size: 3.5rem;
    color: #111;
    padding-top: 30px;
    margin-bottom: 20px;
}
"""

with gr.Blocks() as demo:
    gr.HTML("<h1 class='stylized-title'>Ingredient Scout</h1>")
    
    with gr.Row():
        with gr.Column(scale=1):
            user_input = gr.Textbox(
                label="What do you want to cook?",
                placeholder="e.g. Pasta for 2 guests",
                lines=3
            )
            submit_btn = gr.Button("Scout Ingredients", variant="primary")
            
        with gr.Column(scale=2):
            thinking_box = gr.Textbox(label="Agent's Thoughts & Actions", lines=15, interactive=False)
            final_answer_box = gr.JSON(label="Final Answer")

    submit_btn.click(
        fn=run_agent,
        inputs=[user_input],
        outputs=[thinking_box, final_answer_box]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, css=css, theme=gr.themes.Base())
