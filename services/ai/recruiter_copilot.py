"""
Recruiter Copilot Agent — Natural language Q&A over ranking results.

Recruiter can ask questions like:
  - "Why is Candidate A ranked above Candidate B?"
  - "Which candidate is best for backend development?"
  - "Who has strongest AI experience?"
  - "Show me candidates with leadership potential."
  - "What are the most common missing skills?"
  - "Which candidate has the strongest ATS score?"
  - "Explain Candidate X's strengths."
  - "Which candidates are suitable for ML roles?"

LLM-FIRST architecture:
  1. Try LLM for rich natural-language answer
  2. Fall back to rule engine if LLM unavailable
  3. Friendly fallback if both fail
"""

import re
import json
import logging

logger = logging.getLogger(__name__)


class RecruiterCopilotAgent:
    """AI-powered Q&A assistant for recruiter queries over ranking data."""

    def __init__(self):
        self._llm_text_available = False
        self._call_llm_text = None
        try:
            from services.ai.multi_llm import call_llm_text
            self._call_llm_text = call_llm_text
            self._llm_text_available = True
        except ImportError:
            pass

    def ask(self, question, ranking_data):
        """
        Answer a recruiter's question using existing ranking data.

        Flow (LLM-first):
          1. LLM (if available) — best quality answers
          2. Rule engine — deterministic patterns
          3. Friendly fallback — always produces useful output

        Args:
            question: str — natural language question
            ranking_data: dict from screen_resumes() (with all scoring data)

        Returns:
            dict with answer, evidence, candidates_referenced, method
        """
        if not question or not ranking_data:
            return {
                "answer": "Please provide a question and ensure screening results are available.",
                "evidence": [],
                "candidates_referenced": [],
                "method": "error",
            }

        question_lower = question.lower().strip()

        # ── Step 1: Try LLM-powered answer (primary) ──
        if self._llm_text_available and self._call_llm_text:
            llm_result = self._llm_answer(question, ranking_data)
            if llm_result:
                return llm_result

        # ── Step 2: Rule-based matching (fallback) ──
        rule_result = self._rule_based_answer(question_lower, ranking_data)
        if rule_result:
            return rule_result

        # ── Step 3: Smart fallback (always produces useful output) ──
        return self._smart_fallback(question_lower, ranking_data)

    # ─────────────── RULE-BASED ENGINE ───────────────

    def _rule_based_answer(self, question, ranking_data):
        """Handle common question patterns with rule-based logic."""
        candidates = ranking_data.get("top_candidates", [])
        all_results = ranking_data.get("all_results", [])

        # ── "Why is X ranked above Y?" ──
        rank_compare = re.search(
            r"why\s+(?:is|was)\s+(.+?)\s+(?:ranked?\s+)?(?:above|higher|better)\s+(?:than\s+)?(.+?)[\?\.]?$",
            question
        )
        if rank_compare:
            name_a = rank_compare.group(1).strip()
            name_b = rank_compare.group(2).strip()
            return self._explain_ranking_difference(name_a, name_b, candidates, all_results)

        # ── "Who is best for X?" / "Which candidate for X?" ──
        best_for = re.search(
            r"(?:who|which)\s+(?:candidate\s+)?(?:is\s+)?(?:best|strongest|most\s+suitable)\s+(?:for|at|in)\s+(.+?)[\?\.]?$",
            question
        )
        if best_for:
            domain = best_for.group(1).strip()
            return self._find_best_for(domain, candidates, all_results)

        # ── "Show candidates with leadership/AI/X" ──
        show_with = re.search(
            r"(?:show|list|find|who\s+has)\s+(?:me\s+)?(?:candidates?\s+)?(?:with|having)\s+(.+?)[\?\.]?$",
            question
        )
        if show_with:
            trait = show_with.group(1).strip()
            return self._find_with_trait(trait, candidates, all_results)

        # ── "Top N candidates" ──
        top_n_match = re.search(r"(?:top|best)\s+(\d+)", question)
        if top_n_match:
            n = int(top_n_match.group(1))
            return self._list_top_n(n, candidates, all_results)

        # ── "Who is the best candidate?" ──
        if re.search(r"(?:who|which)\s+(?:is\s+)?(?:the\s+)?best\s+candidate", question):
            return self._best_candidate(candidates, all_results)

        # ── "What are the most common missing skills?" ──
        if re.search(r"(?:common|frequent|most)\s+(?:missing|lacking|absent)\s+skills?", question):
            return self._common_missing_skills(candidates, all_results)

        # ── "Strongest ATS score" ──
        if re.search(r"(?:strongest|highest|best)\s+(?:ats|ats\s+score)", question):
            return self._strongest_ats(candidates, all_results)

        # ── "Explain X's strengths / weaknesses" ──
        strength_match = re.search(
            r"(?:explain|describe|what\s+are)\s+(.+?)(?:'s|s')?\s+(?:strengths?|strong\s+points?)", question
        )
        if strength_match:
            return self._explain_candidate_strengths(strength_match.group(1).strip(), candidates, all_results)

        weakness_match = re.search(
            r"(?:explain|describe|what\s+are)\s+(.+?)(?:'s|s')?\s+(?:weaknesses?|weak\s+points?|limitations?)", question
        )
        if weakness_match:
            return self._explain_candidate_weaknesses(weakness_match.group(1).strip(), candidates, all_results)

        # ── "Candidates suitable for ML/AI/backend/frontend roles" ──
        role_match = re.search(
            r"(?:suitable|good|fit|candidates?)\s+(?:for\s+)?(?:ml|machine\s+learning|ai|backend|frontend|devops|data)\s+(?:roles?|positions?|jobs?)?",
            question
        )
        if role_match:
            role_keyword = role_match.group(0).strip()
            return self._find_best_for(role_keyword, candidates, all_results)

        # ── "Show candidates with strongest ATS score" ──
        if "strongest" in question and "ats" in question:
            return self._strongest_ats(candidates, all_results)

        # ── "Which candidate has leadership potential?" ──
        if "leadership" in question:
            return self._find_with_trait("leadership", candidates, all_results)

        return None  # No rule matched — was already tried with LLM first

    # ─────────────── LLM ANSWER ───────────────

    def _llm_answer(self, question, ranking_data):
        """Use LLM to answer complex questions with natural language."""
        candidates = ranking_data.get("top_candidates", [])
        all_results = ranking_data.get("all_results", [])

        # Build compact context summary for LLM
        context_lines = []
        for c in (candidates or all_results)[:10]:
            name = c.get("name", c.get("filename", "Unknown"))
            score = c.get("combined_score", c.get("score", 0))
            ats = c.get("ats_score", 0)
            semantic = c.get("semantic_score", 0)
            skills = ", ".join(c.get("matched_skills", [])[:6])
            missing = ", ".join(c.get("missing_skills", [])[:4])
            behavioral = c.get("behavioral_score", "N/A")
            platform = c.get("platform_score", "N/A")
            skill_pct = c.get("skill_match_pct", 0)
            context_lines.append(
                f"#{c.get('rank', '?')} {name}: overall={score}/100, ATS={ats}, semantic={semantic}, "
                f"skill_match={skill_pct}%, behavioral={behavioral}, platform={platform}, "
                f"skills=[{skills}], missing=[{missing}]"
            )

        context = "\n".join(context_lines)

        prompt = f"""You are a professional AI recruiter assistant analyzing resume screening results.

CANDIDATE DATA:
{context}

SCORING METHOD: {ranking_data.get('scoring_details', '7-Signal Hybrid')}
Total Candidates Processed: {ranking_data.get('total_processed', len(all_results))}

RECRUITER QUESTION: {question}

INSTRUCTIONS:
- Provide a clear, professional, evidence-based answer.
- Reference specific candidate names, scores, and data points.
- Be concise and actionable — write like a senior recruiter briefing.
- Use bullet points for comparisons.
- NEVER return raw JSON. Write in natural language only.
- If the question is about comparison, highlight key differentiators.
- If the question is about missing skills, list the most common gaps."""

        try:
            response = self._call_llm_text(prompt)
            if response and isinstance(response, str) and len(response.strip()) > 20:
                answer = response.strip()

                # Safety check: if it looks like raw JSON, extract the text
                if answer.startswith("{") or answer.startswith("["):
                    answer = self._extract_text_from_json(answer)

                # Extract referenced candidate names
                referenced = []
                for c in (candidates or all_results)[:10]:
                    name = c.get("name", c.get("filename", ""))
                    if name and name.lower() in answer.lower():
                        referenced.append(name)

                return {
                    "answer": answer,
                    "evidence": [],
                    "candidates_referenced": referenced,
                    "method": "llm",
                }
        except Exception as e:
            logger.warning("Copilot LLM call failed: %s", e)

        return None  # Signal to fall back to rule engine

    # ─────────────── RULE-BASED HANDLERS ───────────────

    def _explain_ranking_difference(self, name_a, name_b, candidates, all_results):
        """Explain why one candidate ranks above another."""
        all_candidates = candidates + [r for r in all_results if r not in candidates]

        cand_a = self._find_candidate(name_a, all_candidates)
        cand_b = self._find_candidate(name_b, all_candidates)

        if not cand_a or not cand_b:
            available = ", ".join(c.get("name", c.get("filename", "?")) for c in candidates[:5])
            return {
                "answer": f"Could not find both candidates. Available candidates: {available}",
                "evidence": [],
                "candidates_referenced": [name_a, name_b],
                "method": "rule",
            }

        score_a = cand_a.get("combined_score", cand_a.get("score", 0))
        score_b = cand_b.get("combined_score", cand_b.get("score", 0))
        rank_a = cand_a.get("rank", "?")
        rank_b = cand_b.get("rank", "?")
        name_a_actual = cand_a.get("name", name_a)
        name_b_actual = cand_b.get("name", name_b)

        parts = [f"{name_a_actual} (#{rank_a}, score: {score_a}/100) ranks "
                 f"{'above' if score_a >= score_b else 'below'} "
                 f"{name_b_actual} (#{rank_b}, score: {score_b}/100)."]

        # Compare key dimensions
        dims = [
            ("ATS Score", "ats_score"),
            ("Semantic Score", "semantic_score"),
            ("Skill Match", "skill_match_pct"),
            ("Behavioral", "behavioral_score"),
            ("Platform", "platform_score"),
        ]
        evidence = []
        for label, key in dims:
            va = cand_a.get(key, 0) or 0
            vb = cand_b.get(key, 0) or 0
            if abs(va - vb) >= 3:
                winner = name_a_actual if va > vb else name_b_actual
                evidence.append(f"{label}: {name_a_actual}={va}, {name_b_actual}={vb} → advantage {winner}")

        if evidence:
            parts.append("Key differences:")
            for e in evidence[:5]:
                parts.append(f"  • {e}")

        # Skill differences
        skills_a = set(cand_a.get("matched_skills", []))
        skills_b = set(cand_b.get("matched_skills", []))
        only_a = skills_a - skills_b
        only_b = skills_b - skills_a
        if only_a:
            parts.append(f"Skills unique to {name_a_actual}: {', '.join(list(only_a)[:5])}.")
        if only_b:
            parts.append(f"Skills unique to {name_b_actual}: {', '.join(list(only_b)[:5])}.")

        return {
            "answer": "\n".join(parts),
            "evidence": evidence,
            "candidates_referenced": [name_a_actual, name_b_actual],
            "method": "rule",
        }

    def _find_best_for(self, domain, candidates, all_results):
        """Find best candidate for a specific domain/role."""
        domain_lower = domain.lower()
        all_c = candidates if candidates else all_results

        scored = []
        for c in all_c:
            relevance = 0
            skills = [s.lower() for s in c.get("matched_skills", [])]
            for skill in skills:
                if domain_lower in skill or skill in domain_lower:
                    relevance += 10
            reason = (c.get("reason", "") + " " + c.get("ai_explanation", "")).lower()
            if domain_lower in reason:
                relevance += 5
            relevance += (c.get("combined_score", c.get("score", 0)) or 0) / 10
            scored.append((c, relevance))

        scored.sort(key=lambda x: x[1], reverse=True)
        best = scored[0][0] if scored else None

        if best:
            name = best.get("name", best.get("filename", "Unknown"))
            score = best.get("combined_score", best.get("score", 0))
            skills = best.get("matched_skills", [])[:6]
            answer = (
                f"For {domain}, the strongest candidate is {name} "
                f"(overall score: {score}/100, rank #{best.get('rank', '?')}).\n\n"
                f"Relevant skills: {', '.join(skills) if skills else 'general profile match'}.\n"
                f"ATS: {best.get('ats_score', 'N/A')}/100, "
                f"Behavioral: {best.get('behavioral_score', 'N/A')}/100, "
                f"Platform: {best.get('platform_score', 'N/A')}/100."
            )
            return {
                "answer": answer,
                "evidence": [f"Score: {score}", f"Skills: {', '.join(skills[:5])}"],
                "candidates_referenced": [name],
                "method": "rule",
            }
        return None

    def _find_with_trait(self, trait, candidates, all_results):
        """Find candidates with a specific trait (leadership, AI, etc.)."""
        trait_lower = trait.lower()
        all_c = candidates if candidates else all_results
        matches = []

        for c in all_c:
            name = c.get("name", c.get("filename", "Unknown"))
            score = c.get("combined_score", c.get("score", 0))

            # Check behavioral breakdown
            breakdown = c.get("behavioral_breakdown", {})
            for cat, val in breakdown.items():
                if trait_lower in cat.replace("_", " ") and val >= 5:
                    matches.append((name, f"Behavioral {cat.replace('_', ' ').title()}: {val}/12.5", score))
                    break

            # Check skills
            skills = [s.lower() for s in c.get("matched_skills", [])]
            if any(trait_lower in s for s in skills):
                if name not in [m[0] for m in matches]:
                    matches.append((name, f"Has '{trait}' in skills", score))

            # Check platforms
            if "platform" in trait_lower or "github" in trait_lower:
                p_score = c.get("platform_score", 50)
                if p_score >= 60 and name not in [m[0] for m in matches]:
                    matches.append((name, f"Platform score: {p_score}/100", score))

        if matches:
            # Sort by score
            matches.sort(key=lambda x: x[2], reverse=True)
            unique = list({m[0]: m for m in matches}.values())[:5]
            answer_parts = [f"Candidates with {trait}:\n"]
            for name, detail, score in unique:
                answer_parts.append(f"  • {name} — {detail} (overall: {score}/100)")
            return {
                "answer": "\n".join(answer_parts),
                "evidence": [f"{n}: {d}" for n, d, _ in unique],
                "candidates_referenced": [n for n, _, _ in unique],
                "method": "rule",
            }

        return {
            "answer": f"No candidates with strong '{trait}' indicators were found in the current results.",
            "evidence": [],
            "candidates_referenced": [],
            "method": "rule",
        }

    def _list_top_n(self, n, candidates, all_results):
        """List top N candidates with summary."""
        source = all_results if all_results else candidates
        top = source[:n]

        lines = [f"Top {min(n, len(top))} candidates:\n"]
        for c in top:
            name = c.get("name", c.get("filename", "Unknown"))
            score = c.get("combined_score", c.get("score", 0))
            rank = c.get("rank", "?")
            ats = c.get("ats_score", "N/A")
            skills_count = len(c.get("matched_skills", []))
            lines.append(f"  #{rank} {name} — Score: {score}/100, ATS: {ats}, Skills matched: {skills_count}")

        return {
            "answer": "\n".join(lines),
            "evidence": [],
            "candidates_referenced": [c.get("name", "") for c in top],
            "method": "rule",
        }

    def _best_candidate(self, candidates, all_results):
        """Return the best candidate with a detailed summary."""
        source = candidates if candidates else all_results
        if not source:
            return self._empty_result()

        best = source[0]
        name = best.get("name", best.get("filename", "Unknown"))
        score = best.get("combined_score", best.get("score", 0))
        ats = best.get("ats_score", "N/A")
        semantic = best.get("semantic_score", "N/A")
        behavioral = best.get("behavioral_score", "N/A")
        platform = best.get("platform_score", "N/A")
        matched = best.get("matched_skills", [])
        missing = best.get("missing_skills", [])

        answer = (
            f"The top-ranked candidate is {name} with an overall score of {score}/100.\n\n"
            f"Score breakdown:\n"
            f"  • ATS Score: {ats}/100\n"
            f"  • Semantic Alignment: {semantic}%\n"
            f"  • Behavioral Score: {behavioral}/100\n"
            f"  • Platform Score: {platform}/100\n\n"
            f"Matched skills ({len(matched)}): {', '.join(matched[:8]) if matched else 'N/A'}\n"
            f"Missing skills ({len(missing)}): {', '.join(missing[:6]) if missing else 'None'}"
        )

        return {
            "answer": answer,
            "evidence": [],
            "candidates_referenced": [name],
            "method": "rule",
        }

    def _common_missing_skills(self, candidates, all_results):
        """Identify the most commonly missing skills across all candidates."""
        from collections import Counter
        source = all_results if all_results else candidates
        missing_counter = Counter()

        for c in source:
            for skill in c.get("missing_skills", []):
                if isinstance(skill, str) and skill.strip():
                    missing_counter[skill.strip().lower()] += 1

        if not missing_counter:
            return {
                "answer": "No significant skill gaps were identified across the candidate pool.",
                "evidence": [],
                "candidates_referenced": [],
                "method": "rule",
            }

        top_missing = missing_counter.most_common(10)
        total = len(source)

        lines = [f"Most commonly missing skills across {total} candidates:\n"]
        for skill, count in top_missing:
            pct = round(count / total * 100)
            lines.append(f"  • {skill.title()} — missing in {count}/{total} candidates ({pct}%)")

        lines.append(f"\nThese represent the biggest skill gaps in your candidate pool. "
                     f"Consider sourcing candidates with these specific competencies.")

        return {
            "answer": "\n".join(lines),
            "evidence": [f"{s}: {c}x" for s, c in top_missing[:5]],
            "candidates_referenced": [],
            "method": "rule",
        }

    def _strongest_ats(self, candidates, all_results):
        """Find candidates with the strongest ATS scores."""
        source = all_results if all_results else candidates
        sorted_by_ats = sorted(source, key=lambda c: c.get("ats_score", 0) or 0, reverse=True)
        top = sorted_by_ats[:5]

        lines = ["Candidates with strongest ATS compatibility:\n"]
        for c in top:
            name = c.get("name", c.get("filename", "Unknown"))
            ats = c.get("ats_score", 0)
            overall = c.get("combined_score", c.get("score", 0))
            lines.append(f"  • {name} — ATS: {ats}/100, Overall: {overall}/100")

        return {
            "answer": "\n".join(lines),
            "evidence": [],
            "candidates_referenced": [c.get("name", "") for c in top],
            "method": "rule",
        }

    def _explain_candidate_strengths(self, name_query, candidates, all_results):
        """Explain a specific candidate's strengths."""
        all_c = candidates + [r for r in all_results if r not in candidates]
        cand = self._find_candidate(name_query, all_c)
        if not cand:
            return {
                "answer": f"Could not find candidate '{name_query}'. Available: "
                          f"{', '.join(c.get('name', '?') for c in candidates[:5])}",
                "evidence": [], "candidates_referenced": [name_query], "method": "rule",
            }

        name = cand.get("name", name_query)
        strengths = []
        ats = cand.get("ats_score", 0)
        if ats >= 70:
            strengths.append(f"Excellent ATS compatibility ({ats}/100)")
        elif ats >= 50:
            strengths.append(f"Good ATS score ({ats}/100)")

        semantic = cand.get("semantic_score", 0)
        if semantic >= 60:
            strengths.append(f"Strong semantic alignment with job description ({semantic}%)")

        behavioral = cand.get("behavioral_score", 0)
        if behavioral >= 65:
            strengths.append(f"Strong behavioral signals ({behavioral}/100)")
            breakdown = cand.get("behavioral_breakdown", {})
            strong_cats = [k.replace("_", " ").title() for k, v in breakdown.items() if v >= 8]
            if strong_cats:
                strengths.append(f"Key behavioral strengths: {', '.join(strong_cats[:3])}")

        matched = cand.get("matched_skills", [])
        if len(matched) >= 4:
            strengths.append(f"Strong skill match ({len(matched)} skills): {', '.join(matched[:6])}")

        platform = cand.get("platform_score", 50)
        if platform >= 65:
            strengths.append(f"Active platform presence (score: {platform}/100)")

        answer = f"Strengths of {name} (overall: {cand.get('combined_score', 0)}/100):\n\n"
        if strengths:
            for s in strengths:
                answer += f"  ✅ {s}\n"
        else:
            answer += "  No standout strengths identified relative to this JD.\n"

        return {
            "answer": answer,
            "evidence": strengths[:4],
            "candidates_referenced": [name],
            "method": "rule",
        }

    def _explain_candidate_weaknesses(self, name_query, candidates, all_results):
        """Explain a specific candidate's weaknesses."""
        all_c = candidates + [r for r in all_results if r not in candidates]
        cand = self._find_candidate(name_query, all_c)
        if not cand:
            return {
                "answer": f"Could not find candidate '{name_query}'.",
                "evidence": [], "candidates_referenced": [name_query], "method": "rule",
            }

        name = cand.get("name", name_query)
        weaknesses = []

        ats = cand.get("ats_score", 0)
        if ats < 50:
            weaknesses.append(f"Below-average ATS score ({ats}/100)")

        semantic = cand.get("semantic_score", 0)
        if semantic < 40:
            weaknesses.append(f"Low semantic alignment with JD ({semantic}%)")

        missing = cand.get("missing_skills", [])
        if missing:
            weaknesses.append(f"Missing {len(missing)} required skills: {', '.join(missing[:5])}")

        behavioral = cand.get("behavioral_score", 0)
        if behavioral < 40:
            weaknesses.append(f"Limited behavioral signals ({behavioral}/100)")

        platform = cand.get("platform_score", 50)
        if platform < 40:
            weaknesses.append("Minimal verifiable platform activity")

        skill_pct = cand.get("skill_match_pct", 0)
        if skill_pct < 40:
            weaknesses.append(f"Low skill coverage ({skill_pct}%)")

        answer = f"Weaknesses of {name} (overall: {cand.get('combined_score', 0)}/100):\n\n"
        if weaknesses:
            for w in weaknesses:
                answer += f"  ⚠️ {w}\n"
        else:
            answer += "  No significant weaknesses identified for this role.\n"

        return {
            "answer": answer,
            "evidence": weaknesses[:4],
            "candidates_referenced": [name],
            "method": "rule",
        }

    # ─────────────── SMART FALLBACK ───────────────

    def _smart_fallback(self, question, ranking_data):
        """
        Comprehensive fallback that generates useful answers for ANY question.
        Produces a recruiter-quality summary instead of a generic redirect.
        """
        candidates = ranking_data.get("top_candidates", [])
        all_results = ranking_data.get("all_results", [])
        source = candidates if candidates else all_results
        total = ranking_data.get("total_processed", len(source))

        if not source:
            return self._empty_result()

        # Try to detect what the user is asking about
        q = question.lower()

        # Check if asking about a specific candidate
        for c in source[:10]:
            name = (c.get("name", "") or "").lower()
            if name and name in q:
                return self._explain_candidate_strengths(name, candidates, all_results)

        # Build a comprehensive summary
        best = source[0]
        best_name = best.get("name", best.get("filename", "Unknown"))
        best_score = best.get("combined_score", best.get("score", 0))

        # Calculate quick stats
        avg_score = round(sum(c.get("combined_score", 0) for c in source) / max(len(source), 1), 1)
        avg_ats = round(sum(c.get("ats_score", 0) for c in source) / max(len(source), 1), 1)

        answer = (
            f"Based on the screening of {total} candidates:\n\n"
            f"🏆 Top candidate: {best_name} (score: {best_score}/100)\n"
            f"📊 Average score: {avg_score}/100, Average ATS: {avg_ats}/100\n\n"
        )

        # Add top 3 summary
        if len(source) >= 2:
            answer += "Top candidates:\n"
            for c in source[:3]:
                name = c.get("name", c.get("filename", "Unknown"))
                score = c.get("combined_score", c.get("score", 0))
                answer += f"  #{c.get('rank', '?')} {name} — {score}/100\n"

        answer += (
            "\nTry specific questions like:\n"
            "  • \"Why is X ranked above Y?\"\n"
            "  • \"What are the most common missing skills?\"\n"
            "  • \"Explain [candidate name]'s strengths\"\n"
            "  • \"Which candidate is best for backend?\""
        )

        return {
            "answer": answer,
            "evidence": [],
            "candidates_referenced": [best_name],
            "method": "fallback",
        }

    # ─────────────── HELPERS ───────────────

    def _empty_result(self):
        """Return empty result when no data is available."""
        return {
            "answer": "No screening results available. Please run a bulk screening first.",
            "evidence": [],
            "candidates_referenced": [],
            "method": "fallback",
        }

    @staticmethod
    def _extract_text_from_json(text):
        """Extract readable text from a JSON string response."""
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                for key in ("answer", "response", "text", "content", "insights",
                            "analysis", "reasoning", "explanation"):
                    if key in data and isinstance(data[key], str) and len(data[key]) > 10:
                        return data[key]
                parts = [str(v) for v in data.values() if isinstance(v, str) and len(str(v)) > 10]
                return " ".join(parts) if parts else text
        except (json.JSONDecodeError, ValueError):
            pass
        return text

    @staticmethod
    def _find_candidate(name_query, candidates):
        """Find a candidate by name (fuzzy match)."""
        name_lower = name_query.lower().strip()
        for c in candidates:
            c_name = (c.get("name", "") or "").lower()
            c_file = (c.get("filename", "") or "").lower()
            if name_lower in c_name or name_lower in c_file or c_name in name_lower:
                return c
        return None
