cat > scripts/evaluate_demo.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
import time
import random
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv_incident.env import IncidentResponseEnv
from openenv_incident.utils import ColoredOutput


class DemoEvaluator:
    def __init__(self, render=False, delay=0.1):
        self.render = render
        self.delay = delay
        self.results = []
    
    def run_heuristic_agent(self, env, max_steps=50):
        obs, info = env.reset()
        steps = 0
        total_reward = 0
        terminated = False
        truncated = False
        suspicious_services = []
        action_history = []
        
        while not terminated and not truncated and steps < max_steps:
            valid_actions = env.get_valid_actions()
            descs = env.get_action_descriptions()
            
            if not valid_actions:
                break
            
            services = obs.get('services', [])
            for svc in services:
                status = svc.get('status', 'healthy')
                metrics = svc.get('metrics', {})
                if status in ['critical', 'failed'] or metrics.get('error_rate', 0) > 0.05:
                    if svc['name'] not in suspicious_services:
                        suspicious_services.append(svc['name'])
            
            action = valid_actions[0]
            if suspicious_services:
                target = suspicious_services[0]
                for aid in valid_actions:
                    desc = descs.get(aid, '')
                    if 'restart_service' in desc and target in desc:
                        action = aid
                        break
                    elif 'inspect_logs' in desc and target in desc:
                        action = aid
            
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            steps += 1
            
            if self.render:
                env.render()
                time.sleep(self.delay)
        
        grade = env.get_grade()
        return {
            'success': terminated,
            'steps': steps,
            'total_reward': total_reward,
            'grade_score': grade.overall_score,
            'grade_letter': grade.grade_letter,
            'root_cause_found': grade.root_cause_correct,
            'scenario_name': info.get('scenario_name', 'Unknown'),
            'difficulty': info.get('difficulty', 'unknown')
        }
    
    def evaluate_all_scenarios(self, max_steps=50, runs_per_scenario=1):
        env = IncidentResponseEnv()
        scenario_ids = env.scenario_manager.get_scenario_ids()
        env.close()
        
        results = []
        for sid in scenario_ids:
            ColoredOutput.print_info(f"\n📋 Evaluating: {sid}")
            for run in range(runs_per_scenario):
                env = IncidentResponseEnv()
                env.reset(options={'scenario_id': sid})
                result = self.run_heuristic_agent(env, max_steps)
                result['scenario_id'] = sid
                result['run'] = run + 1
                results.append(result)
                env.close()
                status = "✅" if result['success'] else "❌"
                print(f"   {status} Run {run+1}: Grade {result['grade_letter']} ({result['grade_score']:.1f})")
        
        self.results = results
        return results
    
    def generate_report(self):
        if not self.results:
            return "No results"
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get('success', False))
        avg_grade = sum(r.get('grade_score', 0) for r in self.results) / total
        
        report = []
        report.append("=" * 60)
        report.append("DEMO EVALUATION REPORT")
        report.append("=" * 60)
        report.append(f"Total Runs: {total}")
        report.append(f"Successful: {successful}/{total} ({successful/total*100:.1f}%)")
        report.append(f"Average Grade: {avg_grade:.1f}/100")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, output_path):
        report = self.generate_report()
        with open(output_path, 'w') as f:
            f.write(report)
        json_path = output_path.replace('.txt', '.json')
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        ColoredOutput.print_success(f"Report saved to {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', '-r', type=int, default=1)
    parser.add_argument('--steps', type=int, default=50)
    parser.add_argument('--output', '-o', type=str)
    args = parser.parse_args()
    
    evaluator = DemoEvaluator(render=False)
    evaluator.evaluate_all_scenarios(max_steps=args.steps, runs_per_scenario=args.runs)
    print(evaluator.generate_report())
    
    if args.output:
        evaluator.save_report(args.output)


if __name__ == "__main__":
    main()
EOF