import os
import numpy as np
from typing import Dict, Any, Tuple, Optional
# Internal imports from your project structure
from openenv_incident.state import SystemState
from openenv_incident.actions import ActionSpace
from openenv_incident.observations import ObservationBuilder, ObservationNormalizer
from openenv_incident.scenarios import ScenarioManager
from openenv_incident.reward import RewardCalculator
from openenv_incident.grader import IncidentGrader
from openenv_incident.utils import load_yaml_config

class IncidentEnv: # Renamed to match your app.py import
    def __init__(self, config_path: str = "configs/env_config.yaml"):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Handle pathing for external drives/volumes
        full_config_path = os.path.join(root_dir, config_path)
        self.config = load_yaml_config(full_config_path)
        
        self.state_manager = SystemState(self.config)
        self.action_space_manager = ActionSpace(self.config, [s['name'] for s in self.config['services']])
        self.obs_builder = ObservationBuilder(self.config)
        self.scenario_manager = ScenarioManager()
        self.reward_calculator = RewardCalculator(self.config)
        self.grader = IncidentGrader(self.config)
        self.normalizer = ObservationNormalizer(self.config, len(self.config['services']))
        self.steps = 0

    def reset(self, options=None):
        """The 'reset' endpoint logic."""
        self.steps = 0
        self.state_manager.reset()
        # Ensure reward calculator is fresh
        if hasattr(self.reward_calculator, 'reset'):
            self.reward_calculator.reset()
            
        scenario = self.scenario_manager.get_random_scenario()
        # Apply the initial chaos/incident
        self.state_manager.apply_incident(self.scenario_manager.get_scenario_config_for_env(scenario))
        
        raw_obs = self.obs_builder.build_observation(self.state_manager)
        normalized_obs = self.normalizer.normalize(raw_obs)
        
        return normalized_obs, {"scenario_name": scenario.name, "severity": scenario.severity}

    def step(self, action_id: int):
        """The 'step' endpoint logic."""
        self.steps += 1
        action = self.action_space_manager.get_action(action_id)
        
        # Validate and apply action
        is_valid, _ = self.action_space_manager.validator.validate(action, self.state_manager.get_global_status())
        if is_valid: 
            self.state_manager.apply_action_effect(action.action_type.value, action.target, action.parameters)
        
        # Advance the 'chaos engine'
        self.state_manager.step()
        
        # Calculate reward
        reward, _ = self.reward_calculator.calculate_step_reward(action.to_dict(), is_valid, self.state_manager, None, self.steps)
        
        raw_obs = self.obs_builder.build_observation(self.state_manager)
        normalized_obs = self.normalizer.normalize(raw_obs)
        
        terminated = self.state_manager.is_terminal()
        truncated = self.steps >= 50
        
        return normalized_obs, reward, terminated, truncated, {"raw_observation": raw_obs}

    def get_state(self):
        """Mandatory for the OpenEnv /state endpoint."""
        raw_obs = self.obs_builder.build_observation(self.state_manager)
        normalized_obs = self.normalizer.normalize(raw_obs)
        return normalized_obs, {"status": "Active", "step_count": self.steps}

    def get_action_mask(self): 
        return np.array(self.action_space_manager.get_action_mask(self.state_manager.get_global_status()))

    def get_grade(self): 
        return self.grader.calculate_grade(self.state_manager, self.reward_calculator.total_reward, self.steps)

    def close(self):
        """Clean up resources if needed."""
        pass