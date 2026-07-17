"""
Platform Activity Agent — Detects platform presence and activity from resume text.

Analyzes URLs and mentions of developer platforms (GitHub, LinkedIn, Kaggle, etc.)
to generate a Platform Score (0–100).

NO web scraping — only analyzes text already present in the resume.
Neutral score (50) if no platform URLs detected — does NOT penalize.
"""

import re
import logging

logger = logging.getLogger(__name__)


# ── Platform URL Patterns ──
_PLATFORM_PATTERNS = {
    "github": re.compile(
        r"(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9\-_]+)", re.IGNORECASE
    ),
    "linkedin": re.compile(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/([A-Za-z0-9\-_]+)", re.IGNORECASE
    ),
    "kaggle": re.compile(
        r"(?:https?://)?(?:www\.)?kaggle\.com/([A-Za-z0-9\-_]+)", re.IGNORECASE
    ),
    "hackerrank": re.compile(
        r"(?:https?://)?(?:www\.)?hackerrank\.com/([A-Za-z0-9\-_]+)", re.IGNORECASE
    ),
    "leetcode": re.compile(
        r"(?:https?://)?(?:www\.)?leetcode\.com/(?:u/)?([A-Za-z0-9\-_]+)", re.IGNORECASE
    ),
    "codeforces": re.compile(
        r"(?:https?://)?(?:www\.)?codeforces\.com/profile/([A-Za-z0-9\-_]+)", re.IGNORECASE
    ),
    "codechef": re.compile(
        r"(?:https?://)?(?:www\.)?codechef\.com/users/([A-Za-z0-9\-_]+)", re.IGNORECASE
    ),
    "geeksforgeeks": re.compile(
        r"(?:https?://)?(?:www\.)?(?:auth\.)?geeksforgeeks\.org/user/([A-Za-z0-9\-_]+)",
        re.IGNORECASE,
    ),
    "portfolio": re.compile(
        r"(?:https?://)?(?:www\.)?([A-Za-z0-9\-]+\.(?:dev|io|me|tech|site|app|co))(?:/|\s|$)",
        re.IGNORECASE,
    ),
}

# ── Activity / Mention Patterns ──
_GITHUB_ACTIVITY_PATTERNS = [
    re.compile(r"\b(\d+)\+?\s*(?:repositories|repos)\b", re.IGNORECASE),
    re.compile(r"\b(\d+)\+?\s*(?:open[\s\-]?source)\s*(?:projects?|contributions?)\b", re.IGNORECASE),
    re.compile(r"\b(?:contributed?\s+to)\s+(\d+)", re.IGNORECASE),
    re.compile(r"\b(\d+)\+?\s*(?:GitHub|public)\s*(?:repositories|repos|projects?)\b", re.IGNORECASE),
    re.compile(r"\b(\d+)\+?\s*(?:stars?|forks?)\b", re.IGNORECASE),
]

_AI_ML_KEYWORDS = [
    "machine learning", "deep learning", "neural network", "tensorflow", "pytorch",
    "keras", "scikit-learn", "nlp", "natural language processing", "computer vision",
    "transformers", "bert", "gpt", "llm", "large language model", "reinforcement learning",
    "generative ai", "gen ai", "ai model", "ml model", "data science",
    "hugging face", "langchain", "rag", "vector database", "faiss",
]

_CONTRIBUTION_INDICATORS = [
    re.compile(r"\b(?:open[\s\-]?source)\b", re.IGNORECASE),
    re.compile(r"\b(?:contributor|maintainer|committer)\b", re.IGNORECASE),
    re.compile(r"\b(?:pull\s*requests?|PRs?|merged)\b", re.IGNORECASE),
    re.compile(r"\b(?:forked|starred)\b", re.IGNORECASE),
]

_BLOG_PATTERNS = [
    re.compile(r"\b(?:blog|article|publication|technical\s*writ(?:ing|e))\b", re.IGNORECASE),
    re.compile(r"(?:medium\.com|dev\.to|hashnode|substack|wordpress)", re.IGNORECASE),
]

