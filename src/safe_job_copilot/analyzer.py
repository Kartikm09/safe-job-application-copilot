"""Analyze job fit and prepare human-approved application packs."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


STOPWORDS = {
    "and", "the", "for", "with", "you", "your", "our", "are", "this", "that",
    "from", "will", "have", "has", "into", "work", "role", "job", "need",
    "using", "about", "can", "all", "any", "who", "must", "should", "team",
}

RISK_TERMS = {
    "captcha": "Platform or CAPTCHA bypass request detected.",
    "bypass": "Potential platform-bypass wording detected.",
    "fake experience": "Experience fabrication request detected.",
    "guaranteed job": "Unrealistic guarantee wording detected.",
    "mass apply": "Mass-application wording requires stronger review.",
}


@dataclass(frozen=True)
class ApplicationPack:
    score: int
    recommendation: str
    matched_keywords: tuple[str, ...]
    missing_keywords: tuple[str, ...]
    risk_flags: tuple[str, ...]
    cv_bullets: tuple[str, ...]
    cover_letter: str
    browser_fill_plan: tuple[dict[str, str], ...]
    approval_gates: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def analyze_application(profile: dict[str, Any], job: dict[str, Any]) -> ApplicationPack:
    profile_text = _flatten(profile)
    job_text = _flatten(job)
    profile_terms = _keywords(profile_text)
    job_terms = _keywords(job_text)

    required = set(job.get("required_skills", [])) | _important_terms(job_terms)
    profile_skill_set = {item.lower() for item in profile.get("skills", [])}
    profile_all = profile_terms | profile_skill_set

    matched = sorted(term for term in required if term.lower() in profile_all or term.lower() in profile_text)
    missing = sorted(term for term in required if term not in matched)[:12]
    risks = _risk_flags(job_text)

    base = 40 + min(45, len(matched) * 7) - min(25, len(missing) * 3) - len(risks) * 12
    score = max(0, min(100, base))
    recommendation = "apply" if score >= 75 and not risks else "tailor" if score >= 50 else "skip"

    evidence = profile.get("evidence", [])
    cv_bullets = tuple(_cv_bullets(evidence, matched))[:5]
    cover_letter = _cover_letter(profile, job, matched, cv_bullets)
    fill_plan = _browser_fill_plan(profile, job, cover_letter)

    approval_gates = (
        "Review generated CV bullets against real experience.",
        "Review cover letter before copying into any platform.",
        "Manually confirm every form field before submit.",
        "Do not bypass CAPTCHA, payment, login, or platform safety checks.",
    )

    return ApplicationPack(
        score=score,
        recommendation=recommendation,
        matched_keywords=tuple(matched),
        missing_keywords=tuple(missing),
        risk_flags=tuple(risks),
        cv_bullets=cv_bullets,
        cover_letter=cover_letter,
        browser_fill_plan=tuple(fill_plan),
        approval_gates=approval_gates,
    )


def _flatten(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_flatten(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_flatten(item) for item in value)
    return str(value).lower()


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-z][a-z0-9+.-]{2,}", text.lower())
    return {word for word in words if word not in STOPWORDS}


def _important_terms(terms: set[str]) -> set[str]:
    priority = {
        "python", "automation", "agent", "agents", "llm", "evaluation", "red",
        "teaming", "linkedin", "resume", "cover", "letter", "workflow",
        "browser", "upwork", "germany", "student", "scraping", "crm",
    }
    return {term for term in terms if term in priority}


def _risk_flags(text: str) -> list[str]:
    return [message for term, message in RISK_TERMS.items() if term in text]


def _cv_bullets(evidence: list[dict[str, Any]], matched: list[str]) -> list[str]:
    bullets: list[str] = []
    matched_text = ", ".join(matched[:4]) or "relevant workflow skills"
    for item in evidence:
        title = item.get("title", "Relevant project")
        outcome = item.get("outcome", "Produced a measurable workflow output")
        bullets.append(f"{title}: {outcome} using {matched_text}.")
    return bullets or [f"Built relevant workflow evidence around {matched_text}."]


def _cover_letter(profile: dict[str, Any], job: dict[str, Any], matched: list[str], bullets: tuple[str, ...]) -> str:
    name = profile.get("name", "Kartik Mishra")
    role = job.get("title", "this role")
    company = job.get("company", "your team")
    matched_phrase = ", ".join(matched[:6]) or "AI workflow automation"
    proof = bullets[0] if bullets else "I can show relevant public-safe project examples."
    return (
        f"Hi {company} team,\n\n"
        f"I am interested in {role}. My strongest match is {matched_phrase}. "
        f"{proof} I would approach this with a human-reviewed workflow: map the role requirements, "
        f"tailor only truthful experience, prepare the application materials, and keep final submission under manual approval.\n\n"
        f"Best,\n{name}"
    )


def _browser_fill_plan(profile: dict[str, Any], job: dict[str, Any], cover_letter: str) -> list[dict[str, str]]:
    return [
        {"field": "full_name", "value": profile.get("name", ""), "approval": "verify identity field"},
        {"field": "email", "value": profile.get("email", "[manual]"), "approval": "verify contact details"},
        {"field": "portfolio", "value": profile.get("portfolio", ""), "approval": "verify public portfolio link"},
        {"field": "cover_letter", "value": cover_letter, "approval": "review before paste"},
        {"field": "submit", "value": "[manual click only]", "approval": "human final approval required"},
    ]
