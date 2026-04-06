cat > scripts/generate_scenarios.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
import json
import yaml
import random
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv_incident.utils import ColoredOutput
from openenv_incident.scenarios import Scenario, DifficultyLevel


class ScenarioGenerator:
    def __init__(self, config_path=None):
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = config_path or os.path.join(self.base_path, 'configs', 'scenarios.yaml')
        self.existing_scenarios = {}
        self.load_existing_scenarios()
        
        self.services = ['api_gateway', 'auth_service', 'user_service', 'payment_service', 'database', 'cache', 'notification_service']
        self.issue_types = {
            'api_gateway': ['network_congestion', 'rate_limiting', 'ssl_certificate'],
            'auth_service': ['memory_leak', 'token_validation', 'database_connection'],
            'user_service': ['data_corruption', 'slow_queries', 'dependency_failure'],
            'payment_service': ['gateway_error', 'fraud_detection', 'webhook_failure'],
            'database': ['connection_pool', 'deadlock', 'replication_lag', 'disk_full'],
            'cache': ['split_brain', 'eviction_policy', 'memory_pressure'],
            'notification_service': ['queue_backlog', 'rate_limit', 'webhook_failure']
        }
        self.severity_levels = ['low', 'medium', 'high', 'critical']
        self.difficulty_levels = ['easy', 'medium', 'hard']
    
    def load_existing_scenarios(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and 'scenarios' in data:
                        self.existing_scenarios = data['scenarios']
                ColoredOutput.print_info(f"Loaded {len(self.existing_scenarios)} existing scenarios")
            except Exception as e:
                ColoredOutput.print_warning(f"Could not load: {e}")
    
    def generate_random_scenario(self):
        service = random.choice(self.services)
        issue = random.choice(self.issue_types.get(service, ['unknown_issue']))
        scenario_id = f"{service}_{issue}_{random.randint(1000, 9999)}"
        name = f"{service.replace('_', ' ').title()} {issue.replace('_', ' ').title()}"
        severity = random.choice(self.severity_levels)
        difficulty = random.choice(self.difficulty_levels)
        
        affected = [service]
        if service == "database":
            affected.extend(["user_service", "payment_service"])
        elif service == "auth_service":
            affected.extend(["api_gateway", "user_service"])
        elif service == "cache":
            affected.extend(["user_service", "database"])
        
        return {
            scenario_id: {
                'name': name,
                'severity': severity,
                'difficulty': difficulty,
                'root_cause': {'service': service, 'issue': issue, 'details': f"Issue in {service}"},
                'symptoms': [{'type': 'alert', 'message': f"{service} issue detected", 'service': service}],
                'affected_services': affected[:4],
                'correct_mitigations': [{'action': 'inspect_logs', 'target': service}, {'action': 'restart_service', 'target': service}],
                'wrong_actions_penalty': [],
                'resolution_steps': 3 if difficulty == 'easy' else 5 if difficulty == 'medium' else 8,
                'time_to_resolve_steps': 6 if difficulty == 'easy' else 10 if difficulty == 'medium' else 16
            }
        }
    
    def generate_multiple_scenarios(self, count=5):
        scenarios = {}
        for i in range(count):
            scenario = self.generate_random_scenario()
            scenarios.update(scenario)
            ColoredOutput.print_success(f"Generated {i+1}/{count}")
        return scenarios
    
    def save_scenarios(self, scenarios, output_path=None):
        output_path = output_path or self.config_path
        existing_data = {}
        if os.path.exists(output_path):
            try:
                with open(output_path, 'r') as f:
                    existing_data = yaml.safe_load(f) or {}
            except:
                existing_data = {}
        
        if 'scenarios' not in existing_data:
            existing_data['scenarios'] = {}
        existing_data['scenarios'].update(scenarios)
        existing_data['generated_at'] = datetime.now().isoformat()
        existing_data['total_scenarios'] = len(existing_data['scenarios'])
        
        with open(output_path, 'w') as f:
            yaml.dump(existing_data, f, default_flow_style=False, sort_keys=False)
        ColoredOutput.print_success(f"Saved {len(scenarios)} scenarios to {output_path}")
    
    def generate_and_save(self, count=5, output_path=None):
        ColoredOutput.print_header("\n" + "=" * 60)
        ColoredOutput.print_header("SCENARIO GENERATOR")
        ColoredOutput.print_header("=" * 60 + "\n")
        scenarios = self.generate_multiple_scenarios(count)
        self.save_scenarios(scenarios, output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', '-c', type=int, default=5, help='Number of scenarios')
    parser.add_argument('--output', '-o', type=str, help='Output file path')
    args = parser.parse_args()
    
    generator = ScenarioGenerator()
    generator.generate_and_save(count=args.count, output_path=args.output)


if __name__ == "__main__":
    main()
EOF