# ── Research / Academic Patterns ──
_RESEARCH_PATTERNS = [
    re.compile(r"(?:arxiv\.org|arxiv\s*:)", re.IGNORECASE),
    re.compile(r"\b(?:IEEE|ACM|ICML|NeurIPS|CVPR|AAAI|ICLR|ECCV|EMNLP|ACL)\b"),
    re.compile(r"(?:scholar\.google|google\s*scholar)", re.IGNORECASE),
    re.compile(r"(?:orcid\.org|ORCID)", re.IGNORECASE),
    re.compile(r"\b(?:doi|DOI)\s*:\s*10\.\d+", re.IGNORECASE),
    re.compile(r"\b(?:published|peer[\s\-]?reviewed|journal|conference\s+proceed|proceedings)\b", re.IGNORECASE),
    re.compile(r"\b(?:research\s+paper|thesis|dissertation)\b", re.IGNORECASE),
]

_LANGUAGE_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang",
    "rust", "ruby", "swift", "kotlin", "scala", "r ", "matlab", "julia",
    "php", "perl", "dart", "elixir", "haskell",
]


class PlatformActivityAgent:
    """Evaluates candidate platform activity signals from resume text.

    Does NOT perform any web scraping — only analyzes information present
    in the resume document. If no platform URLs are detected, assigns a
    neutral score (50) so candidates are not penalized.
    """

    def evaluate(self, resume_text, parsed_data=None):
        """
        Analyze platform presence and activity indicators.

        Args:
            resume_text: Full resume text
            parsed_data: Pre-parsed resume data (optional)

        Returns:
            dict with platform_score (0–100), platforms_detected, details,
            github_info, linkedin_detected, portfolio_detected
        """
        if not resume_text:
            return self._neutral_result()

        text = resume_text
        text_lower = text.lower()

        # ── 1. Detect Platform URLs ──
        platforms_detected = {}
        # ── Portfolio domain exclusions (avoid false positives) ──
        _PORTFOLIO_EXCLUDE = {
            "github", "linkedin", "kaggle", "hackerrank", "leetcode",
            "codechef", "geeksforgeeks", "codeforces", "google", "gmail",
            "outlook", "yahoo", "hotmail", "microsoft", "apple", "amazon",
            "facebook", "twitter", "instagram", "reddit", "stackoverflow",
            "medium", "substack", "wordpress", "arxiv", "doi", "scholar",
            "npmjs", "pypi", "maven", "docker", "npm",
        }

        for platform, pattern in _PLATFORM_PATTERNS.items():
            if platform == "portfolio":
                for match in pattern.finditer(text):
                    val = match.group(1) if match.lastindex else match.group(0)
                    val_lower = val.lower()
                    if not any(domain in val_lower for domain in _PORTFOLIO_EXCLUDE):
                        platforms_detected[platform] = val
                        break
            else:
                match = pattern.search(text)
                if match:
                    platforms_detected[platform] = match.group(1) if match.lastindex else True

        # ── 2. Detect GitHub activity mentions ──
        github_info = {
            "detected": "github" in platforms_detected,
            "username": platforms_detected.get("github", ""),
            "repo_count": 0,
            "ai_ml_repos": 0,
            "contribution_signals": 0,
            "activity_indicators": [],
        }

        for pattern in _GITHUB_ACTIVITY_PATTERNS:
            match = pattern.search(text)
            if match:
                try:
                    count = int(match.group(1))
                    github_info["repo_count"] = max(github_info["repo_count"], count)
                    github_info["activity_indicators"].append(match.group(0).strip())
                except (ValueError, IndexError):
                    pass

        # Count AI/ML project mentions
        ai_ml_count = sum(1 for kw in _AI_ML_KEYWORDS if kw in text_lower)
        github_info["ai_ml_repos"] = min(ai_ml_count, 10)

        # Count open-source contribution indicators
        for pattern in _CONTRIBUTION_INDICATORS:
            if pattern.search(text):
                github_info["contribution_signals"] += 1

        # ── 3. Detect programming language diversity ──
        languages_found = [lang for lang in _LANGUAGE_KEYWORDS if lang.lower().strip() in text_lower]
        language_diversity = min(len(set(languages_found)), 10)

        # ── 4. Detect blog/writing ──
        blog_detected = any(p.search(text) for p in _BLOG_PATTERNS)

        # ── 5. Detect research papers / academic publications ──
        research_signals = sum(1 for p in _RESEARCH_PATTERNS if p.search(text))
        research_detected = research_signals >= 1

        # ── 6. Compute Platform Score ──
        platform_count = len(platforms_detected)

        if platform_count == 0:
            # No platform URLs detected — assign neutral score
            return self._neutral_result()

        score = 0.0

        # Platform presence points (max 40)
        if "github" in platforms_detected:
            score += 15
        if "linkedin" in platforms_detected:
            score += 10
        if "portfolio" in platforms_detected:
            score += 5
        # Other platforms: 2.5 each, max 10
        other_platforms = [p for p in platforms_detected if p not in ("github", "linkedin", "portfolio")]
        score += min(len(other_platforms) * 2.5, 10)

        # Activity indicators (max 30)
        if github_info["repo_count"] >= 10:
            score += 15
        elif github_info["repo_count"] >= 5:
            score += 10
        elif github_info["repo_count"] >= 1:
            score += 5

        if github_info["contribution_signals"] >= 2:
            score += 10
        elif github_info["contribution_signals"] >= 1:
            score += 5

        if github_info["activity_indicators"]:
            score += 5

        # Technical depth (max 30)
        if github_info["ai_ml_repos"] >= 3:
            score += 12
        elif github_info["ai_ml_repos"] >= 1:
            score += 6

        if language_diversity >= 4:
            score += 10
        elif language_diversity >= 2:
            score += 5

        if blog_detected:
            score += 8

        # Research/academic publications (max 10)
        if research_signals >= 3:
            score += 10
        elif research_signals >= 2:
            score += 7
        elif research_signals >= 1:
            score += 4

        platform_score = round(max(0, min(100, score)), 1)

        # ── Build Details ──
        details = []
        if "github" in platforms_detected:
            detail = "GitHub detected"
            if github_info["repo_count"] > 0:
                detail += f" — {github_info['repo_count']} repositories"
            if github_info["ai_ml_repos"] > 0:
                detail += f", {github_info['ai_ml_repos']} AI/ML projects"
            if github_info["contribution_signals"] > 0:
                detail += ", active contributor"
            details.append(detail)

        if "linkedin" in platforms_detected:
            details.append("LinkedIn profile detected")

        if "portfolio" in platforms_detected:
            details.append("Portfolio/personal website detected")

        for p in other_platforms:
            details.append(f"{p.title()} profile detected")

        if languages_found:
            details.append(f"Strong {', '.join(list(set(languages_found))[:4])} profile")

        if blog_detected:
            details.append("Technical blog/writing detected")

        if research_detected:
            details.append(f"Research/academic publications detected ({research_signals} signals)")

        logger.info(
            "Platform Activity Agent: platforms=%s, count=%d, score=%.1f, urls_detected=%s",
            list(platforms_detected.keys()),
            platform_count,
            platform_score,
            {k: v for k, v in platforms_detected.items() if isinstance(v, str)}
        )

        return {
            "platform_score": platform_score,
            "platforms_detected": platforms_detected,
            "platform_count": platform_count,
            "details": details,
            "github_info": github_info,
            "linkedin_detected": "linkedin" in platforms_detected,
            "portfolio_detected": "portfolio" in platforms_detected,
            "language_diversity": language_diversity,
            "blog_detected": blog_detected,
            "research_detected": research_detected,
            "explanation": f"Platform Score: {platform_score}/100. " + "; ".join(details[:4]) if details else f"Platform Score: {platform_score}/100."
        }

    def _neutral_result(self):
        """Return neutral result when no platform data is available."""
        return {
            "platform_score": 50,
            "platforms_detected": {},
            "platform_count": 0,
            "details": ["No platform URLs detected — neutral score assigned"],
            "github_info": {
                "detected": False, "username": "", "repo_count": 0,
                "ai_ml_repos": 0, "contribution_signals": 0, "activity_indicators": [],
            },
            "linkedin_detected": False,
            "portfolio_detected": False,
            "language_diversity": 0,
            "blog_detected": False,
            "explanation": "Platform Score: 50/100. No platform URLs detected — neutral score assigned."
        }
