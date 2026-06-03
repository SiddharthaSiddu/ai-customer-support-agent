import os
import sys

# Add the 'src' directory to the system path so Python knows where to find agent.py and tools.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent import run_customer_agent
import hooks

def test_scenarios():
    """
    Executes the exact evaluation prompts provided in your assignment blueprint.
    """
    
    # -----------------------------------------------------------------
    # Scenario 1: Basic validation, lookup, and normal policy resolution
    # -----------------------------------------------------------------
    print("\n" + "="*60)
    print("RUNNING SCENARIO 1: Identity verification and order check")
    print("="*60)
    prompt_1 = "Hi, it's Asha. My blender stopped working, I want a refund."
    run_customer_agent(prompt_1)
    
    
    # Resetting state variables cleanly between evaluation test runs
    hooks.IS_CUSTOMER_VERIFIED = False
    hooks.VERIFIED_CUSTOMER_ID = None

    
    # -----------------------------------------------------------------
    # Scenario 2: Multi-purchase returns with higher dollar value limit
    # -----------------------------------------------------------------
    print("\n" + "="*60)
    print("RUNNING SCENARIO 2: High value transaction escalation gate")
    print("="*60)
    # This scenario triggers the PostToolUse hook because a laptop refund is $1,200 (over our $1,000 threshold)
    prompt_2 = "Hi, it's Asha. I need to refund my $1,200 laptop."
    run_customer_agent(prompt_2)

if __name__ == "__main__":
    # Quick sanity check for your API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY environment variable is not set yet.")
        print("Set it in your terminal using: set ANTHROPIC_API_KEY=your_key_here\n")
        
    test_scenarios()