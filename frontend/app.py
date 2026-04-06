import gradio as gr
import os
import sys

# Ensure root directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from openenv_incident.env import IncidentResponseEnv

# Initialize the Environment
env = IncidentResponseEnv()

def get_ui_metrics():
    try:
        raw = env.state_manager.get_all_service_summaries()
        if not raw: return 0.0, 0, 0
        avg_err = sum(s['metrics']['error_rate'] for s in raw.values()) / len(raw)
        avg_lat = sum(s['metrics']['latency'] for s in raw.values()) / len(raw)
        deg = sum(1 for s in raw.values() if s['status'] != 'healthy')
        return round(float(avg_err * 100), 1), round(float(avg_lat), 0), int(deg)
    except: return 0.0, 0, 0

def get_service_table():
    raw = env.state_manager.get_all_service_summaries()
    table = "| Service | Status | Health | Latency |\n| :--- | :--- | :--- | :--- |\n"
    for name, s in raw.items():
        emoji = "✅ healthy" if s['status'] == 'healthy' else "🚨 degraded"
        table += f"| **{name}** | {emoji} | {s['health']*100:.0f}% | {s['metrics']['latency']:.0f}ms |\n"
    return table

def start_incident_pro(scenario):
    env.reset(options={"scenario_id": scenario} if scenario != "Random" else None)
    err, lat, deg = get_ui_metrics()
    table = get_service_table()
    logs = "\n".join(env.state_manager.get_recent_logs(10))
    actions = list(env.action_space_manager.id_to_action.values())
    return (
        f"### 📡 {env.state_manager.incident.scenario_name}", 
        f"**Severity:** {env.state_manager.incident.severity.upper()}",
        err, lat, deg, table, logs, gr.update(choices=actions, value=actions[0]),
        "### 🔍 Analysis: Triage Started"
    )

def execute_action_pro(action_desc):
    if not action_desc or "Waiting" in action_desc:
        return 0.0, 0, 0, get_service_table(), "Logs...", "### 🔍 Analysis: Start incident first."
    
    action_id = next(id for id, desc in env.action_space_manager.id_to_action.items() if desc == action_desc)
    env.step(action_id)
    
    err, lat, deg = get_ui_metrics()
    table = get_service_table()
    logs = "\n".join(env.state_manager.get_recent_logs(10))
    
    # Check resolution
    if env.state_manager.incident.resolved:
        grade = env.get_grade()
        # We use a clean, bold string to ensure Gradio renders it
        rca = f"## ✅ INCIDENT RESOLVED\n\n**Final Grade: {grade.grade_letter}**\n\n**Action Taken:** {action_desc}\n\n**System Status:** Back to 100% Health"
    else:
        rca = f"### 🔍 Analysis: Action `{action_desc}` performed. Monitoring metrics..."

    return err, lat, deg, table, logs, rca

# --- UI Header ---
head_content = """
<link rel="icon" type="image/png" href="https://cdn-icons-png.flaticon.com/512/1063/1063376.png">
<script>document.title = "AI VARANI";</script>
"""

with gr.Blocks(title="AI VARANI", head=head_content) as demo:
    gr.Markdown("# 🛡️ AI VARANI: Autonomous SRE Command Center")
    with gr.Row():
        err_card = gr.Number(label="Avg Error Rate %", precision=1)
        lat_card = gr.Number(label="Avg Latency (ms)", precision=0)
        deg_card = gr.Number(label="Degraded Services", precision=0)
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group():
                gr.Markdown("### ⚙️ Incident Control")
                scen_drop = gr.Dropdown(["Random", "database_slowdown", "auth_crash"], label="Scenario", value="Random")
                btn_init = gr.Button("🚀 Initialize Environment", variant="primary")
            with gr.Group():
                gr.Markdown("### ⚡ Action Console")
                act_drop = gr.Dropdown(["Waiting for init..."], label="Select Action")
                btn_exec = gr.Button("Execute Action")
        with gr.Column(scale=2):
            with gr.Group():
                inc_title = gr.Markdown("### 🛰️ System Standby")
                inc_sev = gr.Markdown("Severity: N/A")
                rca_panel = gr.Markdown("### 🔍 Analysis: System is Healthy")
            with gr.Tabs():
                with gr.TabItem("📊 Health Metrics"): health_table = gr.Markdown("Initialize to see data.")
                with gr.TabItem("📜 System Logs"): log_viewer = gr.Code(label="Real-time Feed", lines=10)

    btn_init.click(start_incident_pro, [scen_drop], [inc_title, inc_sev, err_card, lat_card, deg_card, health_table, log_viewer, act_drop, rca_panel])
    btn_exec.click(execute_action_pro, [act_drop], [err_card, lat_card, deg_card, health_table, log_viewer, rca_panel])

if __name__ == "__main__":
    css = "footer {display: none !important;} .gradio-container footer {display: none !important;}"
    # Changed port to 7862 to ensure a clean cache for the Grade update
    demo.launch(theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate"), css=css, server_port=7862)