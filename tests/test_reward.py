cat > tests/test_reward.py << 'EOF'
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv_incident.env import IncidentResponseEnv
from openenv_incident.reward import RewardCalculator


class TestRewardCalculator(unittest.TestCase):
    
    def setUp(self):
        self.env = IncidentResponseEnv()
        self.reward_calc = RewardCalculator(self.env.config)
        
    def test_reward_calculator_initialization(self):
        self.assertIsNotNone(self.reward_calc)
        self.assertIsNotNone(self.reward_calc.reward_weights)
        
    def test_step_penalty_applied(self):
        self.env.reset()
        self.reward_calc.reset()
        
        valid_actions = self.env.get_valid_actions()
        action = valid_actions[0] if valid_actions else 0
        action_obj = self.env.action_space_obj.get_action(action)
        action_dict = action_obj.to_dict() if action_obj else {'action_type': 'inspect_logs', 'target': 'api_gateway'}
        
        reward, details = self.reward_calc.calculate_step_reward(
            action_dict, True, self.env.system_state, None, 1
        )
        
        self.assertLess(reward, 0)
        self.assertIn('step_penalty', details['components'])
        
    def test_wrong_action_penalty(self):
        self.env.reset()
        self.reward_calc.reset()
        
        action_dict = {'action_type': 'invalid_action', 'target': 'none'}
        reward, details = self.reward_calc.calculate_step_reward(
            action_dict, False, self.env.system_state, None, 1
        )
        
        self.assertIn('invalid_action', details['components'])
        self.assertLess(details['components']['invalid_action'], 0)
        
    def test_episode_reward_calculation(self):
        self.env.reset()
        self.reward_calc.reset()
        
        for _ in range(3):
            valid_actions = self.env.get_valid_actions()
            if valid_actions:
                action = valid_actions[0]
                action_obj = self.env.action_space_obj.get_action(action)
                if action_obj:
                    self.env.step(action)
                    
        episode_reward, breakdown = self.reward_calc.calculate_episode_reward(
            self.env.system_state, self.env.step_count,
            self.env.system_state.incident.resolved, False
        )
        
        self.assertIsInstance(episode_reward, float)
        self.assertIsInstance(breakdown, dict)
        
    def test_reward_calculator_reset(self):
        self.reward_calc.reset()
        self.assertEqual(len(self.reward_calc.correct_diagnoses_made), 0)
        self.assertEqual(len(self.reward_calc.wrong_actions_taken), 0)
        
    def test_action_efficiency_score(self):
        score = self.reward_calc.get_action_efficiency_score(10, 7)
        self.assertEqual(score, 0.7)
        
        score = self.reward_calc.get_action_efficiency_score(0, 0)
        self.assertEqual(score, 0.0)


if __name__ == '__main__':
    unittest.main()
EOF