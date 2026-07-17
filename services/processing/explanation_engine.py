"""
Ranking Explanation Engine — Generates recruiter-friendly explainable AI output.

For every candidate, produces:
  - Strengths & Weaknesses
  - Matched & Missing Requirements
  - Risk Factors
  - Recommendation label
  - Natural language summary (recruiter-friendly)

Pure computation — NO LLM calls. Uses existing scoring data.
"""

import logging

logger = logging.getLogger(__name__)


class RankingExplanationEngine:
    """Generates explainable 'Why Ranked Here' explanations for each candidate."""

    def explain_candidate(self, candidate_data, rank, total_candidates):
        """
        Generate a comprehensive explanation for a candidate's ranking position.

        Args:
            candidate_data: dict with all scores and skills for the candidate
            rank: int — current rank (1-based)
            total_candidates: int — total number of candidates

        Returns:
            dict with strengths, weaknesses, matched_requirements,
            missing_requirements, risk_factors, recommendation, summary
        """
        strengths = []
        weaknesses = []
        risk_factors = []

        # ── Analyze individual scores ──
        semantic = candidate_data.get("semantic_score", 0)
        ats = candidate_data.get("ats_score", 0)
        skill_pct = candidate_data.get("skill_match_pct", 0)
        agent_score = candidate_data.get("agent_score")
        behavioral = candidate_data.get("behavioral_score", 50)
        platform = candidate_data.get("platform_score", 50)
        combined = candidate_data.get("combined_score", candidate_data.get("score", 0))
        confidence = candidate_data.get("confidence", candidate_data.get("agent_confidence", "medium"))

        matched_skills = candidate_data.get("matched_skills", [])
        missing_skills = candidate_data.get("missing_skills", [])

        # ── Strengths ──
        if semantic >= 70:
            strengths.append(f"{semantic}% semantic alignment with job description")
        elif semantic >= 50:
            strengths.append(f"Moderate semantic relevance ({semantic}%)")

        if ats >= 70:
            strengths.append(f"Excellent ATS compatibility ({ats}/100)")
        elif ats >= 50:
            strengths.append(f"Solid ATS score ({ats}/100)")

        if skill_pct >= 60:
            strengths.append(f"High skill match ({skill_pct}% of required skills)")

        if agent_score is not None and agent_score >= 7:
            strengths.append("Strong multi-agent AI evaluation")

        if behavioral >= 70:
            strengths.append(f"Strong behavioral signals (score: {behavioral}/100)")

            # Add behavioral details if breakdown available
            breakdown = candidate_data.get("behavioral_breakdown", {})
            strong_behaviors = [k.replace("_", " ").title()
                                for k, v in breakdown.items() if v >= 8]
            if strong_behaviors:
                strengths.append(f"Key behavioral strengths: {', '.join(strong_behaviors[:3])}")

        if platform >= 70:
            strengths.append(f"Active platform presence (score: {platform}/100)")
            platforms = candidate_data.get("platforms_detected", {})
            if platforms:
                platform_names = [p.title() for p in platforms.keys()]
                strengths.append(f"Platforms: {', '.join(platform_names[:4])}")

        if len(matched_skills) >= 5:
            strengths.append(f"{len(matched_skills)} required skills matched")

        # ── Weaknesses ──
        if semantic < 40:
            weaknesses.append(f"Low semantic alignment with JD ({semantic}%)")

        if ats < 50:
            weaknesses.append(f"Below-average ATS score ({ats}/100)")

        if skill_pct < 40:
            weaknesses.append(f"Limited skill coverage ({skill_pct}%)")

        if agent_score is not None and agent_score < 5:
            weaknesses.append("Weak agent evaluation score")

        if behavioral < 40:
            weaknesses.append(f"Limited behavioral signals detected ({behavioral}/100)")

        if platform < 40:
            weaknesses.append("Minimal platform activity or presence")

        if missing_skills:
            weaknesses.append(f"{len(missing_skills)} required skills missing")

        # ── Risk Factors ──
        if confidence == "low":
            risk_factors.append("Low confidence in scoring — limited data available")

        if semantic < 30 and ats >= 60:
            risk_factors.append("ATS score inflated relative to semantic match — possible keyword stuffing")

        if behavioral < 30:
            risk_factors.append("Very limited behavioral/soft-skill indicators in resume")

        if platform < 30 and platform != 50:  # 50 is neutral
            risk_factors.append("No verifiable platform activity detected")

        if len(missing_skills) > 5:
            risk_factors.append(f"Significant skill gaps: missing {len(missing_skills)} required skills")

        if agent_score is not None and abs(agent_score * 10 - ats) > 30:
            risk_factors.append("Discrepancy between agent and ATS evaluations")

        # ── Recommendation ──
        recommendation = self._compute_recommendation(combined, confidence, len(risk_factors))

        # ── Behavioral Summary ──
        behavioral_summary = self._build_behavioral_summary(candidate_data)

        # ── Platform Summary ──
        platform_summary = self._build_platform_summary(candidate_data)

        # ── Experience Summary ──
        experience_summary = self._build_experience_summary(candidate_data)

        # ── Summary ──
        summary = self._build_summary(
            candidate_data.get("name", f"Candidate #{rank}"),
            rank, total_candidates, combined, strengths, weaknesses,
            missing_skills, recommendation, behavioral_summary, platform_summary
        )

        return {
            "rank": rank,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "matched_requirements": matched_skills,
            "missing_requirements": missing_skills,
            "risk_factors": risk_factors,
            "recommendation": recommendation,
            "summary": summary,
            "confidence": confidence,
            "behavioral_summary": behavioral_summary,
            "platform_summary": platform_summary,
            "experience_summary": experience_summary,
        }

    @staticmethod
    def _compute_recommendation(score, confidence, risk_count):
        """Derive recommendation label from score, confidence, and risks."""
        if score >= 75 and confidence in ("high", "medium") and risk_count <= 1:
            return "Strong Hire"
        elif score >= 60 and risk_count <= 2:
            return "Recommended"
        elif score >= 45:
            return "Consider"
        elif score >= 30:
            return "Below Average"
        else:
            return "Needs Review"

    @staticmethod
    def _build_behavioral_summary(candidate_data):
        """Build a summary of the candidate's behavioral profile."""
        behavioral = candidate_data.get("behavioral_score", 50)
        breakdown = candidate_data.get("behavioral_breakdown", {})

        if not breakdown:
            return f"Behavioral score: {behavioral}/100. No detailed breakdown available."

        strong = [k.replace("_", " ").title() for k, v in breakdown.items() if v >= 8]
        moderate = [k.replace("_", " ").title() for k, v in breakdown.items() if 4 <= v < 8]
        weak = [k.replace("_", " ").title() for k, v in breakdown.items() if v < 4]

        parts = [f"Behavioral score: {behavioral}/100."]
        if strong:
            parts.append(f"Strong signals in: {', '.join(strong[:4])}.")
        if moderate:
            parts.append(f"Moderate signals in: {', '.join(moderate[:3])}.")
        if weak:
            parts.append(f"Limited signals for: {', '.join(weak[:3])}.")

        return " ".join(parts)

    @staticmethod
    def _build_platform_summary(candidate_data):
        """Build a summary of the candidate's platform presence."""
        platform = candidate_data.get("platform_score", 50)
        platforms = candidate_data.get("platforms_detected", {})
        details = candidate_data.get("platform_details", [])

        if not platforms:
            return f"Platform score: {platform}/100. No platform URLs detected."

        platform_names = [p.title() for p in platforms.keys()]
        parts = [f"Platform score: {platform}/100."]
        parts.append(f"Detected: {', '.join(platform_names[:5])}.")
        if details:
            parts.append(f"Details: {'; '.join(details[:3])}.")

        return " ".join(parts)

    @staticmethod
    def _build_experience_summary(candidate_data):
        """Build a summary of the candidate's experience."""
        # Try to extract from agent result or parsed data
        agent_reason = candidate_data.get("agent_reason", "")
        ats = candidate_data.get("ats_score", 0)
        semantic = candidate_data.get("semantic_score", 0)
        skill_pct = candidate_data.get("skill_match_pct", 0)

        parts = []
        if agent_reason:
            parts.append(agent_reason[:200])
        parts.append(f"ATS: {ats}/100, Semantic alignment: {semantic}%, Skill match: {skill_pct}%.")

        return " ".join(parts) if parts else "Experience data unavailable."

    @staticmethod
    def _build_summary(name, rank, total, score, strengths, weaknesses,
                       missing, recommendation, behavioral_summary="", platform_summary=""):
        """Build a natural-language recruiter-friendly summary paragraph."""
        parts = [f"{name} is ranked #{rank} out of {total} candidates with an overall score of {score}/100."]

        if strengths:
            parts.append(f"Key strengths include: {'; '.join(strengths[:3])}.")

        if weaknesses:
            parts.append(f"Areas of concern: {'; '.join(weaknesses[:2])}.")

        if missing:
            parts.append(f"Missing skills: {', '.join(missing[:5])}.")

        if behavioral_summary and "No detailed" not in behavioral_summary:
            parts.append(behavioral_summary)

        if platform_summary and "No platform" not in platform_summary:
            parts.append(platform_summary)

        parts.append(f"Recommendation: {recommendation}.")

        return " ".join(parts)

