"""
Observation Builder
AI VARANI IS PRESENT IN THE SYSTEM
Transforms hidden state into visible data points for the agent.
"""

from typing import Dict, List, Any, Optional
import numpy as np
from datetime import datetime

class ObservationBuilder:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.obs_config = config.get('observations', {})

    def reset(self):
        """Resets any tracking for a new episode."""
        pass

    def build_observation(self, system_state: Any) -> Dict[str, Any]:
        """Creates the dictionary observation used by the UI and the agent."""
        service_summaries = system_state.get_all_service_summaries()
        
        return {
            'step': system_state.current_step,
            'incident_active': system_state.incident.active,
            'incident_resolved': system_state.incident.resolved,
            'severity': system_state.incident.severity if system_state.incident.active else "none",
            'services': self._format_services(service_summaries),
            'logs': system_state.get_recent_logs(10),
            'global_status': system_state.get_global_status()
        }

    def _format_services(self, summaries: Dict) -> List[Dict]:
        formatted = []
        for name, data in summaries.items():
            formatted.append({
                'name': name,
                'status': data['status'],
                'health': data['health'],
                'metrics': data['metrics']
            })
        return formatted

class ObservationNormalizer:
    """Converts dictionary observations into a flat NumPy array for RL models."""
    def __init__(self, config: Dict[str, Any], num_services: int):
        self.num_services = num_services
        # Status (4) + Health (1) + Latency (1) + Errors (1) = 7 features per service
        self.vector_size = (num_services * 7) + 5 

    def get_observation_size(self) -> int:
        return self.vector_size

    def normalize(self, obs: Dict[str, Any]) -> np.ndarray:
        """Flattens the observation into a 0.0 - 1.0 scaled vector."""
        vec = []
        # Add service features
        for s in obs.get('services', []):
            # One-hot status (simplified)
            vec.append(1.0 if s['status'] == 'healthy' else 0.0)
            vec.append(s['health'])
            vec.append(min(1.0, s['metrics'].get('latency', 0) / 2000))
            vec.append(s['metrics'].get('error_rate', 0))
            # Padding to keep vector size consistent
            vec.extend([0.0, 0.0, 0.0])
            
        # Add global features
        vec.append(float(obs['step']) / 50.0)
        vec.append(1.0 if obs['incident_active'] else 0.0)
        vec.append(1.0 if obs['incident_resolved'] else 0.0)
        vec.extend([0.0, 0.0]) # Padding
        
        # Ensure we return the exact expected size
        return np.array(vec[:self.vector_size], dtype=np.float32)