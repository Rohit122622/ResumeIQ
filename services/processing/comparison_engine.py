"""
Candidate Comparison Engine — Compare two candidates across all dimensions.

Produces structured comparison with recruiter justification:
  Skill, Experience, Behavioral, Platform, Score comparisons.

Pure computation — NO LLM calls. Uses existing ranking data.
"""

import logging

logger = logging.getLogger(__name__)


class CandidateComparisonEngine:
    """Compare two candidates across all scoring dimensions with justification."""

    def compare(self, candidate_a, candidate_b):
        """
        Compare two candidate result dicts across all dimensions.

        Args:
            candidate_a: dict with scores, skills, etc. for Candidate A
            candidate_b: dict with scores, skills, etc. for Candidate B

        Returns:
            dict with winner, per-dimension comparisons, recommendation, justification
        """
        name_a = candidate_a.get("name", candidate_a.get("filename", "Candidate A"))
        name_b = candidate_b.get("name", candidate_b.get("filename", "Candidate B"))

        # ── Score Comparison ──
        score_comparison = self._compare_scores(candidate_a, candidate_b)

        # ── Skill Comparison ──
        skill_comparison = self._compare_skills(candidate_a, candidate_b)

        # ── Experience Comparison ──
        experience_comparison = self._compare_experience(candidate_a, candidate_b)

        # ── Behavioral Comparison ──
        behavioral_comparison = self._compare_behavioral(candidate_a, candidate_b)

        # ── Platform Comparison ──
        platform_comparison = self._compare_platform(candidate_a, candidate_b)

        # ── Determine Winner ──
        a_wins = 0
        b_wins = 0
        for dimension in [score_comparison, skill_comparison, experience_comparison,
                          behavioral_comparison, platform_comparison]:
            w = dimension.get("winner", "tie")
            if w == "a":
                a_wins += 1
            elif w == "b":
                b_wins += 1

        if a_wins > b_wins:
            winner = "a"
            winner_name = name_a
        elif b_wins > a_wins:
            winner = "b"
            winner_name = name_b
        else:
            # Tie-break: use combined score
            score_a = candidate_a.get("combined_score", candidate_a.get("score", 0))
            score_b = candidate_b.get("combined_score", candidate_b.get("score", 0))
            if score_a >= score_b:
                winner = "a"
                winner_name = name_a
            else:
                winner = "b"
                winner_name = name_b

        # ── Recommendation ──
        recommendation = f"{winner_name} is the stronger candidate"
        justification = self._build_justification(
            name_a, name_b, winner, a_wins, b_wins,
            score_comparison, skill_comparison, behavioral_comparison
        )

        return {
            "candidate_a_name": name_a,
            "candidate_b_name": name_b,
            "winner": winner,
            "winner_name": winner_name,
            "dimensions_won": {"a": a_wins, "b": b_wins},
            "score_comparison": score_comparison,
            "skill_comparison": skill_comparison,
            "experience_comparison": experience_comparison,
            "behavioral_comparison": behavioral_comparison,
            "platform_comparison": platform_comparison,
            "recommendation": recommendation,
            "justification": justification,
        }

    def _compare_scores(self, a, b):
        """Compare all numeric scores."""
        metrics = {}
        score_keys = [
            ("combined_score", "Final Score"),
            ("ats_score", "ATS Score"),
            ("semantic_score", "Semantic Score"),
            ("skill_match_pct", "Skill Match"),
            ("behavioral_score", "Behavioral Score"),
            ("platform_score", "Platform Score"),
        ]

        a_total = 0
        b_total = 0

        for key, label in score_keys:
            val_a = a.get(key, 0) or 0
            val_b = b.get(key, 0) or 0
            metrics[key] = {
                "label": label,
                "a": val_a,
                "b": val_b,
                "diff": round(val_a - val_b, 1),
                "better": "a" if val_a > val_b else ("b" if val_b > val_a else "tie"),
            }
            a_total += val_a
            b_total += val_b

        # Agent score (0-10 scale)
        agent_a = a.get("agent_score")
        agent_b = b.get("agent_score")
        if agent_a is not None or agent_b is not None:
            val_a = (agent_a or 0) * 10
            val_b = (agent_b or 0) * 10
            metrics["agent_score"] = {
                "label": "Agent Score",
                "a": val_a,
                "b": val_b,
                "diff": round(val_a - val_b, 1),
                "better": "a" if val_a > val_b else ("b" if val_b > val_a else "tie"),
            }

        winner = "a" if a_total > b_total else ("b" if b_total > a_total else "tie")
        return {"metrics": metrics, "winner": winner}

    def _compare_skills(self, a, b):
        """Compare matched and missing skills."""
        skills_a = set(s.lower() for s in a.get("matched_skills", []))
        skills_b = set(s.lower() for s in b.get("matched_skills", []))
        missing_a = set(s.lower() for s in a.get("missing_skills", []))
        missing_b = set(s.lower() for s in b.get("missing_skills", []))

        shared = skills_a & skills_b
        only_a = skills_a - skills_b
        only_b = skills_b - skills_a

        winner = "tie"
        if len(skills_a) > len(skills_b) and len(missing_a) <= len(missing_b):
            winner = "a"
        elif len(skills_b) > len(skills_a) and len(missing_b) <= len(missing_a):
            winner = "b"
        elif len(skills_a) > len(skills_b):
            winner = "a"
        elif len(skills_b) > len(skills_a):
            winner = "b"

        return {
            "shared": sorted(shared),
            "only_a": sorted(only_a),
            "only_b": sorted(only_b),
            "a_matched_count": len(skills_a),
            "b_matched_count": len(skills_b),
            "a_missing_count": len(missing_a),
            "b_missing_count": len(missing_b),
            "winner": winner,
        }

    def _compare_experience(self, a, b):
        """Compare experience-related signals."""
        # Try to get from agent evidence or parsed data
        a_years = a.get("experience_years", 0)
        b_years = b.get("experience_years", 0)
        a_projects = a.get("project_count", 0)
        b_projects = b.get("project_count", 0)

        a_exp_total = a_years * 2 + a_projects
        b_exp_total = b_years * 2 + b_projects

        winner = "a" if a_exp_total > b_exp_total else ("b" if b_exp_total > a_exp_total else "tie")

        return {
            "a_years": a_years,
            "b_years": b_years,
            "a_projects": a_projects,
            "b_projects": b_projects,
            "winner": winner,
        }

    def _compare_behavioral(self, a, b):
        """Compare behavioral scores and breakdowns."""
        a_score = a.get("behavioral_score", 50)
        b_score = b.get("behavioral_score", 50)

        a_breakdown = a.get("behavioral_breakdown", {})
        b_breakdown = b.get("behavioral_breakdown", {})

        category_comparison = {}
        for cat in set(list(a_breakdown.keys()) + list(b_breakdown.keys())):
            val_a = a_breakdown.get(cat, 0)
            val_b = b_breakdown.get(cat, 0)
            category_comparison[cat] = {
                "a": val_a, "b": val_b,
                "better": "a" if val_a > val_b else ("b" if val_b > val_a else "tie"),
            }

        winner = "a" if a_score > b_score else ("b" if b_score > a_score else "tie")

        return {
            "a_score": a_score,
            "b_score": b_score,
            "categories": category_comparison,
            "winner": winner,
        }

    def _compare_platform(self, a, b):
        """Compare platform activity scores."""
        a_score = a.get("platform_score", 50)
        b_score = b.get("platform_score", 50)
        a_platforms = a.get("platforms_detected", {})
        b_platforms = b.get("platforms_detected", {})

        winner = "a" if a_score > b_score else ("b" if b_score > a_score else "tie")

        return {
            "a_score": a_score,
            "b_score": b_score,
            "a_platforms": list(a_platforms.keys()),
            "b_platforms": list(b_platforms.keys()),
            "winner": winner,
        }

    @staticmethod
    def _build_justification(name_a, name_b, winner, a_wins, b_wins,
                              score_cmp, skill_cmp, behavioral_cmp):
        """Build a recruiter-friendly justification paragraph."""
        winner_name = name_a if winner == "a" else name_b
        loser_name = name_b if winner == "a" else name_a

        parts = [f"{winner_name} outperforms {loser_name} in {max(a_wins, b_wins)} out of 5 evaluated dimensions."]

        # Score context
        final_metrics = score_cmp.get("metrics", {}).get("combined_score", {})
        if final_metrics:
            parts.append(
                f"Overall score: {final_metrics['a']} ({name_a}) vs {final_metrics['b']} ({name_b})."
            )

        # Skill context
        a_matched = skill_cmp.get("a_matched_count", 0)
        b_matched = skill_cmp.get("b_matched_count", 0)
        if a_matched != b_matched:
            parts.append(
                f"Skill coverage: {name_a} matched {a_matched} skills, "
                f"{name_b} matched {b_matched} skills."
            )

        # Behavioral context
        a_beh = behavioral_cmp.get("a_score", 50)
        b_beh = behavioral_cmp.get("b_score", 50)
        if abs(a_beh - b_beh) >= 10:
            higher = name_a if a_beh > b_beh else name_b
            parts.append(f"{higher} demonstrates stronger behavioral signals.")

        return " ".join(parts)
