"""
Behavioral Signal Agent — Evaluates soft-skill and behavioral signals from resume text.

Analyzes 8 behavioral categories using keyword and phrase pattern matching:
  Communication, Leadership, Teamwork, Problem Solving,
  Ownership/Initiative, Adaptability, Growth Mindset, Mentorship

Generates a Behavioral Score (0–100) with per-category breakdown.
NO LLM calls — pure regex and NLP pattern matching.

Existing ExperienceAgent is NOT modified — this agent is fully additive.
"""

import re
import logging

logger = logging.getLogger(__name__)


# ── Behavioral Category Patterns ──
# Each category maps to a list of regex patterns with weighted relevance.
# Weight: how many points each match contributes (before category cap).

_BEHAVIORAL_CATEGORIES = {
    "communication": {
        "max_score": 12.5,
        "patterns": [
            (re.compile(r"\b(?:present(?:ed|ing)?|presentation)\b", re.IGNORECASE), 3.0),
            (re.compile(r"\b(?:communicat(?:ed|ing|ion)|conveyed)\b", re.IGNORECASE), 3.0),
            (re.compile(r"\b(?:document(?:ed|ing|ation)|wrote|written|authored)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:stakeholder|client[\s\-]facing|cross[\s\-]team)\b", re.IGNORECASE), 2.0),
            (re.compile(r"\b(?:report(?:ed|ing)?|briefing|articulated)\b", re.IGNORECASE), 1.5),
            (re.compile(r"\b(?:technical\s*writ(?:ing|er)|blog|published)\b", re.IGNORECASE), 2.0),
            (re.compile(r"\b(?:facilitated|moderated)\b", re.IGNORECASE), 2.0),
        ],
    },
    "leadership": {
        "max_score": 12.5,
        "patterns": [
            (re.compile(r"\b(?:led|lead(?:ing)?|headed)\b", re.IGNORECASE), 3.0),
            (re.compile(r"\b(?:managed|manager|management)\b", re.IGNORECASE), 3.0),
            (re.compile(r"\b(?:supervised|supervisor|oversaw)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:directed|director|orchestrated)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:team\s*lead|tech\s*lead|principal)\b", re.IGNORECASE), 3.0),
            (re.compile(r"\b(?:championed|drove\s+adoption|spearheaded)\b", re.IGNORECASE), 2.0),
            (re.compile(r"\b(?:founded|co[\s\-]?founded)\b", re.IGNORECASE), 2.5),
        ],
    },
    "teamwork": {
        "max_score": 12.5,
        "patterns": [
            (re.compile(r"\b(?:collaborat(?:ed|ing|ion))\b", re.IGNORECASE), 3.0),
            (re.compile(r"\b(?:team(?:work|mate|s)?)\b", re.IGNORECASE), 2.0),
            (re.compile(r"\b(?:cross[\s\-]?functional|inter[\s\-]?department)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:worked\s+(?:with|closely|alongside))\b", re.IGNORECASE), 2.0),
            (re.compile(r"\b(?:pair\s*programm(?:ing|ed)|peer\s*review)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:agile|scrum|sprint|standup)\b", re.IGNORECASE), 1.5),
            (re.compile(r"\b(?:coordinated|partnered)\b", re.IGNORECASE), 2.0),
        ],
    },
    "problem_solving": {
        "max_score": 12.5,
        "patterns": [
            (re.compile(r"\b(?:solv(?:ed|ing)|solution)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:debug(?:ged|ging)?|troubleshot|troubleshoot(?:ing)?)\b", re.IGNORECASE), 3.0),
            (re.compile(r"\b(?:resolved|resolution|fixed|addressed)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:optimiz(?:ed|ing|ation)|improv(?:ed|ing))\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:analyz(?:ed|ing)|investigat(?:ed|ing)|diagnos(?:ed|ing))\b", re.IGNORECASE), 2.0),
            (re.compile(r"\b(?:root\s*cause|bottleneck|critical\s*issue)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:refactor(?:ed|ing)?|redesign(?:ed|ing)?)\b", re.IGNORECASE), 2.0),
        ],
    },
    "ownership": {
        "max_score": 12.5,
        "patterns": [
            (re.compile(r"\b(?:initiat(?:ed|ive)|proactiv(?:e|ely))\b", re.IGNORECASE), 3.0),
            (re.compile(r"\b(?:proposed|pitching|pitched)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:drove|driving|spearheaded)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:owned|ownership|accountab(?:le|ility))\b", re.IGNORECASE), 3.0),
            (re.compile(r"\b(?:end[\s\-]?to[\s\-]?end|full[\s\-]?stack\s+ownership)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:independently|self[\s\-]?directed|autonomously)\b", re.IGNORECASE), 2.0),
            (re.compile(r"\b(?:launched|shipped|delivered)\b", re.IGNORECASE), 2.0),
        ],
    },
    "adaptability": {
        "max_score": 12.5,
        "patterns": [
            (re.compile(r"\b(?:adapt(?:ed|ing|ability|able))\b", re.IGNORECASE), 3.0),
            (re.compile(r"\b(?:migrat(?:ed|ing|ion))\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:transition(?:ed|ing)?|pivot(?:ed|ing)?)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:fast[\s\-]?paced|dynamic\s+environment)\b", re.IGNORECASE), 2.0),
            (re.compile(r"\b(?:versatil(?:e|ity)|flexible|multi[\s\-]?disciplin)\b", re.IGNORECASE), 2.0),
            (re.compile(r"\b(?:rapid(?:ly)?|quick(?:ly)?)\s+(?:learn|adopt|ramp)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:wore\s+many\s+hats|generalist)\b", re.IGNORECASE), 1.5),
        ],
    },
    "growth_mindset": {
        "max_score": 12.5,
        "patterns": [
            (re.compile(r"\b(?:learn(?:ed|ing|er)|self[\s\-]?taught)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:certifi(?:ed|cation|cate))\b", re.IGNORECASE), 3.0),
            (re.compile(r"\b(?:course|coursera|udemy|edx|mooc)\b", re.IGNORECASE), 2.0),
            (re.compile(r"\b(?:hackathon|competition|contest)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:research(?:ed|ing)?|paper|thesis|dissertation)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:upskill(?:ed|ing)?|reskill|continuous\s+learn)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:mentor(?:ship)?|conference|workshop)\b", re.IGNORECASE), 2.0),
        ],
    },
    "mentorship": {
        "max_score": 12.5,
        "patterns": [
            (re.compile(r"\b(?:mentor(?:ed|ing)?)\b", re.IGNORECASE), 3.5),
            (re.compile(r"\b(?:train(?:ed|ing)|taught|coaching|coached)\b", re.IGNORECASE), 3.0),
            (re.compile(r"\b(?:onboard(?:ed|ing)?)\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:guided|guid(?:ing|ance))\b", re.IGNORECASE), 2.0),
            (re.compile(r"\b(?:knowledge\s+(?:shar(?:ing|ed)|transfer))\b", re.IGNORECASE), 2.5),
            (re.compile(r"\b(?:code\s*review(?:ed|ing|s)?)\b", re.IGNORECASE), 2.0),
            (re.compile(r"\b(?:intern(?:s|ship)?|junior\s+developer)\b", re.IGNORECASE), 1.5),
        ],
    },
}


