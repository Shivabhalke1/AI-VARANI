#!/usr/bin/env python3
import sys
import random

sys.path.insert(0, '.')

from openenv_incident.env import IncidentResponseEnv
from openenv_incident.utils import ColoredOutput


def run_quick_test():
    ColoredOutput.print_header("\nQuick Environment Test\n")
    env = IncidentResponseEnv()
    obs, info = env.reset()
    print(f"✓ Environment reset successfully")
    print(f"  Scenario: {info.get('scenario_name', 'Unknown')}")
    print(f"  Difficulty: {info.get('difficulty', 'unknown')}")
    print(f"  Action space size: {env.action_space}")
    
    steps = 0
    total_reward = 0
    
    while steps < 10:
        mask = env.get_action_mask()
        valid = [i for i, v in enumerate(mask) if v == 1]
        if not valid:
            break
        action = random.choice(valid)
        _, reward, terminated, truncated, _ = env.step(action)
        total_reward += reward
        steps += 1
        if terminated or truncated:
            break
    
    print(f"✓ Completed {steps} steps")
    print(f"  Total reward: {total_reward:.2f}")
    
    grade = env.get_grade()
    print(f"✓ Grade: {grade.grade_letter} ({grade.overall_score:.1f})")
    ColoredOutput.print_success("\n✓ Quick test passed!")


if __name__ == "__main__":
    run_quick_test()