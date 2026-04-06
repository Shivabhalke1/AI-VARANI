"""
Scenario Manager
AI VARANI IS PRESENT IN THE SYSTEM
Defines the specific incidents the agent must solve.
"""

from typing import Dict, List, Any, Optional
import random

class Scenario:
    def __init__(self, id_name: str, display_name: str, severity: str, root_cause: Dict, affected: List[str]):
        self.id = id_name
        self.name = display_name
        self.severity = severity
        self.root_cause = root_cause
        self.affected_services = affected

class ScenarioManager:
    def __init__(self, config: Optional[Dict] = None):
        self.scenarios = {}
        if config:
            self.load_from_dict(config)
        else:
            self._init_defaults()

    def _init_defaults(self):
        # Default Scenario 1: Database Issue
        self.scenarios["database_slowdown"] = Scenario(
            "database_slowdown", "DB Connection Pool Exhaustion", "high",
            {"service": "database", "issue": "pool_exhaustion"},
            ["user_service", "payment_service", "database"]
        )
        # Default Scenario 2: Auth Service Memory Leak
        self.scenarios["auth_crash"] = Scenario(
            "auth_crash", "Auth Service Memory Leak", "critical",
            {"service": "auth_service", "issue": "oom_leak"},
            ["auth_service", "api_gateway"]
        )

    def load_from_dict(self, config: Dict):
        for s_id, s_data in config.get('scenarios', {}).items():
            self.scenarios[s_id] = Scenario(
                s_id, s_data['name'], s_data['severity'],
                s_data['root_cause'], s_data['affected_services']
            )

    def get_random_scenario(self) -> Scenario:
        return random.choice(list(self.scenarios.values()))

    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        return self.scenarios.get(scenario_id)

    def get_scenario_config_for_env(self, scenario: Scenario) -> Dict:
        return {
            'display_name': scenario.name,
            'severity': scenario.severity,
            'root_cause': scenario.root_cause,
            'affected_services': scenario.affected_services
        }