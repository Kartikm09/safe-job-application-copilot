import unittest

from safe_job_copilot.analyzer import analyze_application


class ApplicationCopilotTests(unittest.TestCase):
    def test_high_fit_job_generates_application_pack(self):
        profile = {
            "name": "Kartik",
            "portfolio": "https://github.com/Kartikm09",
            "skills": ["python", "automation", "resume", "linkedin", "workflow"],
            "evidence": [{"title": "Lead Scout", "outcome": "Scored freelance jobs"}],
        }
        job = {
            "company": "Studio",
            "title": "Automation Builder",
            "description": "Python automation for resume and LinkedIn workflow",
            "required_skills": ["python", "automation", "resume", "linkedin"],
        }
        pack = analyze_application(profile, job)
        self.assertGreaterEqual(pack.score, 75)
        self.assertEqual(pack.recommendation, "apply")
        self.assertIn("python", pack.matched_keywords)
        self.assertTrue(pack.cover_letter.startswith("Hi Studio team"))
        self.assertEqual(pack.browser_fill_plan[-1]["value"], "[manual click only]")

    def test_bypass_request_is_flagged(self):
        profile = {"skills": ["python", "automation"], "evidence": []}
        job = {"description": "Need mass apply bot to bypass captcha", "required_skills": ["python"]}
        pack = analyze_application(profile, job)
        self.assertTrue(pack.risk_flags)
        self.assertNotEqual(pack.recommendation, "apply")


if __name__ == "__main__":
    unittest.main()

