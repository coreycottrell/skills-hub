#!/usr/bin/env python3
"""
Skill Upload Tool — Packages and uploads a skill to the skills-hub registry.

Usage:
    python3 skill_upload.py <path_to_skill.md> [--repo REPO] [--dry-run]

What it does:
1. Reads the SKILL.md file
2. Validates/extracts YAML frontmatter (or generates stub if missing)
3. Adds entry to manifest.json
4. Commits and pushes to the registry repo
"""

import argparse
import json
import os
import re
import subprocess
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_REPO = "rkorus/skills-hub"
DEFAULT_BRANCH = "main"

REQUIRED_FRONTMATTER = ["name", "description"]
RECOMMENDED_FRONTMATTER = ["version", "author", "category", "tags"]

VALID_CATEGORIES = [
    "reasoning", "development", "communication", "operations",
    "decision-gates", "debugging", "security", "testing",
    "voice", "marketing", "governance", "meta", "onboarding",
    "comedy", "language", "infrastructure"
]


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from a SKILL.md file."""
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    if match:
        try:
            fm = yaml.safe_load(match.group(1)) or {}
            body = match.group(2)
            return fm, body
        except yaml.YAMLError:
            return {}, content
    return {}, content


def generate_frontmatter(skill_path: str, body: str) -> dict:
    """Generate stub frontmatter from file name and content."""
    name = Path(skill_path).stem
    if name == "SKILL":
        name = Path(skill_path).parent.name

    # Try to extract description from first paragraph
    lines = [l.strip() for l in body.split('\n') if l.strip() and not l.startswith('#')]
    description = lines[0][:200] if lines else f"Skill: {name}"

    return {
        "name": name,
        "description": description,
        "version": "1.0.0",
        "author": "unknown",
        "category": "uncategorized",
        "tags": [],
    }


def validate_frontmatter(fm: dict) -> list[str]:
    """Validate frontmatter and return list of issues."""
    issues = []
    for field in REQUIRED_FRONTMATTER:
        if field not in fm or not fm[field]:
            issues.append(f"Missing required field: {field}")

    if fm.get("category") and fm["category"] not in VALID_CATEGORIES:
        issues.append(f"Unknown category: {fm['category']}. Valid: {', '.join(VALID_CATEGORIES)}")

    if fm.get("tags") and not isinstance(fm["tags"], list):
        issues.append("'tags' should be a list")

    return issues


def build_manifest_entry(fm: dict, skill_path: str, content: str) -> dict:
    """Build a manifest.json entry from frontmatter."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "name": fm.get("name", "unknown"),
        "version": fm.get("version", "1.0.0"),
        "description": fm.get("description", ""),
        "author": fm.get("author", "unknown"),
        "category": fm.get("category", "uncategorized"),
        "tags": fm.get("tags", []),
        "file_path": skill_path,
        "created_at": now,
        "updated_at": now,
        "downloads": 0,
        "usage_count": 0,
        "rating": 0.0,
        "endorsements": 0,
        "status": "draft",
        "size_bytes": len(content.encode()),
        "dependencies": fm.get("dependencies", []),
    }


def clone_or_update_registry(repo: str, work_dir: str) -> str:
    """Clone or update the registry repo. Returns repo path."""
    repo_dir = os.path.join(work_dir, repo.split("/")[-1])

    if os.path.exists(repo_dir):
        subprocess.run(["git", "pull", "--rebase"], cwd=repo_dir, check=True, capture_output=True)
    else:
        # Check for PAT in git-credentials
        subprocess.run(
            ["git", "clone", f"https://github.com/{repo}.git", repo_dir],
            check=True, capture_output=True
        )

    return repo_dir


