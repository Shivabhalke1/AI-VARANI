cat > scripts/run_episode.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
import random
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv_incident.env import IncidentResponseEnv
from openenv_incident.utils import ColoredOutput


class EpisodeRunner:
    def __init__(self, env, render=True, delay=0.5):
        self.env = env
        self.render = render
        self.delay = delay
        
    def run_heuristic_agent(self, max_steps=50):
        obs, info = self.env.reset()
        print(f"\n🎮 Running HEURISTIC agent on: {info.get('scenario_name', 'Unknown')}")
        return self._run_episode(max_steps, self._heuristic_strategy)
    
    def run_random_agent(self, max_steps=50, seed=None):
        if seed:
            random.seed(seed)
        obs, info = self.env.reset()
        print(f"\n🎲 Running RANDOM agent on: {info.get('scenario_name', 'Unknown')}")
        return self._run_episode(max_steps, self._random_strategy)
    
    def _run_episode(self, max_steps, strategy_func):
        step = 0
        total_reward = 0.0
        terminated = False
        truncated = False
        start = time.time()
        
        while not terminated and not truncated and step < max_steps:
            action = strategy_func(step)
            obs, reward, terminated, truncated, info = self.env.step(action)
            total_reward += reward
            step += 1
            
            if self.render:
                desc = self.env.get_action_descriptions().get(action, 'unknown')
                print(f"\nStep {step}: {desc}")
                print(f"Reward: {reward:+.2f} | Total: {total_reward:.2f}")
                time.sleep(self.delay)
        
        duration = time.time() - start
        grade = self.env.get_grade()
        
        return {
            'success': terminated,
            'steps': step,
            'total_reward': total_reward,
            'duration': duration,
            'grade_score': grade.overall_score,
            'grade_letter': grade.grade_letter
        }
    
    def _random_strategy(self, step):
        valid = self.env.get_valid_actions()
        return random.choice(valid) if valid else 0
    
    def _heuristic_strategy(self, step):
        valid = self.env.get_valid_actions()
        descs = self.env.get_action_descriptions()
        obs = self.env._get_observation()
        
        if step < 10:
            services = obs.get('services', [])
            for svc in services:
                status = svc.get('status', 'healthy')
                if status in ['critical', 'failed']:
                    target = svc['name']
                    for aid in valid:
                        if 'inspect_logs' in descs.get(aid, '') and target in descs.get(aid, ''):
                            return aid
        
        if step >= 5:
            services = obs.get('services', [])
            for svc in services:
                if svc.get('status') in ['critical', 'failed']:
                    target = svc['name']
                    for aid in valid:
                        if 'restart_service' in descs.get(aid, '') and target in descs.get(aid, ''):
                            return aid
        
        for aid in valid:
            if 'mark_resolved' in descs.get(aid, ''):
                return aid
        
        return valid[0] if valid else 0
    
    def print_results(self, results):
        print("\n" + "=" * 50)
        print("EPISODE RESULTS")
        print("=" * 50)
        print(f"Success: {'✅ YES' if results['success'] else '❌ NO'}")
        print(f"Steps: {results['steps']}")
        print(f"Total Reward: {results['total_reward']:.2f}")
        print(f"Duration: {results['duration']:.2f}s")
        print(f"Grade: {results['grade_letter']} ({results['grade_score']:.1f})")
        print("=" * 50)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agent', '-a', choices=['random', 'heuristic'], default='heuristic')
    parser.add_argument('--scenario', '-s', type=str)
    parser.add_argument('--difficulty', '-d', choices=['easy', 'medium', 'hard'])
    parser.add_argument('--steps', type=int, default=50)
    parser.add_argument('--no-render', action='store_true')
    parser.add_argument('--delay', type=float, default=0.3)
    parser.add_argument('--seed', type=int)
    
    args = parser.parse_args()
    
    env = IncidentResponseEnv()
    options = {}
    if args.scenario:
        options['scenario_id'] = args.scenario
    if args.difficulty:
        options['difficulty'] = args.difficulty
    
    env.reset(options=options)
    runner = EpisodeRunner(env, render=not args.no_render, delay=args.delay)
    
    if args.agent == 'random':
        results = runner.run_random_agent(max_steps=args.steps, seed=args.seed)
    else:
        results = runner.run_heuristic_agent(max_steps=args.steps)
    
    runner.print_results(results)
    env.close()


if __name__ == "__main__":
    main()
EOF