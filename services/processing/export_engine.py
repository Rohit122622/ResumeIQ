"""
Export Engine — Generates downloadable CSV and JSON from ranking results.

Produces ranked_candidates.csv and ranked_candidates.json with all
scoring dimensions for judge/recruiter evaluation.

No existing functionality is modified — this is a pure additive module.
"""

import csv
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ExportEngine:
    """Generates exportable ranked candidate files in CSV and JSON formats."""

    # CSV column order
    CSV_COLUMNS = [
        "Rank", "Candidate Name", "Final Score", "Semantic Score", "ATS Score",
        "Agent Score", "Skill Score", "ML Score", "Behavioral Score",
        "Platform Score", "Experience Years", "Matched Skills", "Missing Skills",
        "Confidence", "Recommendation", "Behavioral Summary", "Platform Summary",
        "Reason",
    ]

    def generate_csv(self, ranking_results, output_path):
        """
        Generate ranked_candidates.csv from bulk screening results.

        Args:
            ranking_results: dict from screen_resumes() or enriched result
            output_path: absolute path for the CSV file

        Returns:
            str: path to the generated CSV file
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        rows = self._build_rows(ranking_results)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_COLUMNS)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

        logger.info("CSV export: %d candidates → %s", len(rows), output_path)
        return output_path

    def generate_json(self, ranking_results, output_path):
        """
        Generate ranked_candidates.json from bulk screening results.

        Args:
            ranking_results: dict from screen_resumes() or enriched result
            output_path: absolute path for the JSON file

        Returns:
            str: path to the generated JSON file
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        rows = self._build_rows(ranking_results)

        export_data = {
            "generated_at": datetime.now().isoformat(),
            "total_candidates": ranking_results.get("total_processed", len(rows)),
            "scoring_formula": ranking_results.get("scoring_details", ""),
            "agent_enabled": ranking_results.get("agent_enabled", False),
            "candidates": rows,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info("JSON export: %d candidates → %s", len(rows), output_path)
        return output_path

    def generate_comparison_report(self, comparison_data, output_path):
        """
        Generate comparison_report.txt from candidate comparison.

        Args:
            comparison_data: dict from CandidateComparisonEngine.compare()
            output_path: absolute path for the text file

        Returns:
            str: path to the generated report
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        lines = [
            "=" * 60,
            "NEXUS CV — CANDIDATE COMPARISON REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
        ]

        if comparison_data:
            a = comparison_data.get("candidate_a_name", "Candidate A")
            b = comparison_data.get("candidate_b_name", "Candidate B")

            lines.append(f"Comparing: {a} vs {b}")
            lines.append("-" * 40)

            # Score comparison
            scores = comparison_data.get("score_comparison", {})
            metrics = scores.get("metrics", {}) if isinstance(scores, dict) else {}
            if metrics:
                lines.append("")
                lines.append("SCORE COMPARISON:")
                for metric, vals in metrics.items():
                    if not isinstance(vals, dict):
                        continue
                    label = vals.get("label", metric.replace("_", " ").title())
                    lines.append(f"  {label}: {vals.get('a', 'N/A')} vs {vals.get('b', 'N/A')}")

            # Skill comparison
            skill_cmp = comparison_data.get("skill_comparison", {})
            if skill_cmp:
                lines.append("")
                lines.append("SKILL COMPARISON:")
                lines.append(f"  Shared Skills: {', '.join(skill_cmp.get('shared', [])[:10])}")
                lines.append(f"  Only {a}: {', '.join(skill_cmp.get('only_a', [])[:8])}")
                lines.append(f"  Only {b}: {', '.join(skill_cmp.get('only_b', [])[:8])}")

            # Recommendation
            rec = comparison_data.get("recommendation", "")
            if rec:
                lines.append("")
                lines.append(f"RECOMMENDATION: {rec}")

            justification = comparison_data.get("justification", "")
            if justification:
                lines.append(f"JUSTIFICATION: {justification}")

        lines.append("")
        lines.append("=" * 60)
        lines.append("Generated by Nexus CV — Agentic AI Resume Screening Platform")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info("Comparison report → %s", output_path)
        return output_path

    def _build_rows(self, ranking_results):
        """Build flat rows from ranking results for CSV/JSON export."""
        rows = []

        # Use all_results if available (full list), else top_candidates
        candidates = ranking_results.get("all_results", [])
        top_map = {}

        # Build lookup from top_candidates (which has richer data)
        for tc in ranking_results.get("top_candidates", []):
            key = tc.get("name", tc.get("filename", ""))
            top_map[key] = tc

        for c in candidates:
            name = c.get("name", c.get("filename", "Unknown"))
            top = top_map.get(name, {})

            # Derive recommendation from score
            score = c.get("combined_score", c.get("score", 0))
            recommendation = self._score_to_recommendation(score)

            matched_skills = top.get("matched_skills", c.get("matched_skills", []))
            missing_skills = top.get("missing_skills", c.get("missing_skills", []))

            # Behavioral summary from breakdown
            behavioral_breakdown = top.get("behavioral_breakdown", c.get("behavioral_breakdown", {}))
            behavioral_summary = ""
            if behavioral_breakdown:
                strong = [k.replace("_", " ").title() for k, v in behavioral_breakdown.items() if v >= 8]
                if strong:
                    behavioral_summary = f"Strong: {', '.join(strong[:4])}"

            # Platform summary
            platforms = top.get("platforms_detected", c.get("platforms_detected", {}))
            platform_summary = ", ".join(p.title() for p in platforms.keys())[:100] if platforms else ""

            row = {
                "Rank": c.get("rank", 0),
                "Candidate Name": name,
                "Final Score": score,
                "Semantic Score": top.get("semantic_score", c.get("semantic_score", "")),
                "ATS Score": c.get("ats_score", ""),
                "Agent Score": self._format_agent_score(top.get("agent_score", c.get("agent_score"))),
                "Skill Score": top.get("skill_match_pct", c.get("skill_match_pct", "")),
                "ML Score": top.get("xgboost_score", c.get("xgboost_score", "")),
                "Behavioral Score": top.get("behavioral_score", c.get("behavioral_score", "")),
                "Platform Score": top.get("platform_score", c.get("platform_score", "")),
                "Experience Years": top.get("experience_years", c.get("experience_years", "")),
                "Matched Skills": "; ".join(matched_skills) if isinstance(matched_skills, list) else str(matched_skills),
                "Missing Skills": "; ".join(missing_skills) if isinstance(missing_skills, list) else str(missing_skills),
                "Confidence": top.get("confidence", top.get("agent_confidence", c.get("confidence", ""))),
                "Recommendation": recommendation,
                "Behavioral Summary": behavioral_summary,
                "Platform Summary": platform_summary,
                "Reason": top.get("reason", top.get("ai_explanation", c.get("reason", ""))),
            }
            rows.append(row)

        return rows

    @staticmethod
    def _score_to_recommendation(score):
        """Convert numeric score to recruiter recommendation label."""
        if score >= 75:
            return "Strong Hire"
        elif score >= 60:
            return "Recommended"
        elif score >= 45:
            return "Consider"
        elif score >= 30:
            return "Below Average"
        else:
            return "Needs Review"

    @staticmethod
    def _format_agent_score(agent_score):
        """Format agent score (0-10 scale to percentage)."""
        if agent_score is None:
            return ""
        try:
            return round(float(agent_score) * 10, 1)
        except (ValueError, TypeError):
            return ""
