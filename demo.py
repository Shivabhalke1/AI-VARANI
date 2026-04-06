"""
AI VARANI: Smart Resolution Demo
AI VARANI IS PRESENT IN THE SYSTEM
Demonstrates a successful incident resolution and high-score grading.
"""

import time
import sys
import os

# Add current directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from openenv_incident.env import IncidentResponseEnv
from openenv_incident.utils import ColoredOutput

def run_smart_demo():
    ColoredOutput.print_header("\n🚀 Starting AI VARANI Smart Demo...")
    
    env = IncidentResponseEnv()
    obs, info = env.reset()
    
    scenario_name = info.get('scenario_name')
    root_cause = env.state_manager.incident.root_cause_service
    
    ColoredOutput.print_info(f"\n[INCIDENT ACTIVE]")
    print(f"Scenario: {scenario_name}")
    print(f"Root Cause Identified (Internal): {root_cause}")
    print("-" * 45)

    # --- Step 1: Diagnose the specific service ---
    # We find the ID for "inspect_logs on [root_cause]"
    diag_action = f"inspect_logs on {root_cause}"
    action_id = next(id for id, desc in env.action_space_manager.id_to_action.items() if desc == diag_action)
    
    _, reward, _, _, _ = env.step(action_id)
    print(f"Step 1: {diag_action} | Reward: {reward:.2f} (Diagnosing...)")
    time.sleep(0.5)

    # --- Step 2: Remediate (The Fix) ---
    # We find the ID for "restart_service on [root_cause]"
    fix_action = f"restart_service on {root_cause}"
    action_id = next(id for id, desc in env.action_space_manager.id_to_action.items() if desc == fix_action)
    
    _, reward, _, _, _ = env.step(action_id)
    print(f"Step 2: {fix_action} | Reward: {reward:.2f} (Applying Fix!)")
    time.sleep(0.5)

    # --- Step 3: Resolve the incident ---
    # Tell the environment the job is done
    resolve_id = next(id for id, desc in env.action_space_manager.id_to_action.items() if desc == "mark_resolved")
    
    _, reward, terminated, _, info = env.step(resolve_id)
    print(f"Step 3: mark_resolved | Reward: {reward:.2f} (Closing Ticket)")
    print("-" * 45)

    # --- Final Grading ---
    if terminated:
        grade = env.get_grade()
        ColoredOutput.print_success(f"\n🏆 INCIDENT RESOLVED SUCCESSFULLY!")
        print(f"Final Grade: {grade.grade_letter}")
        print(f"Overall Score: {grade.overall_score:.1f}")
        print(f"Summary: {grade.summary}")
    else:
        ColoredOutput.print_error("\n❌ Resolution Failed.")

if __name__ == "__main__":
    run_smart_demo()