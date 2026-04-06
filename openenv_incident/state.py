from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from openenv_incident.utils import calculate_health_score, SERVICE_STATUS, ServiceDependencyGraph

@dataclass
class ServiceMetrics:
    error_rate: float = 0.0
    latency: float = 100.0
    throughput: float = 1000.0
    cpu_usage: float = 50.0
    memory_usage: float = 50.0
    def to_dict(self): return vars(self)

class ServiceState:
    def __init__(self, name: str):
        self.name = name
        self.status = SERVICE_STATUS['HEALTHY']
        self.metrics = ServiceMetrics()
    def get_health(self): return calculate_health_score(self.metrics.to_dict())
    def degrade(self, val):
        self.metrics.error_rate = min(1.0, self.metrics.error_rate + val * 0.2)
        self.metrics.latency *= (1 + val)
        self.status = SERVICE_STATUS['DEGRADED'] if self.get_health() < 0.8 else SERVICE_STATUS['HEALTHY']
    def restart(self):
        self.metrics.error_rate = 0.0
        self.metrics.latency = 100.0
        self.status = SERVICE_STATUS['HEALTHY']

class IncidentState:
    def __init__(self):
        self.active = False
        self.scenario_name = ""
        self.severity = "none"
        self.root_cause_service = None
        self.affected_services = []
        self.resolved = False

class SystemState:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.services = {s['name']: ServiceState(s['name']) for s in config['services']}
        self.incident = IncidentState()
        self.current_step = 0
        self.system_logs = []

    def reset(self): self.__init__(self.config)
    def apply_incident(self, data):
        self.incident.active = True
        self.incident.scenario_name = data['display_name']
        self.incident.severity = data.get('severity', 'medium')
        self.incident.root_cause_service = data['root_cause']['service']
        self.incident.affected_services = data['affected_services']
        for s in self.incident.affected_services: self.services[s].degrade(0.5)
        self.system_logs.append(f"ALERT: {self.incident.scenario_name}")

    def apply_action_effect(self, action, target, params):
        if action == 'restart_service' and target in self.services:
            self.services[target].restart()
            self.system_logs.append(f"Action: Restarted {target}")
        if action == 'mark_resolved': self.incident.resolved = True

    def get_all_service_summaries(self):
        return {n: {'status': s.status, 'health': s.get_health(), 'metrics': s.metrics.to_dict()} for n, s in self.services.items()}
    def get_global_status(self): return {'incident_active': self.incident.active, 'incident_resolved': self.incident.resolved}
    def is_terminal(self): return self.incident.resolved or self.current_step >= 50
    def get_recent_logs(self, count=10): return self.system_logs[-count:]
    def step(self): self.current_step += 1