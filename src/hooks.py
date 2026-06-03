import json

# Global simulation state to track whether identity verification has happened
# (This fulfills Step 3's programmatic identity enforcement)
IS_CUSTOMER_VERIFIED = False
VERIFIED_CUSTOMER_ID = None

def check_prerequisite_gate(tool_name: str) -> tuple[bool, str]:
    """
    Step 3: Programmatic Prerequisite Gate.
    Blocks monetary/sensitive tools from running until identity is verified.
    """
    global IS_CUSTOMER_VERIFIED
    
    # Define which tools are protected behind the identity gate
    protected_tools = ["lookup_order", "process_refund"]
    
    if tool_name in protected_tools and not IS_CUSTOMER_VERIFIED:
        # Programmatically reject the tool call with a clear instruction message
        error_payload = {
            "status": "Rejected",
            "error_type": "PreRequisiteViolation",
            "message": "Access Denied. You must explicitly verify the customer's identity using 'get_customer' before using this tool."
        }
        return False, json.dumps(error_payload)
    
    return True, ""


def run_post_tool_hook(tool_name: str, tool_input: dict, current_output: str) -> str:
    """
    Step 4: PostToolUse Hook.
    Automatically intercepts tool executions to catch high-value refunds 
    and override them to human escalation.
    """
    # Look closely at process_refund operations
    if tool_name == "process_refund":
        amount = tool_input.get("amount", 0)
        
        # Intercept any refund above the set business limit threshold (e.g., $1000)
        if amount > 1000:
            print(f"\n⚠️ [Security Hook Action]: Refund of ${amount} exceeds the auto-approve limit!")
            
            # Formulate the Step 7 Clean Escalation Summary automatically
            escalation_summary = (
                f"CRITICAL ESCALATION SUMMARY:\n"
                f"- Customer ID: {tool_input.get('customer_id', 'UNKNOWN')}\n"
                f"- Core Problem: High-value refund request requires manual auditing.\n"
                f"- Request Amount: ${amount}\n"
                f"- Recommended Action: Human agent to manually verify original receipt and issue approval."
            )
            
            # Hard override the output to a human escalation payload
            override_payload = {
                "status": "Escalated",
                "message": "This refund exceeds auto-approval limits. Intercepted and routed to a supervisor.",
                "escalation_summary": escalation_summary
            }
            return json.dumps(override_payload)
            
    return current_output