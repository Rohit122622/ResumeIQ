"""
Demo Package Generator — Creates sample output for judge evaluation.

Generates:
  sample_output/ranked_candidates.csv
  sample_output/ranked_candidates.json
  sample_output/comparison_report.txt

Uses realistic synthetic data to demonstrate the full Nexus CV pipeline output.
Run: python scripts/generate_demo.py
"""

import os
import sys

# Project root setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from services.processing.export_engine import ExportEngine
from services.processing.comparison_engine import CandidateComparisonEngine


def generate_demo():
    """Generate complete demo output package."""
    output_dir = os.path.join(PROJECT_ROOT, "sample_output")
    os.makedirs(output_dir, exist_ok=True)

    # ── Synthetic candidate data ──
    candidates = [
        {
            "rank": 1, "name": "Arjun Mehta", "filename": "arjun_mehta.pdf",
            "combined_score": 87.3, "score": 87.3,
            "ats_score": 82, "semantic_score": 91.2, "skill_match_pct": 78.5,
            "agent_score": 8.5, "xgboost_score": 76.4,
            "behavioral_score": 85, "platform_score": 90,
            "matched_skills": ["python", "tensorflow", "pytorch", "sql", "docker", "kubernetes", "aws", "machine learning", "deep learning", "nlp"],
            "missing_skills": ["spark", "airflow"],
            "confidence": "high", "agent_confidence": "high",
            "scoring_method": "xgboost_hybrid",
            "reason": "Ranked #1: strong semantic alignment with JD, excellent ATS score (82/100), high skill match (78%), 10 matched skills. Strong GitHub presence with 15+ repositories including 4 AI/ML projects.",
            "ai_explanation": "Top candidate with exceptional alignment across all dimensions.",
            "agent_evidence": ["Built production ML pipeline serving 1M+ predictions daily", "Led team of 5 engineers on NLP project"],
            "platforms_detected": {"github": "arjunmehta", "linkedin": "arjunmehta"},
            "behavioral_breakdown": {"communication": 10.5, "leadership": 11.0, "teamwork": 9.5, "problem_solving": 10.0, "ownership": 9.0, "adaptability": 8.5, "growth_mindset": 10.5, "mentorship": 6.0},
        },
        {
            "rank": 2, "name": "Priya Sharma", "filename": "priya_sharma.pdf",
            "combined_score": 79.1, "score": 79.1,
            "ats_score": 75, "semantic_score": 83.4, "skill_match_pct": 72.0,
            "agent_score": 7.8, "xgboost_score": 71.2,
            "behavioral_score": 78, "platform_score": 72,
            "matched_skills": ["python", "react", "node.js", "sql", "aws", "docker", "javascript", "git"],
            "missing_skills": ["kubernetes", "terraform", "spark"],
            "confidence": "high", "agent_confidence": "high",
            "scoring_method": "xgboost_hybrid",
            "reason": "Ranked #2: strong semantic relevance, solid ATS score (75/100), good skill coverage with 8 matched skills.",
            "ai_explanation": "Strong full-stack candidate with solid cloud experience.",
            "agent_evidence": ["Developed microservice architecture reducing latency by 40%", "Contributed to 3 open-source projects"],
            "platforms_detected": {"github": "priyasharma", "linkedin": "priya-sharma"},
            "behavioral_breakdown": {"communication": 8.0, "leadership": 7.5, "teamwork": 10.0, "problem_solving": 9.5, "ownership": 8.0, "adaptability": 9.0, "growth_mindset": 11.0, "mentorship": 5.0},
        },
        {
            "rank": 3, "name": "Rahul Verma", "filename": "rahul_verma.pdf",
            "combined_score": 71.6, "score": 71.6,
            "ats_score": 68, "semantic_score": 74.1, "skill_match_pct": 65.0,
            "agent_score": 7.2, "xgboost_score": 65.8,
            "behavioral_score": 70, "platform_score": 65,
            "matched_skills": ["python", "java", "sql", "aws", "git", "docker"],
            "missing_skills": ["kubernetes", "tensorflow", "react", "spark"],
            "confidence": "medium", "agent_confidence": "medium",
            "scoring_method": "xgboost_hybrid",
            "reason": "Ranked #3: moderate semantic relevance, adequate skill coverage (65%), solid backend foundation.",
            "ai_explanation": "Solid backend engineer with room for growth in cloud-native and ML skills.",
            "agent_evidence": ["Optimized database queries improving performance by 60%"],
            "platforms_detected": {"github": "rahulverma"},
            "behavioral_breakdown": {"communication": 7.0, "leadership": 5.5, "teamwork": 8.5, "problem_solving": 10.5, "ownership": 7.0, "adaptability": 7.5, "growth_mindset": 8.0, "mentorship": 6.0},
        },
        {
            "rank": 4, "name": "Ananya Patel", "filename": "ananya_patel.pdf",
            "combined_score": 64.2, "score": 64.2,
            "ats_score": 61, "semantic_score": 66.8, "skill_match_pct": 55.0,
            "agent_score": 6.5, "xgboost_score": 58.3,
            "behavioral_score": 62, "platform_score": 55,
            "matched_skills": ["python", "sql", "javascript", "html", "css"],
            "missing_skills": ["docker", "kubernetes", "aws", "tensorflow", "react"],
            "confidence": "medium", "agent_confidence": "medium",
            "scoring_method": "heuristic",
            "reason": "Ranked #4: adequate skill coverage, moderate semantic match. Good foundation but missing key cloud/ML skills.",
            "ai_explanation": "Promising junior candidate; needs upskilling in cloud and ML technologies.",
            "agent_evidence": [],
            "platforms_detected": {"linkedin": "ananyapatel"},
            "behavioral_breakdown": {"communication": 6.5, "leadership": 4.0, "teamwork": 7.5, "problem_solving": 8.0, "ownership": 6.0, "adaptability": 8.5, "growth_mindset": 10.0, "mentorship": 1.5},
        },
        {
            "rank": 5, "name": "Vikram Singh", "filename": "vikram_singh.pdf",
            "combined_score": 52.8, "score": 52.8,
            "ats_score": 48, "semantic_score": 55.2, "skill_match_pct": 42.0,
            "agent_score": 5.4, "xgboost_score": 45.1,
            "behavioral_score": 55, "platform_score": 50,
            "matched_skills": ["python", "sql", "html"],
            "missing_skills": ["docker", "kubernetes", "aws", "react", "node.js", "tensorflow"],
            "confidence": "low", "agent_confidence": "low",
            "scoring_method": "heuristic",
            "reason": "Ranked #5: limited skill coverage (42%), below-average ATS score. Significant skill gaps for the target role.",
            "ai_explanation": "Candidate shows potential but lacks multiple critical skills for the role.",
            "agent_evidence": [],
            "platforms_detected": {},
            "behavioral_breakdown": {"communication": 5.0, "leadership": 3.0, "teamwork": 6.0, "problem_solving": 7.0, "ownership": 5.0, "adaptability": 6.0, "growth_mindset": 7.0, "mentorship": 1.0},
        },
    ]

    ranking_results = {
        "top_candidates": candidates[:3],
        "all_results": candidates,
        "total_processed": 5,
        "top_n": 3,
        "scoring_details": (
            "7-Signal Hybrid: 0.20 × Semantic + 0.18 × ATS + 0.20 × Multi-Agent + "
            "0.12 × Skill Match + 0.10 × XGBoost + 0.10 × Behavioral + 0.10 × Platform"
        ),
        "agent_enabled": True,
    }

    # ── Generate CSV ──
    export = ExportEngine()
    csv_path = os.path.join(output_dir, "ranked_candidates.csv")
    export.generate_csv(ranking_results, csv_path)
    print(f"[OK] {csv_path}")

    # ── Generate JSON ──
    json_path = os.path.join(output_dir, "ranked_candidates.json")
    export.generate_json(ranking_results, json_path)
    print(f"[OK] {json_path}")

    # ── Generate Comparison Report ──
    comparison_engine = CandidateComparisonEngine()
    comparison = comparison_engine.compare(candidates[0], candidates[1])
    report_path = os.path.join(output_dir, "comparison_report.txt")
    export.generate_comparison_report(comparison, report_path)
    print(f"[OK] {report_path}")

    print(f"\n[DONE] Demo package generated in: {output_dir}")
    print(f"   - ranked_candidates.csv ({len(candidates)} candidates)")
    print(f"   - ranked_candidates.json ({len(candidates)} candidates)")
    print(f"   - comparison_report.txt ({candidates[0]['name']} vs {candidates[1]['name']})")


if __name__ == "__main__":
    generate_demo()
