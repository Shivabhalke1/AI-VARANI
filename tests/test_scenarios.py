cat > tests/test_scenarios.py << 'EOF'
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv_incident.scenarios import ScenarioManager, Scenario, DifficultyLevel
from openenv_incident.env import IncidentResponseEnv


class TestScenario(unittest.TestCase):
    
    def test_scenario_creation(self):
        scenario = Scenario(
            id="test_scenario",
            name="Test Incident",
            severity="high",
            difficulty=DifficultyLevel.MEDIUM,
            root_cause_service="database",
            root_cause_issue="connection_pool_exhaustion",
            root_cause_details="Connection pool too small",
            symptoms=[],
            affected_services=["api_gateway"],
            correct_mitigations=[],
            wrong_actions_penalty=[],
            resolution_steps=4,
            time_to_resolve_steps=8
        )
        self.assertIsNotNone(scenario)
        self.assertEqual(scenario.id, "test_scenario")
        
    def test_scenario_to_dict(self):
        scenario = Scenario(
            id="test_scenario", name="Test", severity="high",
            difficulty=DifficultyLevel.EASY, root_cause_service="db",
            root_cause_issue="issue", root_cause_details="details",
            symptoms=[], affected_services=[], correct_mitigations=[],
            wrong_actions_penalty=[], resolution_steps=3, time_to_resolve_steps=6
        )
        scenario_dict = scenario.to_dict()
        self.assertIn('id', scenario_dict)
        self.assertIn('root_cause', scenario_dict)


class TestScenarioManager(unittest.TestCase):
    
    def setUp(self):
        self.manager = ScenarioManager()
        
    def test_manager_initialization(self):
        self.assertIsNotNone(self.manager)
        self.assertGreater(len(self.manager.scenarios), 0)
        
    def test_get_scenario(self):
        scenario_ids = self.manager.get_scenario_ids()
        if scenario_ids:
            scenario = self.manager.get_scenario(scenario_ids[0])
            self.assertIsNotNone(scenario)
            
    def test_get_random_scenario(self):
        scenario = self.manager.get_random_scenario()
        self.assertIsNotNone(scenario)
        
    def test_get_random_scenario_by_difficulty(self):
        scenario = self.manager.get_random_scenario(difficulty=DifficultyLevel.EASY)
        self.assertEqual(scenario.difficulty, DifficultyLevel.EASY)
        
    def test_get_all_scenarios(self):
        all_scenarios = self.manager.get_all_scenarios()
        self.assertIsInstance(all_scenarios, dict)
        
    def test_get_scenario_ids(self):
        scenario_ids = self.manager.get_scenario_ids()
        self.assertIsInstance(scenario_ids, list)
        self.assertGreater(len(scenario_ids), 0)
        
    def test_generate_random_scenario(self):
        scenario = self.manager.generate_random_scenario()
        self.assertIsNotNone(scenario)
        self.assertTrue(scenario.id.startswith("generated_"))
        
    def test_default_scenarios_exist(self):
        scenario_ids = self.manager.get_scenario_ids()
        expected = ['database_slowdown', 'auth_crash', 'cache_failure']
        for exp in expected:
            self.assertIn(exp, scenario_ids)


class TestScenarioIntegration(unittest.TestCase):
    
    def setUp(self):
        self.env = IncidentResponseEnv()
        
    def test_load_scenario_into_environment(self):
        scenario_ids = self.env.scenario_manager.get_scenario_ids()
        if scenario_ids:
            self.env.reset(options={'scenario_id': scenario_ids[0]})
            self.assertEqual(self.env.current_scenario_id, scenario_ids[0])
            self.assertTrue(self.env.system_state.incident.active)


if __name__ == '__main__':
    unittest.main()
EOF