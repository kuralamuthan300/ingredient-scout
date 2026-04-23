import json
from tools import tools as available_tools
from agent import call_gemma_cloud, parse_llm_response

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
        tool_response = available_tools[llm_response['action']['tool']](**llm_response['action']['params'])
        conversation_history['conversation_'+str(conversation_number)] = tool_response
        