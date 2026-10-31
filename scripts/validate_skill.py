#!/usr/bin/env python3
"""Validate Documentation Writer skill structure and mandatory policies."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/documentation-writer/SKILL.md"
README = ROOT / "README.md"

REQUIRED_METADATA = ("description", "name", "license")

REQUIRED_SECTIONS = (
    "GUIDING PRINCIPLES",
    "THE FOUR DOCUMENT TYPES",
    "WORKFLOW",
    "Research and source authorization",
    "Technical quality assurance",
    "Documentation quality assurance",
    "RELEASE AND VERSION CONTROL",
)

MANDATORY_POLICIES = (
    "You may not consult external websites or other sources unless I provide a link and instruct you to do so.",
    "DO NOT copy content from them unless the user explicitly asks you to.",
    "Do not copy external material unless I explicitly ask you to.",
)


def parse_frontmatter(content):
    if not content.startswith("---\n"):
        raise ValueError("Missing YAML frontmatter opening delimiter.")

    parts = content.split("---", 2)
    if len(parts) != 3:
        raise ValueError("Missing YAML frontmatter closing delimiter.")

    metadata = {}
    for line in parts[1].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"Invalid metadata line: {line}")
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()

    return metadata, parts[2]


def validate():
    errors = []

    if not SKILL.is_file():
        return ["Skill file is missing."]

    if not README.is_file():
        errors.append("README.md is missing.")

    content = SKILL.read_text(encoding="utf-8")

    try:
        metadata, body = parse_frontmatter(content)
    except ValueError as exc:
        return [str(exc)]

    for key in REQUIRED_METADATA:
        if not metadata.get(key):
            errors.append(f"Missing required metadata: {key}")

    if metadata.get("name") != "documentation-writer":
        errors.append("Unexpected skill name.")

    if metadata.get("license") != "MIT":
        errors.append("Expected MIT license metadata.")

    for section in REQUIRED_SECTIONS:
        if section.lower() not in body.lower():
            errors.append(f"Missing required section: {section}")

    for policy in MANDATORY_POLICIES:
        if policy not in body:
            errors.append(f"Mandatory policy missing or changed: {policy}")

    if len(re.findall(r"(?m)^```", body)) % 2:
        errors.append("Unclosed Markdown code fence.")

    for number, line in enumerate(content.splitlines(), 1):
        if line.rstrip() != line:
            errors.append(f"Trailing whitespace on line {number}.")

    if README.is_file():
        readme = README.read_text(encoding="utf-8")
        if not re.search(r"(?m)^\*\*Development version: 1\.1\.0\*\*$", readme):
            errors.append("README does not declare exact development version 1.1.0.")

    return errors


if __name__ == "__main__":
    problems = validate()

    if problems:
        print("VALIDATION FAILED")
        for problem in problems:
            print(f"- {problem}")
        sys.exit(1)

    print("VALIDATION PASSED")
    print("Skill metadata, required sections, source policies, and Markdown checks passed.")
