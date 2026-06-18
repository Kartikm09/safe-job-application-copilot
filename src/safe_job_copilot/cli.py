"""Command line interface for Safe Job Application Copilot."""

from __future__ import annotations

import argparse
import json

from .analyzer import analyze_application, load_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a safe, evidence-backed application pack.")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Analyze a profile against a job.")
    analyze.add_argument("profile_json")
    analyze.add_argument("job_json")
    analyze.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    pack = analyze_application(load_json(args.profile_json), load_json(args.job_json))
    if args.format == "json":
        print(json.dumps(pack.to_dict(), indent=2))
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


if __name__ == "__main__":
    main()

