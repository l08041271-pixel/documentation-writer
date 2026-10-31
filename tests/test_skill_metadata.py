import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_skill.py"

spec = importlib.util.spec_from_file_location("validate_skill", VALIDATOR)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class DocumentationWriterTests(unittest.TestCase):

    def test_frontmatter_metadata(self):
        content = validator.SKILL.read_text(encoding="utf-8")
        metadata, _ = validator.parse_frontmatter(content)

        self.assertEqual(metadata["name"], "documentation-writer")
        self.assertEqual(metadata["license"], "MIT")
        self.assertTrue(metadata["description"])

    def test_external_source_restriction(self):
        content = validator.SKILL.read_text(encoding="utf-8")

        self.assertIn(
            "You may not consult external websites or other sources "
            "unless I provide a link and instruct you to do so.",
            content,
        )

    def test_no_unauthorized_copying(self):
        content = validator.SKILL.read_text(encoding="utf-8")

        self.assertIn(
            "Do not copy external material unless I explicitly ask you to.",
            content,
        )

    def test_all_document_types(self):
        content = validator.SKILL.read_text(encoding="utf-8")

        for term in ("Tutorial", "How-to Guide", "Reference", "Explanation"):
            self.assertIn(term, content)

    def test_release_safety(self):
        content = validator.SKILL.read_text(encoding="utf-8")

        self.assertIn("Never publish, tag, merge, or deploy a release", content)

    def test_readme_declares_exact_development_version(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertRegex(
            readme,
            r"(?m)^\*\*Development version: 1\.1\.0\*\*$",
        )

    def test_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
