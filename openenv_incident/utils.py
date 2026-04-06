import yaml
import numpy as np
from typing import Dict, List, Any

SERVICE_STATUS = {
    'HEALTHY': 'healthy',
    'DEGRADED': 'degraded',
    'CRITICAL': 'critical',
    'FAILED': 'failed'
}

def load_yaml_config(filepath: str) -> Dict[str, Any]:
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def calculate_health_score(metrics: Dict[str, float]) -> float:
    score = 1.0
    if 'error_rate' in metrics:
        score -= (metrics['error_rate'] * 0.5)
    if 'latency' in metrics:
        latency_penalty = min(metrics['latency'] / 2000.0, 0.5)
        score -= latency_penalty
    return max(0.0, min(1.0, score))

class ServiceDependencyGraph:
    def __init__(self, services: List[Dict]):
        self.services = {s['name']: s for s in services}
    def get_dependents(self, service_name: str) -> List[str]:
        dependents = []
        for name, data in self.services.items():
            if service_name in data.get('dependencies', []):
                dependents.append(name)
        return dependents

class ColoredOutput:
    @staticmethod
    def print_header(text: str): print(f"\033[95m\033[1m{text}\033[0m")
    @staticmethod
    def print_success(text: str): print(f"\033[92m{text}\033[0m")
    @staticmethod
    def print_error(text: str): print(f"\033[91m{text}\033[0m")
    @staticmethod
    def print_info(text: str): print(f"\033[94m{text}\033[0m")