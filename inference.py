import os
import sys
import numpy as np
from openai import OpenAI
from openenv_incident.env import IncidentEnv

def run_evaluation():
    task_name = "autonomous_incident_response"
    client = OpenAI(
        base_url=os.environ.get("API_BASE_URL", "https://api.openai.com/v1"),
        api_key=os.environ.get("API_KEY", "dummy-key")
    )

    try:
        env = IncidentEnv(config_path="configs/env_config.yaml")
        print(f"[START] task={task_name}", flush=True)
        
        obs, info = env.reset()
        total_reward = 0
        
        for step in range(1, 4):
            # MANDATORY LLM CALL
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"State: {obs}. Action 0, 1, or 2?"}]
            )
            action = int(''.join(filter(str.isdigit, response.choices[0].message.content)) or 0)
            
            obs, reward, term, trunc, info = env.step(action)
            total_reward += reward
            print(f"[STEP] step={step} reward={reward}", flush=True)
            if term or trunc: break
        
        print(f"[END] task={task_name} score={total_reward/3} steps={step}", flush=True)
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    run_evaluation()
