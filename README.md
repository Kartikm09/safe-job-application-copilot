# Safe Job Application Copilot

AI-assisted job application copilot for students, freelancers, and international job seekers.

This project turns a profile evidence file and a job description into a practical application pack: fit score, matched skills, missing keywords, tailored CV bullets, cover-letter draft, and a browser-fill plan. It is intentionally a copilot, not a hidden auto-apply bot: every external action stays behind a human review gate.

## Why It Exists

Many job seekers waste time applying randomly or rewriting the same profile manually. This repo shows how to automate the thinking layer while avoiding risky platform behavior:

- no credentials
- no cookies
- no CAPTCHA bypass
- no silent job submissions
- no fabricated experience

## Quick Start

```bash
PYTHONPATH=src python3 -m safe_job_copilot.cli analyze examples/profile.json examples/job.json
```

JSON output:

```bash
PYTHONPATH=src python3 -m safe_job_copilot.cli analyze examples/profile.json examples/job.json --format json
```

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Output

The CLI returns:

- fit score and recommendation
- matched keywords and missing keywords
- risk flags
- evidence-backed CV bullets
- cover-letter draft
- browser-fill plan for manual application forms
- required human approval gates before submit

## Portfolio Signal

This repo supports profile positioning around:

- AI job application automation
- resume/job-fit matching
- cover-letter drafting
- browser workflow planning
- human-in-the-loop automation
- safe AI agents
- Python CLI tooling

