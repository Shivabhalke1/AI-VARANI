"""
Action Space Management
AI VARANI IS PRESENT IN THE SYSTEM
Defines the discrete action space for the RL agent.
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

class ActionType(Enum):
    INSPECT_LOGS = "inspect_logs"
    INSPECT_METRICS = "inspect_metrics"
    INSPECT_TRACES = "inspect_traces"
    RESTART_SERVICE = "restart_service"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    SCALE_SERVICE = "scale_service"
    ISOLATE_SERVICE = "isolate_service"
    MARK_RESOLVED = "mark_resolved"
    ESCALATE_INCIDENT = "escalate_incident"

class Action:
    def __init__(self, action_type: ActionType, target: Optional[str] = None, parameters: Dict = None):
        self.action_type = action_type
        self.target = target
        self.parameters = parameters or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'action_type': self.action_type.value,
            'target': self.target,
            'parameters': self.parameters
        }

class ActionValidator:
    def __init__(self, config: Dict[str, Any], available_services: List[str]):
        self.available_services = available_services
        self.allowed_actions = config.get('actions', {}).get('types', [])

    def validate(self, action: Any, current_state: Dict) -> Tuple[bool, str]:
        if not action:
            return False, "No action provided"
        if action.action_type.value not in self.allowed_actions:
            return False, f"Action {action.action_type.value} not allowed"
        if action.target and action.target not in self.available_services:
            return False, f"Invalid target: {action.target}"
        return True, "Valid"

class ActionSpace:
    def __init__(self, config: Dict[str, Any], available_services: List[str]):
        self.config = config
        self.available_services = available_services
        self.id_to_action = {}
        self._build_mapping()
        self.validator = ActionValidator(config, available_services)

    def _build_mapping(self):
        idx = 0
        action_types = self.config.get('actions', {}).get('types', [])
        for at_str in action_types:
            at = ActionType(at_str)
            if at in [ActionType.MARK_RESOLVED, ActionType.ESCALATE_INCIDENT]:
                self.id_to_action[idx] = f"{at.value}"
                idx += 1
            else:
                for service in self.available_services:
                    self.id_to_action[idx] = f"{at.value} on {service}"
                    idx += 1
        self.action_space_size = idx

    def get_action_space_size(self) -> int:
        return self.action_space_size

    def get_action(self, action_id: int) -> Action:
        desc = self.id_to_action.get(action_id, "mark_resolved")
        parts = desc.split(" on ")
        at = ActionType(parts[0])
        target = parts[1] if len(parts) > 1 else None
        return Action(at, target)

    def get_action_mask(self, state_summary: Dict) -> List[float]:
        # Simplify: all actions are valid for now unless incident is resolved
        mask = [1.0] * self.action_space_size
        if state_summary.get('incident_resolved'):
            mask = [0.0] * self.action_space_size
        return mask