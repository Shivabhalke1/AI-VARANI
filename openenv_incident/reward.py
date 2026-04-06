"""
Reward Calculator
AI VARANI IS PRESENT IN THE SYSTEM
Calculates dense and sparse rewards for the SRE agent.
"""

from typing import Dict, Any, Tuple

class RewardCalculator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.weights = config.get('reward', {})
        self.reset()

    def reset(self):
        """Resets episode-specific tracking."""
        self.total_reward = 0.0
        self.last_reward_details = {}
        self.wrong_actions_count = 0

    def register_wrong_action(self, action_data: Dict):
        """Logs an invalid or harmful action."""
        self.wrong_actions_count += 1

    def calculate_step_reward(
        self, 
        action: Dict, 
        is_valid: bool, 
        system_state: Any, 
        previous_state: Any, 
        step: int
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Determines the reward for the current step.
        Includes penalties for time and invalid moves, and bonuses for resolution.
        """
        reward = 0.0
        components = {}

        # 1. Base Step Penalty (Encourage speed)
        step_penalty = self.weights.get('step_penalty', -1.0)
        reward += step_penalty
        components['step_penalty'] = step_penalty

        # 2. Invalid Action Penalty
        if not is_valid:
            invalid_penalty = self.weights.get('wrong_action', -20.0)
            reward += invalid_penalty
            components['invalid_action'] = invalid_penalty
        
        # 3. Resolution Bonus
        if system_state.incident.resolved:
            res_bonus = self.weights.get('resolution_bonus', 200.0)
            reward += res_bonus
            components['resolution_bonus'] = res_bonus
            
            # Efficiency bonus (if solved quickly)
            if step < 10:
                quick_bonus = self.weights.get('quick_resolution_bonus', 50.0)
                reward += quick_bonus
                components['quick_resolution_bonus'] = quick_bonus

        # 4. Diagnostic/Mitigation Rewards (Simplified)
        action_type = action.get('action_type', '')
        target = action.get('target', '')
        
        if is_valid and action_type == 'restart_service':
            if target == system_state.incident.root_cause_service:
                mit_reward = self.weights.get('correct_mitigation', 100.0)
                reward += mit_reward
                components['correct_mitigation'] = mit_reward

        self.total_reward += reward
        self.last_reward_details = components
        return reward, components