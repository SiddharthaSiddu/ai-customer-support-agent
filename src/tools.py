import json

# =====================================================================
# 1. PYTHON TOOL FUNCTIONS (The implementation)
# =====================================================================

def get_customer(customer_name: str) -> str:
    """Simulates looking up a customer by name to get their profile and ID."""
    if "Asha" in customer_name:
        return json.dumps({"customer_id": "CUST-101", "name": "Asha", "status": "Verified"})
    return json.dumps({"error": f"Customer '{customer_name}' not found."})


def lookup_order(customer_id: str) -> str:
    """Simulates retrieving all historical orders for a verified customer ID."""
    if customer_id == "CUST-101":
        orders = [
            {"order_id": "ORD-901", "product": "Water Heater Premium", "date": "2025-05-10", "price": 450.00},
            {"order_id": "ORD-902", "product": "Water Heater Eco", "date": "2025-11-22", "price": 300.00},
            {"order_id": "ORD-903", "product": "Water Heater Eco", "date": "2026-02-15", "price": 300.00}
        ]
        return json.dumps({"customer_id": customer_id, "orders": orders})
    return json.dumps({"error": f"No orders found for customer ID {customer_id}."})


def process_refund(order_id: str, amount: float) -> str:
    """Simulates executing a refund transaction for a specific order."""
    return json.dumps({
        "status": "Success",
        "order_id": order_id,
        "refunded_amount": amount,
        "message": f"Refund of ${amount} processed successfully."
    })


def escalate_to_human(summary: str) -> str:
    """Hand-off mechanism when a human agent needs to step in."""
    return json.dumps({
        "status": "Escalated",
        "message": "Case transferred to a human representative.",
        "payload": summary
    })


# =====================================================================
# 2. ANTHROPIC TOOL SCHEMAS (What you pass to Claude)
# =====================================================================

TOOLS_SCHEMA = [
    {
        "name": "get_customer",
        "description": "Retrieves customer profile and unique customer_id based on a plain English name string. Always execute this tool first to resolve customer identification before attempting any account lookup or modifications.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "The full name of the customer mentioned in the prompt."
                }
            },
            "required": ["customer_name"]
        }
    },
    {
        "name": "lookup_order",
        "description": "Retrieves the historical purchase logs and order records matching a verified customer_id. Do not call this tool with a customer's name; it strictly requires a valid customer_id alphanumeric token.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The validated unique customer ID (e.g., CUST-101)."
                }
            },
            "required": ["customer_id"]
        }
    },
    {
        "name": "process_refund",
        "description": "Triggers financial reversal and processes a refund transaction back to the original payment method. Requires a specific order_id and the monetary numeric amount to refund.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The explicit target order ID token."},
                "amount": {"type": "number", "description": "The dollar value amount to be reversed."}
            },
            "required": ["order_id", "amount"]
        }
    },
    {
        "name": "escalate_to_human",
        "description": "Triggers an emergency workflow freeze and hands off the current context to a live customer service manager. Use this if a scenario cannot be auto-approved, exceeds a threshold, or encounters unresolvable complications.",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "A comprehensive, structured summary payload explaining the core issue and recommendation."
                }
            },
            "required": ["summary"]
        }
    }
]