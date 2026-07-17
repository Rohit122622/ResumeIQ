"""
Dashboard Metrics — Aggregates recruiter-level insights from bulk screening.

Generates:
  - Top Skills Found (across all candidates)
  - Most Missing Skills
  - Average Candidate Score (overall + per dimension)
  - Score Distribution data
  - Behavioral Insights (average per category)
  - Platform Insights (% with GitHub, LinkedIn, etc.)

Pure computation — NO LLM calls.
"""

import logging
from collections import Counter

logger = logging.getLogger(__name__)


def generate_dashboard_metrics(ranking_results):
    """
    Aggregate recruiter dashboard metrics from bulk screening results.

    Args:
        ranking_results: dict from screen_resumes() (enriched with behavioral/platform)

    Returns:
        dict with top_skills, missing_skills, averages, distributions,
        behavioral_insights, platform_insights
    """
    top_candidates = ranking_results.get("top_candidates", [])
    all_results = ranking_results.get("all_results", [])

    # Use the richer data source
    candidates = top_candidates if top_candidates else all_results
    total = len(candidates) or 1  # avoid division by zero

    # ── Top Skills Found ──
    skill_counter = Counter()
    for c in candidates:
        for skill in c.get("matched_skills", []):
            if isinstance(skill, str) and skill.strip():
                skill_counter[skill.strip().lower()] += 1
    top_skills = skill_counter.most_common(10)

    # ── Most Missing Skills ──
    missing_counter = Counter()
    for c in candidates:
        for skill in c.get("missing_skills", []):
            if isinstance(skill, str) and skill.strip():
                missing_counter[skill.strip().lower()] += 1
    most_missing = missing_counter.most_common(10)

    # ── Average Scores ──
    def _avg(key, source=None):
        src = source or candidates
        values = [c.get(key, 0) or 0 for c in src]
        return round(sum(values) / max(len(values), 1), 1)

    averages = {
        "overall": _avg("combined_score", all_results) if all_results else _avg("combined_score"),
        "ats": _avg("ats_score"),
        "semantic": _avg("semantic_score"),
        "skill_match": _avg("skill_match_pct"),
        "behavioral": _avg("behavioral_score"),
        "platform": _avg("platform_score"),
    }

    # Agent score average (only where available, 0-10 scale)
    agent_scores = [c.get("agent_score", 0) for c in candidates if c.get("agent_score") is not None]
    averages["agent"] = round(sum(agent_scores) / max(len(agent_scores), 1), 1) if agent_scores else 0

    # ── Score Distribution ──
    score_ranges = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for c in (all_results or candidates):
        s = c.get("combined_score", 0) or 0
        if s <= 20:
            score_ranges["0-20"] += 1
        elif s <= 40:
            score_ranges["21-40"] += 1
        elif s <= 60:
            score_ranges["41-60"] += 1
        elif s <= 80:
            score_ranges["61-80"] += 1
        else:
            score_ranges["81-100"] += 1

    # ── Behavioral Insights ──
    behavioral_insights = {}
    behavioral_categories = [
        "communication", "leadership", "teamwork", "problem_solving",
        "ownership", "adaptability", "growth_mindset", "mentorship"
    ]
    for cat in behavioral_categories:
        values = []
        for c in candidates:
            breakdown = c.get("behavioral_breakdown", {})
            if cat in breakdown:
                values.append(breakdown[cat])
        if values:
            behavioral_insights[cat] = {
                "average": round(sum(values) / len(values), 1),
                "max": round(max(values), 1),
                "candidates_with_signal": sum(1 for v in values if v > 2),
            }
        else:
            behavioral_insights[cat] = {
                "average": 0, "max": 0, "candidates_with_signal": 0,
            }

    # ── Platform Insights ──
    platform_types = ["github", "linkedin", "kaggle", "hackerrank", "leetcode",
                      "codechef", "geeksforgeeks", "portfolio"]
    platform_insights = {}
    for ptype in platform_types:
        count = sum(
            1 for c in candidates
            if ptype in c.get("platforms_detected", {})
        )
        platform_insights[ptype] = {
            "count": count,
            "percentage": round(count / total * 100, 1),
        }

    # ── Top / Bottom Gap ──
    sorted_by_score = sorted(
        (all_results or candidates),
        key=lambda c: c.get("combined_score", 0) or 0,
        reverse=True
    )
    top_score = sorted_by_score[0].get("combined_score", 0) if sorted_by_score else 0
    bottom_score = sorted_by_score[-1].get("combined_score", 0) if sorted_by_score else 0
    gap_analysis = {
        "top_score": top_score,
        "bottom_score": bottom_score,
        "gap": round(top_score - bottom_score, 1),
        "top_name": sorted_by_score[0].get("name", "Top") if sorted_by_score else "",
        "bottom_name": sorted_by_score[-1].get("name", "Bottom") if sorted_by_score else "",
    }

    return {
        "top_skills": top_skills,
        "most_missing_skills": most_missing,
        "averages": averages,
        "score_distribution": score_ranges,
        "behavioral_insights": behavioral_insights,
        "platform_insights": platform_insights,
        "gap_analysis": gap_analysis,
        "total_candidates": len(all_results or candidates),
    }
