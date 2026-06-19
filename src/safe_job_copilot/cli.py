"""Command line interface for Safe Job Application Copilot."""

from __future__ import annotations

import argparse
import json

from .analyzer import analyze_application, load_json
from .llm import LLMConfigurationError, LLMRequestError, generate_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a safe, evidence-backed application pack.")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Analyze a profile against a job.")
    analyze.add_argument("profile_json")
    analyze.add_argument("job_json")
    analyze.add_argument("--format", choices=["text", "json"], default="text")
    analyze.add_argument("--llm", action="store_true", help="Add optional Kimi/ZenMux proposal strategy.")
    args = parser.parse_args()

    profile = load_json(args.profile_json)
    job = load_json(args.job_json)
    pack = analyze_application(profile, job)
    llm_analysis = _optional_llm_analysis(args.llm, profile, job, pack)
    if args.format == "json":
        payload = pack.to_dict()
        if llm_analysis:
            payload["llm_analysis"] = llm_analysis
        print(json.dumps(payload, indent=2))
        return

    print("Safe Job Application Copilot")
    print(f"Score: {pack.score}/100")
    print(f"Recommendation: {pack.recommendation}")
    print(f"Matched: {', '.join(pack.matched_keywords) or 'none'}")
    print(f"Missing: {', '.join(pack.missing_keywords) or 'none'}")
    if pack.risk_flags:
        print("Risks:")
        for risk in pack.risk_flags:
            print(f"- {risk}")
    print("\nCV Bullets")
    for bullet in pack.cv_bullets:
        print(f"- {bullet}")
    print("\nCover Letter")
    print(pack.cover_letter)
    print("\nApproval Gates")
    for gate in pack.approval_gates:
        print(f"- {gate}")
    if llm_analysis:
        print("\nKimi Application Strategy")
        print(llm_analysis)


def _optional_llm_analysis(enabled: bool, profile: dict[str, object], job: dict[str, object], pack: object) -> str | None:
    if not enabled:
        return None
    prompt = (
        "Create a truthful, human-reviewed freelance/job application strategy from this evidence. "
        "Do not fabricate experience, do not suggest automated submission, and keep every claim grounded.\n\n"
        f"PROFILE:\n{json.dumps(profile, indent=2)}\n\n"
        f"JOB:\n{json.dumps(job, indent=2)}\n\n"
        f"DETERMINISTIC PACK:\n{json.dumps(pack.to_dict(), indent=2)}\n\n"
        "Return: 1) strongest positioning, 2) improved cover-letter draft, "
        "3) five truthful CV/profile bullets, 4) manual application checklist. "
        "Keep the full answer under 350 words with compact bullets."
    )
    try:
        return generate_text(
            prompt,
            system="You are a careful job-application strategist who avoids fabricated claims.",
            max_tokens=6000,
        )
    except (LLMConfigurationError, LLMRequestError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
