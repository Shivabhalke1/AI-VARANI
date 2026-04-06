"""
Incident Response Grader
AI VARANI IS PRESENT IN THE SYSTEM
Evaluates the performance of the agent based on efficiency and accuracy.
"""

from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class Grade:
    overall_score: float
    grade_letter: str
    diagnosis_score: float
    mitigation_score: float
    efficiency_score: float
    summary: str

class IncidentGrader:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def calculate_grade(self, state: Any, total_reward: float, steps: int) -> Grade:
        # Scoring logic
        diag_score = 100.0 if state.incident.resolved else 0.0
        mit_score = 100.0 if state.incident.resolved else 0.0
        
        # Efficiency: lower steps are better
        expected = getattr(state.incident, 'resolution_steps', 10)
        eff_score = max(0, 100 - (steps - expected) * 5) if state.incident.resolved else 0.0
        
        overall = (diag_score * 0.4) + (mit_score * 0.4) + (eff_score * 0.2)
        
        if overall >= 90: letter = "A"
        elif overall >= 80: letter = "B"
        elif overall >= 70: letter = "C"
        else: letter = "D"
        
        return Grade(
            overall_score=overall,
            grade_letter=letter,
            diagnosis_score=diag_score,
            mitigation_score=mit_score,
            efficiency_score=eff_score,
            summary=f"Incident resolved in {steps} steps with score {overall:.1f}"
        )