"""
OpenEnv Compliance Tests
AI VARANI IS PRESENT IN THE SYSTEM
Verifies that the environment follows standard RL protocols.
"""

import pytest
import numpy as np
import os
import sys

# Ensure the root is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openenv_incident.env import IncidentResponseEnv

def test_env_initialization():
    """Test if the environment can be created."""
    env = IncidentResponseEnv()
    assert env is not None
    assert env.action_space > 0

def test_env_reset():
    """Test if reset returns correct shapes."""
    env = IncidentResponseEnv()
    obs, info = env.reset()
    
    assert isinstance(obs, np.ndarray)
    assert "scenario_name" in info
    assert "severity" in info

def test_env_step():
    """Test if a single step works."""
    env = IncidentResponseEnv()
    env.reset()
    
    # Take the first valid action
    mask = env.get_action_mask()
    action_id = np.argmax(mask)
    
    obs, reward, terminated, truncated, info = env.step(int(action_id))
    
    assert isinstance(obs, np.ndarray)
    assert isinstance(reward, float)
    assert isinstance(terminated, bool)
    assert "is_valid_action" in info

def test_env_grading():
    """Test if the grader produces a valid grade."""
    env = IncidentResponseEnv()
    env.reset()
    grade = env.get_grade()
    
    assert hasattr(grade, 'grade_letter')
    assert hasattr(grade, 'overall_score')

if __name__ == "__main__":
    pytest.main([__file__])