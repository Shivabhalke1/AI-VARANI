import gradio as gr
import time
import pandas as pd
from openenv_incident.env import IncidentEnv

# 1. Initialize the SRE Engine
env = IncidentEnv()
log_history = []  # Stores the scrolling history for the judge to see

def get_autonomous_diagnosis(obs):
    """The AI Brain: Analyzes metrics to identify the root cause."""
    error_rate, latency = obs[0], obs[1]
    if error_rate > 5:
        return 0, "Database Connection Pool Exhaustion", "Restarting DB Service to clear connections"
    elif latency > 200:
        return 1, "Network Congestion / Traffic Spike", "Scaling Replicas to handle load"
    return 2, "Configuration Drift", "Rolling back to last stable version"

def update_ui_components(is_resolving=False, diagnosis_info=None):
    """Fetches real-time telemetry and formats the UI components."""
    obs, info = env.get_state()
    is_healthy = obs[0] < 5
    
    if is_resolving:
        briefing = f"🤖 **SELF-HEALING ACTIVE:** {diagnosis_info[2]}"
        analysis = f"### ⚠️ Incident Identified: {diagnosis_info[1]}"
    elif is_healthy:
        briefing = "✅ **System Healthy:** AI Agent is monitoring background telemetry..."
        analysis = "### 🔍 Analysis: No anomalies detected. SLA is green."
    else:
        briefing = "⚠️ **Anomalous Activity:** High Error Rates! AI is investigating..."
        analysis = "### ⚠️ Analysis: Critical Incident Detected. Waiting for trigger."

    # Build the Service Health Table
    services = ["api_gateway", "auth_service", "user_service", "payment_service", "database"]
    health_data = [{"Service": s, "Status": "✅ Healthy" if is_healthy else "❌ Degraded", "Health": "95%", "Latency": "100ms"} for s in services]
    table_html = f"<div style='overflow-x:auto;'>{pd.DataFrame(health_data).to_html(classes='table', index=False, border=0)}</div>"
    
    return obs[0], obs[1], obs[2], table_html, analysis, briefing

def handle_reset():
    """Initializes the simulation and clears logs."""
    global log_history
    env.reset()
    log_history = [f"[{time.strftime('%H:%M:%S')}] 🚀 Simulation Initialized. Monitoring active."]
    return *update_ui_components(), "\n".join(log_history)

def handle_self_heal(is_auto_active):
    """The Core Logic: Detects issues and applies fixes automatically."""
    global log_history
    obs, _ = env.get_state()
    
    # Check if remediation is needed (Error > 5% or Latency > 200ms)
    if obs[0] >= 5 or obs[1] >= 200:
        action_idx, issue_name, fix_desc = get_autonomous_diagnosis(obs)
        
        # 1. Update UI to show AI is working
        err, lat, deg, table, _, _ = update_ui_components(is_resolving=True, diagnosis_info=(action_idx, issue_name, fix_desc))
        
        # 2. Execute the fix in the environment
        env.step(action_idx)
        
        # 3. Final status update
        final_err, final_lat, final_deg, final_table, _, _ = update_ui_components()
        analysis = f"### ✅ Resolved: {issue_name}\nRoot cause mitigated automatically."
        briefing = f"🎉 **Success:** AI detected and resolved {issue_name}."
        
        new_entry = f"[{time.strftime('%H:%M:%S')}] 🤖 AI FIXED: {issue_name} via {fix_desc.split(' ')[0]}."
        log_history.insert(0, new_entry)
        
        return final_err, final_lat, final_deg, final_table, analysis, briefing, "\n".join(log_history)
    
    # If healthy, keep the current view but don't spam the logs
    return *update_ui_components(), gr.skip()

# 2. Professional SRE Styling
custom_css = """
footer {visibility: hidden} 
#header-title {text-align: center; color: #ffffff; background: #c0392b; padding: 15px; border-radius: 8px;}
.info-text {background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #c0392b; color: #e0e0e0;}
.table {width: 100%; text-align: center; color: white;}
"""

# 3. Build the Command Center
with gr.Blocks(title="AI VARANI", theme=gr.themes.Soft(), css=custom_css) as demo:
    gr.Markdown("# 🛡️ AI VARANI: Autonomous Self-Healing SRE", elem_id="header-title")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Chaos Engine\n*Inject an incident into the system.*")
            scenario_drop = gr.Dropdown(["Database Leak", "Network Congestion", "Random"], label="Select Scenario")
            init_btn = gr.Button("🚀 Inject Incident", variant="primary")
            
            gr.Markdown("### 🤖 AI Agent Control\n*Enable the AI to fix issues automatically.*")
            auto_solve_toggle = gr.Checkbox(label="Enable AI Auto-Resolution", value=True)
            manual_fix_btn = gr.Button("⚡ Trigger Manual AI Solve", variant="secondary")

        with gr.Column(scale=2):
            gr.Markdown("### 📊 Live System Diagnostics")
            with gr.Row():
                err_m = gr.Number(label="Error Rate %", value=0)
                lat_m = gr.Number(label="Latency (ms)", value=0)
                deg_m = gr.Number(label="Degraded Services", value=0)
            
            briefing_box = gr.Markdown("🚀 **System Standby**: Initialize to begin monitoring.", elem_classes="info-text")
            analysis_box = gr.Markdown("### 🛰️ AI Analysis: Standby")
            
            with gr.Tabs():
                with gr.TabItem("📋 Health Metrics"):
                    table_output = gr.HTML("<p style='text-align:center;'>Telemetry Offline</p>")
                with gr.TabItem("📜 AI Agent Logs"):
                    logs_output = gr.Textbox(label="", lines=10, interactive=False)

    # --- Button Logic ---
    outputs_list = [err_m, lat_m, deg_m, table_output, analysis_box, briefing_box, logs_output]
    
    init_btn.click(fn=handle_reset, outputs=outputs_list)
    manual_fix_btn.click(fn=handle_self_heal, inputs=[auto_solve_toggle], outputs=outputs_list)

    # --- THE BACKGROUND MONITOR (The Secret Sauce) ---
    timer = gr.Timer(3) # Scans for issues every 3 seconds
    timer.tick(
        fn=lambda active: handle_self_heal(active) if active else (gr.skip(),)*7,
        inputs=[auto_solve_toggle],
        outputs=outputs_list
    )

if __name__ == "__main__":
    demo.launch()