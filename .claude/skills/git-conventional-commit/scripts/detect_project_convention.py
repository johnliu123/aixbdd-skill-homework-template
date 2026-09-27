#!/usr/bin/env python3
"""
detect_project_convention.py — Project-Aware detection script.

Before inventing a commit style, check what the project already does:
- Is there an enforced convention (commitlint/husky/commitizen config)?
- What does real commit history actually look like (types, scopes, body
  usage, emoji, language)?

This script never *decides* the convention for the agent — it only reports
evidence. The agent (per SKILL.md) is responsible for the judgment call of
"follow existing convention" vs "ask the user" vs "propose Conventional
Commits defaults".

Usage:
    python detect_project_convention.py [--repo PATH] [--history-size N]

Output: JSON on stdout.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Windows consoles default to a legacy codepage (e.g. cp950) that cannot encode
# BOM/CJK/emoji bytes that show up in commit history. Force UTF-8 stdout so
# this never crashes regardless of the host OS/console.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

CONFIG_CANDIDATES = [
    "commitlint.config.js", "commitlint.config.cjs", "commitlint.config.mjs",
    "commitlint.config.ts", ".commitlintrc", ".commitlintrc.json",
    ".commitlintrc.js", ".commitlintrc.yml", ".commitlintrc.yaml",
    ".cz-config.js", ".czrc",
]
HOOK_CANDIDATES = [".husky/commit-msg", ".husky/prepare-commit-msg", ".git/hooks/commit-msg"]
DOC_CANDIDATES = ["CONTRIBUTING.md", "CONTRIBUTING.rst", "docs/CONTRIBUTING.md", ".github/CONTRIBUTING.md"]

CONVENTIONAL_HEADER_RE = re.compile(r"^([a-zA-Z]+)(\(([^()]+)\))?(!)?: .+")
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F900-\U0001F9FF]"
)
CJK_RE = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff]")


def run(args, cwd):
    try:
        result = subprocess.run(
            ["git"] + args, cwd=cwd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 127, "", "git executable not found"


def find_config_files(repo):
    found = []
    for name in CONFIG_CANDIDATES:
        p = Path(repo) / name
        if p.exists():
            found.append(str(p.relative_to(repo)))
    pkg = Path(repo) / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8", errors="replace"))
            if "commitlint" in data:
                found.append("package.json#commitlint")
            if isinstance(data.get("config"), dict) and "commitizen" in data["config"]:
                found.append("package.json#config.commitizen")
        except Exception:
            pass
    return found


def find_hooks(repo):
    return [h for h in HOOK_CANDIDATES if (Path(repo) / h).exists()]


def find_docs(repo):
    found = []
    for name in DOC_CANDIDATES:
        p = Path(repo) / name
        if p.exists():
            text = p.read_text(encoding="utf-8", errors="replace")
            if re.search(r"(?i)commit", text):
                found.append(str(p.relative_to(repo)))
    return found


def try_extract_enum(repo, key):
    """Best-effort regex extraction of type-enum/scope-enum arrays from any
    commitlint config file text, without executing JS."""
    values = set()
    for name in CONFIG_CANDIDATES:
        p = Path(repo) / name
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(rf"{key}[^\[]*\[([^\]]*)\]", text):
            for item in re.findall(r"['\"]([\w./-]+)['\"]", m.group(1)):
                values.add(item)
    return sorted(values)


def analyze_history(repo, history_size):
    _, out, _ = run(["log", f"-n{history_size}", "--pretty=format:%s"], repo)
    subjects = [s for s in out.split("\n") if s.strip()]
    total = len(subjects)
    if total == 0:
        return {"total_analyzed": 0}

    conventional_matches = 0
    types_count, scopes_count = {}, {}
    emoji_count, cjk_count, total_len = 0, 0, 0

    for s in subjects:
        total_len += len(s)
        if EMOJI_RE.search(s):
            emoji_count += 1
        if CJK_RE.search(s):
            cjk_count += 1
        m = CONVENTIONAL_HEADER_RE.match(s)
        if m:
            conventional_matches += 1
            t = m.group(1).lower()
            types_count[t] = types_count.get(t, 0) + 1
            if m.group(3):
                sc = m.group(3).lower()
                scopes_count[sc] = scopes_count.get(sc, 0) + 1

    _, body_out, _ = run(["log", f"-n{min(30, history_size)}", "--pretty=format:%B%x00"], repo)
    bodies = [b for b in body_out.split("\x00") if b.strip()]
    with_body = sum(1 for b in bodies if len(b.strip().splitlines()) > 1)

    return {
        "total_analyzed": total,
        "conventional_compliance_rate": round(conventional_matches / total, 2),
        "types_used": dict(sorted(types_count.items(), key=lambda x: -x[1])),
        "scopes_used": dict(sorted(scopes_count.items(), key=lambda x: -x[1])),
        "gitmoji_style_ratio": round(emoji_count / total, 2),
        "chinese_or_cjk_ratio": round(cjk_count / total, 2),
        "avg_subject_length": round(total_len / total, 1),
        "body_usage_rate": round(with_body / len(bodies), 2) if bodies else None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--history-size", type=int, default=100)
    args = parser.parse_args()
    repo = str(Path(args.repo).resolve())

    code, _, _ = run(["rev-parse", "--is-inside-work-tree"], repo)
    if code != 0:
        print(json.dumps({"error": "not_a_git_repository", "path": repo}))
        sys.exit(1)

    config_files = find_config_files(repo)
    hooks = find_hooks(repo)
    docs = find_docs(repo)
    history = analyze_history(repo, args.history_size)
    type_enum = try_extract_enum(repo, "type-enum")
    scope_enum = try_extract_enum(repo, "scope-enum")

    enforcement_detected = bool(config_files or hooks)
    compliance = history.get("conventional_compliance_rate", 0) or 0

    if enforcement_detected or compliance >= 0.6:
        recommendation = "FOLLOW_DETECTED_CONVENTION"
    elif history.get("total_analyzed", 0) == 0:
        recommendation = "NO_HISTORY_USE_ANGULAR_DEFAULTS"
    elif history.get("gitmoji_style_ratio", 0) >= 0.4:
        recommendation = "GITMOJI_STYLE_DETECTED_ASK_USER"
    elif compliance < 0.3:
        recommendation = "NO_ESTABLISHED_CONVENTION_PROPOSE_DEFAULTS"
    else:
        recommendation = "MIXED_HISTORY_ASK_USER_OR_USE_MAJORITY"

    result = {
        "repo_path": repo,
        "enforcement": {
            "config_files": config_files,
            "git_hooks": hooks,
            "contributing_docs_mentioning_commits": docs,
            "detected_type_enum": type_enum,
            "detected_scope_enum": scope_enum,
        },
        "history_analysis": history,
        "recommendation": recommendation,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