class BehavioralSignalAgent:
    """Evaluates behavioral / soft-skill signals from resume text.

    Scores 8 categories: Communication, Leadership, Teamwork,
    Problem Solving, Ownership, Adaptability, Growth Mindset, Mentorship.

    Each category contributes up to 12.5 points for a total max of 100.
    Pure computation — NO LLM calls.

    The existing ExperienceAgent is NOT modified by this agent.
    """

    def evaluate(self, resume_text, parsed_data=None):
        """
        Analyze behavioral signals in resume text.

        Args:
            resume_text: Full resume text
            parsed_data: Pre-parsed resume data (optional, unused currently)

        Returns:
            dict with behavioral_score (0–100), breakdown (per-category),
            top_signals, explanation
        """
        if not resume_text:
            return self._empty_result()

        breakdown = {}
        top_signals = []

        for category, config in _BEHAVIORAL_CATEGORIES.items():
            cat_score = 1.5  # Base score for any non-empty resume (reduced from 3.0)
            max_score = config["max_score"]
            matches_found = []

            for pattern, weight in config["patterns"]:
                matches = pattern.findall(resume_text)
                if matches:
                    # First match gets full weight, subsequent get diminishing returns
                    match_count = len(matches)
                    contribution = weight + (min(match_count - 1, 3) * weight * 0.15)
                    cat_score += contribution
                    matches_found.append(matches[0] if isinstance(matches[0], str) else str(matches[0]))

            cat_score = round(min(cat_score, max_score), 1)
            breakdown[category] = cat_score

        # Calibrated qualitative boost (reduced from 10/10/15/10 to prevent inflation)
        boost = 0.0
        text_lower = resume_text.lower()
        if any(w in text_lower for w in ["led", "managed", "supervised", "directed", "headed", "spearheaded", "manager", "team lead", "tech lead"]):
            boost += 3.0
        if any(w in text_lower for w in ["project", "built", "developed", "created", "designed", "implemented", "deployed", "architected"]):
            boost += 3.0
        if re.search(r"\b\d+%\b", text_lower) or any(w in text_lower for w in ["reduced", "increased", "optimized", "saved", "improved", "throughput", "latency"]):
            boost += 5.0
        if re.search(r"\b\d+\s*(?:k|m|requests|users|transactions|predictions)\b", text_lower):
            boost += 3.0

        # Cap total boost to 10 points spread across categories
        boost = min(boost, 10.0)

        if boost > 0:
            category_boost = boost / len(breakdown)
            for category in breakdown:
                breakdown[category] = round(min(breakdown[category] + category_boost, _BEHAVIORAL_CATEGORIES[category]["max_score"]), 1)

        # Build top signals list using the boosted breakdown
        for category, cat_score in breakdown.items():
            max_score = _BEHAVIORAL_CATEGORIES[category]["max_score"]
            if cat_score >= max_score * 0.5:
                label = category.replace("_", " ").title()
                top_signals.append(f"{label}: {cat_score}/{max_score}")

        behavioral_score = round(sum(breakdown.values()), 1)
        behavioral_score = max(0, min(100, behavioral_score))

        # Build explanation
        strong_areas = [k.replace("_", " ").title() for k, v in breakdown.items()
                        if v >= _BEHAVIORAL_CATEGORIES[k]["max_score"] * 0.6]
        weak_areas = [k.replace("_", " ").title() for k, v in breakdown.items()
                      if v < _BEHAVIORAL_CATEGORIES[k]["max_score"] * 0.25]

        explanation_parts = []
        if strong_areas:
            explanation_parts.append(f"Strong in: {', '.join(strong_areas[:4])}")
        if weak_areas:
            explanation_parts.append(f"Limited signals for: {', '.join(weak_areas[:3])}")

        explanation = f"Behavioral Score: {behavioral_score}/100. " + ". ".join(explanation_parts) if explanation_parts else f"Behavioral Score: {behavioral_score}/100."

        return {
            "behavioral_score": behavioral_score,
            "breakdown": breakdown,
            "top_signals": top_signals,
            "strong_areas": strong_areas,
            "weak_areas": weak_areas,
            "explanation": explanation,
        }

    def _empty_result(self):
        """Return empty result when no text is available."""
        breakdown = {cat: 0.0 for cat in _BEHAVIORAL_CATEGORIES}
        return {
            "behavioral_score": 0.0,
            "breakdown": breakdown,
            "top_signals": [],
            "strong_areas": [],
            "weak_areas": list(_BEHAVIORAL_CATEGORIES.keys()),
            "explanation": "Behavioral Score: 0/100. No resume text available for analysis.",
        }
