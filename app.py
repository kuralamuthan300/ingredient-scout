import gradio as gr
import json
from main import call_gemma_cloud, parse_llm_response
from tools import tools as available_tools

def process_agent_step(user_input, state):
    history = state.get("history", {})
    num = state.get("num", 1)
    status = state.get("status", "idle")
    thinking_log = state.get("thinking_log", "")
    
    if not user_input.strip():
        yield state, thinking_log, {"error": "Empty input."}, user_input
        return

    if status == "idle" or status == "completed" or status == "error":
        history = {'conversation_1': user_input}
        num = 1
        thinking_log = ""
        status = "running"
        yield {"history": history, "num": num, "status": status, "thinking_log": thinking_log}, thinking_log, {"status": "Starting up..."}, ""
    elif status == "waiting_for_user":
        num += 1
        history[f'conversation_{num}'] = json.dumps({"result": user_input})
        status = "running"
        thinking_log += f"👤 User replied: {user_input}\n\n"
        yield {"history": history, "num": num, "status": status, "thinking_log": thinking_log}, thinking_log, {"status": "Resuming..."}, ""
    
    state = {"history": history, "num": num, "status": status, "thinking_log": thinking_log}
    
    while state["status"] == "running":
        raw_response = call_gemma_cloud(str(state["history"]), available_tools)
        if not raw_response:
            state["thinking_log"] += "\nError: Received no response from model."
            state["status"] = "error"
            yield state, state["thinking_log"], {"error": "No response"}, ""
            break
            
        try:
            llm_response = parse_llm_response(raw_response)
        except Exception as e:
            state["thinking_log"] += f"\nError parsing response: {e}\nRaw: {raw_response}"
            state["status"] = "error"
            yield state, state["thinking_log"], {"error": "Parse error"}, ""
            break
            
        if "thinking" in llm_response:
            state["thinking_log"] += f"🤔 Thinking:\n{llm_response['thinking']}\n\n"
            
        yield state, state["thinking_log"], {"status": "Thinking..."}, ""
        
        if llm_response.get('continue') == False:
            state["status"] = "completed"
            yield state, state["thinking_log"], llm_response, ""
            break
            
        if "action" in llm_response:
            tool_name = llm_response['action'].get('tool')
            params = llm_response['action'].get('params', {})
            
            # Format params for logging
            params_str = ", ".join([f"{k}={v}" for k, v in params.items()])
            
            state["thinking_log"] += f"🛠️ Using Tool: {tool_name}\n   Arguments: {params_str}\n\n"
            yield state, state["thinking_log"], {"status": f"Running {tool_name}..."}, ""
            
            if tool_name == "get_more_info_from_user":
                state["status"] = "waiting_for_user"
                query_text = params.get('query', params.get('arg', 'Please provide more info.'))
                state["thinking_log"] += f"❓ Agent asks: {query_text}\n👉 Please type your reply in the text box and click 'Submit / Reply'.\n\n"
                yield state, state["thinking_log"], {"status": "Waiting for user input..."}, ""
                return
            
            state["num"] += 1
            if tool_name in available_tools:
                try:
                    tool_response = available_tools[tool_name](**params)
                except Exception as e:
                    tool_response = json.dumps({"error": str(e)})
            else:
                tool_response = json.dumps({"error": f"Tool {tool_name} not found."})
                
            state["thinking_log"] += f"📥 Received tool response.\n\n"
            state["history"][f'conversation_{state["num"]}'] = tool_response
            yield state, state["thinking_log"], {"status": "Processing tool response..."}, ""
        else:
            state["thinking_log"] += "⚠️ Unexpected model response format.\n\n"
            state["status"] = "error"
            yield state, state["thinking_log"], {"error": "Unexpected format", "raw": llm_response}, ""
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
    
    agent_state = gr.State({"history": {}, "num": 1, "status": "idle", "thinking_log": ""})
    
    with gr.Row():
        with gr.Column(scale=1):
            user_input = gr.Textbox(
                label="What do you want to cook? (Or type your reply here)",
                placeholder="e.g. Pasta for 2 guests\ne.g. Yes, make it spicy",
                lines=3
            )
            submit_btn = gr.Button("Submit / Reply", variant="primary")
            
        with gr.Column(scale=2):
            thinking_box = gr.Textbox(label="Agent's Thoughts & Actions", lines=15, interactive=False)
            final_answer_box = gr.JSON(label="Final Answer")

    submit_btn.click(
        fn=process_agent_step,
        inputs=[user_input, agent_state],
        outputs=[agent_state, thinking_box, final_answer_box, user_input]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, css=css, theme=gr.themes.Base())
