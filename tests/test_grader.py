cat > tests/test_grader.py << 'EOF'
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv_incident.env import IncidentResponseEnv
from openenv_incident.grader import IncidentGrader, GradeReport


class TestGradeReport(unittest.TestCase):
    
    def test_grade_report_creation(self):
        report = GradeReport(
            episode_id="TEST001",
            scenario_name="Test Scenario",
            difficulty="medium",
            timestamp="2024-01-01T00:00:00"
        )
        self.assertIsNotNone(report)
        self.assertEqual(report.episode_id, "TEST001")
        
    def test_grade_letter_calculation(self):
        report = GradeReport(
            episode_id="TEST001", scenario_name="Test",
            difficulty="medium", timestamp="2024-01-01T00:00:00"
        )
        report.overall_score = 95
        self.assertEqual(report.compute_grade_letter(), "A+")
        
        report.overall_score = 85
        self.assertEqual(report.compute_grade_letter(), "A")
        
        report.overall_score = 75
        self.assertEqual(report.compute_grade_letter(), "B+")
        
        report.overall_score = 65
        self.assertEqual(report.compute_grade_letter(), "B-")
        
        report.overall_score = 55
        self.assertEqual(report.compute_grade_letter(), "C")
        
        report.overall_score = 45
        self.assertEqual(report.compute_grade_letter(), "D")
        
        report.overall_score = 30
        self.assertEqual(report.compute_grade_letter(), "F")
        
    def test_grade_report_to_dict(self):
        report = GradeReport(
            episode_id="TEST001", scenario_name="Test",
            difficulty="hard", timestamp="2024-01-01T00:00:00"
        )
        report.overall_score = 85.5
        report_dict = report.to_dict()
        self.assertIn('episode_id', report_dict)
        self.assertIn('overall_score', report_dict)


class TestIncidentGrader(unittest.TestCase):
    
    def setUp(self):
        self.env = IncidentResponseEnv()
        self.grader = IncidentGrader(self.env.config)
        
    def test_grader_initialization(self):
        self.assertIsNotNone(self.grader)
        self.assertIn('root_cause', self.grader.grading_weights)
        
    def test_full_grade_generation(self):
        self.env.reset()
        for _ in range(3):
            valid_actions = self.env.get_valid_actions()
            if valid_actions:
                self.env.step(valid_actions[0])
                
        grade = self.grader.grade_episode(
            self.env.system_state, self.env.action_history,
            self.env.current_scenario_config, self.env.episode_return
        )
        
        self.assertIsNotNone(grade)
        self.assertIsNotNone(grade.overall_score)
        self.assertIsNotNone(grade.grade_letter)
        
    def test_grade_summary(self):
        report = GradeReport(
            episode_id="TEST001", scenario_name="Test",
            difficulty="medium", timestamp="2024-01-01T00:00:00"
        )
        report.overall_score = 88.5
        report.grade_letter = "A-"
        report.resolved_successfully = True
        
        summary = self.grader.get_grade_summary(report)
        self.assertIn('overall_score', summary)
        self.assertIn('grade_letter', summary)


if __name__ == '__main__':
    unittest.main()
EOF