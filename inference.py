import asyncio
import os
import textwrap
from typing import List, Optional
from openai import OpenAI

# Swapping the sample for your actual AI VARANI environment
from openenv_incident.env import IncidentEnv as AI_Varani_Env

API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
TASK_NAME = "incident-response"
BENCHMARK = "ai_varani_v1"
MAX_STEPS = 10

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = AI_Varani_Env() # Initialize your actual environment
    
    rewards = []
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
    
    obs, info = env.reset()
    done = False
    step_count = 0

    try:
        while not done and step_count < MAX_STEPS:
            step_count += 1
            # Simple heuristic for the inference script requirement
            action = 0 # Agent logic goes here or links to your demo.py logic
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            rewards.append(reward)
            
            log_step(step=step_count, action=str(action), reward=reward, done=done, error=None)
        
        score = sum(rewards) / 250.0 # Normalized score based on your success bonus
        log_end(success=(score > 0.5), steps=step_count, score=max(0, min(score, 1.0)), rewards=rewards)
    finally:
        env.close()

if __name__ == "__main__":
    asyncio.run(main())