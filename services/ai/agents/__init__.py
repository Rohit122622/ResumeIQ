"""
Multi-Agent System for Nexus CV Bulk Intelligence.

Agents:
- SkillAgent: Rule-based skill extraction and matching (NO LLM)
- ExperienceAgent: Experience evaluation (1 LLM call max)
- ATSAgent: Wrapper around ATS scorer (NO LLM)
- DecisionAgent: ReAct loop for final scoring (max 2 iterations)
- PlatformActivityAgent: Platform URL/activity detection (NO LLM)
- BehavioralSignalAgent: Behavioral soft-skill evaluation (NO LLM)
"""

from services.ai.agents.skill_agent import SkillAgent
from services.ai.agents.experience_agent import ExperienceAgent
from services.ai.agents.ats_agent import ATSAgent
from services.ai.agents.decision_agent import DecisionAgent
from services.ai.agents.platform_agent import PlatformActivityAgent
from services.ai.agents.behavioral_agent import BehavioralSignalAgent

__all__ = [
    "SkillAgent", "ExperienceAgent", "ATSAgent", "DecisionAgent",
    "PlatformActivityAgent", "BehavioralSignalAgent",
]
