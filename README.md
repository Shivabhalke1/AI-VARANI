# 🛡️ AI VARANI: Autonomous SRE Command Center
**Project for the Meta PyTorch OpenEnv Hackathon 2026**

AI VARANI (Varani AI) is an autonomous Site Reliability Engineering (SRE) environment designed to train and evaluate AI agents in the art of incident response. Built on the **OpenEnv** framework, it simulates a complex microservice architecture where agents must observe telemetry, triage logs, and execute self-healing actions to maintain 100% system uptime.

---

## 🚀 Vision
In modern distributed systems, downtime costs an average of **$9,000 per minute**. Traditional monitoring only alerts humans; AI VARANI provides a "Gym" where agents learn to fix systems autonomously, reducing Mean Time To Recovery (MTTR) from minutes to milliseconds.

---

## 📡 Environment Specifications

AI VARANI follows the standard Gymnasium/OpenEnv interface, making it compatible with any PyTorch-based RL library (Stable Baselines3, Ray Rllib, etc.).

| Component | Type | Description |
| :--- | :--- | :--- |
| **Observation Space** | `Box(0, 1, (24,))` | Normalized telemetry: Error rates, Latency, and CPU/Mem vitals for 4 services. |
| **Action Space** | `Discrete(8)` | SRE Actions: `inspect_logs`, `restart_service`, `scale_up`, `rollback`, etc. |
| **Reward Function** | `Health + Step Penalty` | `+250` for resolution, `-1` per step to encourage speed (MTTR). |
| **Incident Scenarios** | `Deterministic` | Scenarios: DB Pool Exhaustion, Auth Memory Leak, API Latency Spike. |

---

## 🛠️ Project Structure

```text
AI-VARANI/
├── openenv_incident/       # Core Logic & Simulation Engine
│   ├── env.py              # Gymnasium-compliant Environment
│   ├── state_manager.py    # Telemetry and Log tracking
│   └── action_space.py     # Mapping of AI actions to system commands
├── frontend/               
│   └── app.py              # Gradio-based Monitoring Dashboard
├── demo.py                 # "One-Click" Autonomous Agent Demo
├── requirements.txt        # Dependency list
└── README.md               # Technical Documentation