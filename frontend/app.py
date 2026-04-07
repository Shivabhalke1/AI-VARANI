import os
import time
import pandas as pd
import gradio as gr
import numpy as np
from openai import OpenAI
from openenv_incident.env import IncidentEnv

# --- Path Bridge ---
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Meta LLM Proxy Setup ---
client = OpenAI(
    base_url=os.environ.get("API_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.environ.get("API_KEY", "dummy-key")
)

# Initialize Backend
try:
    env = IncidentEnv(config_path="configs/env_config.yaml")
except Exception as e:
    print(f"Error: {e}")
    class MockEnv:
        def get_state(self): return np.array([0.0, 0.0, 0.0]), {}
        def reset(self, seed=None, options=None): return np.array([10.0, 300.0, 1.0]), {}
        def step(self, a): return np.array([0.5, 95.0, 0.0]), 1.0, False, False, {}
    env = MockEnv()

log_history = []

def get_llm_decision(obs):
    try:
        prompt = f"State: Error {obs[0]}%, Latency {obs[1]}ms. Return only action index 0, 1, or 2."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            timeout=5.0
        )
        decision = response.choices[0].message.content
        return int(''.join(filter(str.isdigit, decision)) or 0)
    except:
        return 0

def handle_reset():
    global log_history
    obs, _ = env.reset()
    log_history = [f"[{time.strftime('%H:%M:%S')}] 🚀 System Reset."]
    return *update_ui_components(), "\n".join(log_history)

def handle_step(action_id=None):
    global log_history
    obs, _ = env.get_state()
    action_to_take = int(action_id) if action_id is not None else get_llm_decision(obs)
    
    obs, reward, _, _, _ = env.step(action_to_take)
    err, lat, deg, table, _, _ = update_ui_components()
    log_history.insert(0, f"[{time.strftime('%H:%M:%S')}] 🛠️ Action {action_to_take} applied. Reward: {reward}")
    return err, lat, deg, table, "### Analysis Updated", "Action Processed", "\n".join(log_history)

def update_ui_components():
    obs, _ = env.get_state()
    error_rate = float(obs[0])
    health_data = [{"Service": "API", "Status": "Active", "Latency": f"{int(obs[1])}ms"}]
    table_html = pd.DataFrame(health_data).to_html(classes='table', index=False, border=0)
    return round(error_rate, 2), round(float(obs[1]), 2), int(obs[2]), table_html, "### Live", "Monitoring"

# --- GRADIO UI ---
# CRITICAL: This variable MUST be named 'demo'
with gr.Blocks(title="AI VARANI") as demo:
    gr.Markdown("# 🛡️ AI VARANI: Autonomous SRE")
    with gr.Row():
        with gr.Column():
            init_btn = gr.Button("🚀 Inject Incident", variant="primary")
            action_id_input = gr.Number(label="Action ID", value=0, precision=0)
            step_btn = gr.Button("⚡ Manual Step")
        with gr.Column():
            err_m = gr.Number(label="Error Rate")
            lat_m = gr.Number(label="Latency")
            deg_m = gr.Number(label="Degraded")
            table_output = gr.HTML()
            logs_output = gr.Textbox(lines=5, label="Logs")

    init_btn.click(handle_reset, outputs=[err_m, lat_m, deg_m, table_output, gr.Markdown(), gr.Markdown(), logs_output])
    step_btn.click(handle_step, inputs=[action_id_input], outputs=[err_m, lat_m, deg_m, table_output, gr.Markdown(), gr.Markdown(), logs_output])