def upload_skill(skill_file: str, repo: str, dry_run: bool = False):
    """Main upload flow."""
    skill_path = Path(skill_file).resolve()
    if not skill_path.exists():
        print(f"Error: {skill_path} does not exist")
        sys.exit(1)

    content = skill_path.read_text()
    fm, body = extract_frontmatter(content)

    # Generate frontmatter if missing
    if not fm:
        print("No YAML frontmatter found. Generating stub...")
        fm = generate_frontmatter(str(skill_path), body)
        # Prepend frontmatter to content
        fm_yaml = yaml.dump(fm, default_flow_style=False, sort_keys=False)
        content = f"---\n{fm_yaml}---\n\n{body}"
        print(f"Generated frontmatter: {json.dumps(fm, indent=2)}")

    # Validate
    issues = validate_frontmatter(fm)
    if issues:
        print("Frontmatter issues:")
        for issue in issues:
            print(f"  - {issue}")
        if any("Missing required" in i for i in issues):
            print("Fix required fields before uploading.")
            sys.exit(1)

    # Build manifest entry
    skill_name = fm["name"]
    entry = build_manifest_entry(fm, f"skills/{skill_name}/SKILL.md", content)

    print(f"\nSkill: {skill_name}")
    print(f"Version: {fm.get('version', '?')}")
    print(f"Category: {fm.get('category', '?')}")
    print(f"Tags: {fm.get('tags', [])}")
    print(f"Status: draft (needs endorsement to publish)")

    if dry_run:
        print("\n[DRY RUN] Would upload:")
        print(f"  File: skills/{skill_name}/SKILL.md")
        print(f"  Manifest entry: {json.dumps(entry, indent=2)}")
        return entry

    # Clone/update registry
    work_dir = "/tmp/skills-hub-work"
    os.makedirs(work_dir, exist_ok=True)

    try:
        repo_dir = clone_or_update_registry(repo, work_dir)
    except subprocess.CalledProcessError as e:
        print(f"Error accessing registry repo: {e}")
        print("Make sure the repo exists and you have push access.")
        sys.exit(1)

    # Create skill directory and write file
    skill_dir = os.path.join(repo_dir, "skills", skill_name)
    os.makedirs(skill_dir, exist_ok=True)

    skill_dest = os.path.join(skill_dir, "SKILL.md")
    Path(skill_dest).write_text(content)

    # Update manifest
    manifest_path = os.path.join(repo_dir, "manifest.json")
    if os.path.exists(manifest_path):
        manifest = json.loads(Path(manifest_path).read_text())
    else:
        manifest = {"version": "1.0.0", "skills": [], "updated_at": ""}

    # Check if skill already exists (update vs add)
    existing_idx = None
    for i, s in enumerate(manifest["skills"]):
        if s["name"] == skill_name:
            existing_idx = i
            break

    if existing_idx is not None:
        # Preserve stats, update metadata
        old = manifest["skills"][existing_idx]
        entry["downloads"] = old.get("downloads", 0)
        entry["usage_count"] = old.get("usage_count", 0)
        entry["rating"] = old.get("rating", 0.0)
        entry["endorsements"] = old.get("endorsements", 0)
        entry["status"] = old.get("status", "draft")
        entry["created_at"] = old.get("created_at", entry["created_at"])
        manifest["skills"][existing_idx] = entry
        print(f"\nUpdated existing skill: {skill_name}")
    else:
        manifest["skills"].append(entry)
        print(f"\nAdded new skill: {skill_name}")

    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Write manifest
    Path(manifest_path).write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n"
    )

    # Commit and push
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)

    commit_msg = f"skill: {'update' if existing_idx is not None else 'add'} {skill_name} v{fm.get('version', '1.0.0')}"
    result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=repo_dir, capture_output=True, text=True
    )

    if result.returncode != 0:
        if "nothing to commit" in result.stdout:
            print("No changes to commit (skill already up to date)")
            return entry
        print(f"Commit error: {result.stderr}")
        sys.exit(1)

    push_result = subprocess.run(
        ["git", "push"],
        cwd=repo_dir, capture_output=True, text=True
    )

    if push_result.returncode != 0:
        print(f"Push error: {push_result.stderr}")
        sys.exit(1)

    print(f"Pushed to {repo}")
    return entry


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a skill to the skills-hub registry")
    parser.add_argument("skill_file", help="Path to the SKILL.md file")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"GitHub repo (default: {DEFAULT_REPO})")
    parser.add_argument("--dry-run", action="store_true", help="Validate without uploading")
    args = parser.parse_args()

    upload_skill(args.skill_file, args.repo, args.dry_run)
