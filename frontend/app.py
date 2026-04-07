import os
import time
import pandas as pd
import gradio as gr
import numpy as np
from openai import OpenAI  # <--- New Import

# --- META LLM PROXY SETUP ---
# These environment variables are automatically injected by the Meta Grader
client = OpenAI(
    base_url=os.environ.get("API_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.environ.get("API_KEY", "dummy-key")
)

def get_llm_decision(obs):
    """Consults the Meta LLM Proxy to decide which SRE action to take."""
    try:
        prompt = f"System State: Error Rate {obs[0]}%, Latency {obs[1]}ms. " \
                 "Choose action: 0 (Database Fix), 1 (Scaling), or 2 (Rollback). " \
                 "Return ONLY the number."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Standard model for the proxy
            messages=[{"role": "user", "content": prompt}],
            timeout=5.0
        )
        # Extract the number from the response
        decision = response.choices[0].message.content
        return int(''.join(filter(str.isdigit, decision)) or 0)
    except Exception as e:
        print(f"Proxy Error: {e}")
        return 0 # Fallback to safety

# --- Update your handle_step function to use the LLM ---
def handle_step(action_id=None):
    global log_history
    obs, _ = env.get_state()
    
    # If no manual action_id is provided, ask the LLM
    if action_id is None:
        action_to_take, _, _ = get_llm_decision(obs)
    else:
        action_to_take = int(action_id)
        
    obs, reward, term, trunc, info = env.step(action_to_take)
    # ... rest of your UI update logic remains the same ...
