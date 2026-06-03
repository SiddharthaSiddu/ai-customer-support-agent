import os
import json
from anthropic import Anthropic
# Import tool schemas and functions
from tools import TOOLS_SCHEMA, get_customer, lookup_order, process_refund, escalate_to_human
# Import our security guardrails and verification state variables
import hooks

client = Anthropic()

def run_customer_agent(user_message: str):
    print(f"\n[User]: {user_message}")
    
    # Initialize session conversational history array
    messages = [
        {"role": "user", "content": user_message}
    ]
    
    while True:
        # Call the Anthropic Claude Model
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system="You are an advanced customer support AI assistant. Help the customer resolve their query using available tools dynamically.",
            tools=TOOLS_SCHEMA,
            messages=messages
        )
        
        stop_reason = response.stop_reason
        
        # Scenario A: Claude wants to use a tool
        if stop_reason == "tool_use":
            tool_use_block = next(block for block in response.content if block.type == "tool_use")
            tool_name = tool_use_block.name
            tool_input = tool_use_block.input
            tool_use_id = tool_use_block.id
            
            print(f"\n🤖 [Agent Intent]: Wants to call tool '{tool_name}' with parameters: {tool_input}")
            
            # --- GUARDRAIL HOOKS INTEGRATION ---
            # Step 3: Run the Programmatic Prerequisite Gate Check
            is_allowed, gate_message = hooks.check_prerequisite_gate(tool_name)
            
            if not is_allowed:
                print(f"🛑 [Gate Blocked]: Code strictly rejected the execution of '{tool_name}' due to missing verification.")
                tool_result = gate_message
            else:
                # If it passes the gate, try executing the tool safely
                try:
                    raw_output = ""
                    if tool_name == "get_customer":
                        raw_output = get_customer(tool_input.get("customer_name"))
                        # If a customer profile is fetched successfully, mark them verified in our state
                        if "customer_id" in raw_output:
                            hooks.IS_CUSTOMER_VERIFIED = True
                            hooks.VERIFIED_CUSTOMER_ID = json.loads(raw_output).get("customer_id")
                            
                    elif tool_name == "lookup_order":
                        raw_output = lookup_order(tool_input.get("customer_id"))
                        
                    elif tool_name == "process_refund":
                        raw_output = process_refund(tool_input.get("order_id"), tool_input.get("amount"))
                        
                    elif tool_name == "escalate_to_human":
                        raw_output = escalate_to_human(tool_input.get("summary"))
                    
                    # Step 4 & 7: Run PostToolUse Hook to intercept high refunds or change outputs
                    tool_result = hooks.run_post_tool_hook(tool_name, tool_input, raw_output)
                    
                except Exception as e:
                    # Step 5: Add Structured Error Responses for robustness instead of crashing
                    print(f"💥 [Error caught]: {str(e)}")
                    error_payload = {
                        "category": "transient",
                        "isRetryable": True,
                        "message": f"A temporary system error occurred while processing tool '{tool_name}'. Please retry operation."
                    }
                    tool_result = json.dumps(error_payload)
            
            print(f"⚙️ [Final Tool Output provided to Agent]: {tool_result}")
            
            # Append the agent's action and the tool results to history
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": tool_result
                    }
                ]
            })
            
            # Continue the loop back to Claude
            continue
            
        # Scenario B: Claude is completely finished and replies to the user
        elif stop_reason == "end_turn":
            final_text = response.content[0].text
            print(f"\n[Agent Final Reply]: {final_text}")
            break