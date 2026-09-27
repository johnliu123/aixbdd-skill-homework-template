#!/usr/bin/env python3
"""
analyze_git_changes.py — Evidence-gathering script (Evidence First principle).

Collects the current git state into one structured JSON blob so the agent
never has to guess what changed: branch, staged/unstaged/untracked files,
diffs, special states (merge/rebase/cherry-pick in progress), and a best-
effort scan for accidentally-staged secrets.

Usage:
    python analyze_git_changes.py [--repo PATH] [--max-diff-lines N]

Output: JSON on stdout. Exit code 0 on success, 1 if not a git repo.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Windows consoles default to a legacy codepage (e.g. cp950) that cannot encode
# BOM/CJK/emoji bytes that show up in diffs or file contents. Force UTF-8 stdout
# so this never crashes regardless of the host OS/console.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "aws_access_key_id"),
    (r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", "private_key_block"),
    (r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|client[_-]?secret)\b\s*[=:]\s*['\"]?[A-Za-z0-9_\-/+]{12,}", "generic_secret_assignment"),
    (r"(?i)\bpassword\s*[=:]\s*['\"]?[^\s'\"]{4,}", "hardcoded_password"),
    (r"ghp_[A-Za-z0-9]{30,}", "github_token"),
    (r"sk-[A-Za-z0-9]{20,}", "openai_style_secret_key"),
]
SENSITIVE_FILENAME_PATTERNS = [r"(^|/)\.env(\..+)?$", r"(^|/)id_rsa$", r"\.pem$", r"\.pfx$", r"\.p12$"]


def run(args, cwd):
    try:
        result = subprocess.run(
            ["git"] + args, cwd=cwd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 127, "", "git executable not found"


def parse_porcelain(status_output):
    staged, unstaged, untracked, conflicted = [], [], [], []
    for line in status_output.splitlines():
        if not line:
            continue
        code = line[:2]
        path = line[3:]
        if "->" in path:  # rename
            path = path.split("->")[-1].strip()
        if code == "??":
            untracked.append(path)
        elif code[0] == "U" or code[1] == "U" or code == "AA" or code == "DD":
            conflicted.append(path)
        else:
            if code[0] not in (" ", "?"):
                staged.append(path)
            if code[1] not in (" ", "?"):
                unstaged.append(path)
    return staged, unstaged, untracked, conflicted


def scan_secrets(diff_text):
    findings = []
    for line in diff_text.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        for pattern, label in SECRET_PATTERNS:
            if re.search(pattern, line):
                findings.append({"type": label, "line_preview": line[:120]})
    return findings


def extract_issue_refs(branch_name):
    refs = set()
    for m in re.finditer(r"([A-Z]{2,}-\d+)", branch_name or ""):
        refs.add(m.group(1))
    for m in re.finditer(r"(?:^|[/_-])(\d{2,6})(?:[/_-]|$)", branch_name or ""):
        refs.add("#" + m.group(1))
    return sorted(refs)


def truncate(text, max_lines):
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text, False
    return "\n".join(lines[:max_lines]) + f"\n... [truncated, {len(lines) - max_lines} more lines omitted — request a specific file's diff instead]", True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--max-diff-lines", type=int, default=3000)
    args = parser.parse_args()
    repo = str(Path(args.repo).resolve())

    code, _, _ = run(["rev-parse", "--is-inside-work-tree"], repo)
    if code != 0:
        print(json.dumps({"error": "not_a_git_repository", "path": repo}))
        sys.exit(1)

    git_dir_code, git_dir_out, _ = run(["rev-parse", "--git-dir"], repo)
    git_dir = (Path(repo) / git_dir_out.strip()) if git_dir_out.strip() else None

    _, branch, _ = run(["branch", "--show-current"], repo)
    branch = branch.strip() or "(detached HEAD)"

    _, ahead_behind, _ = run(["rev-list", "--left-right", "--count", "HEAD...@{u}"], repo)
    ahead, behind = None, None
    if ahead_behind.strip():
        parts = ahead_behind.strip().split()
        if len(parts) == 2:
            ahead, behind = int(parts[0]), int(parts[1])

    _, status_out, _ = run(["status", "--porcelain=v1"], repo)
    staged, unstaged, untracked, conflicted = parse_porcelain(status_out)

    special_state = {}
    if git_dir:
        special_state["merge_in_progress"] = (git_dir / "MERGE_HEAD").exists()
        special_state["rebase_in_progress"] = (git_dir / "rebase-merge").exists() or (git_dir / "rebase-apply").exists()
        special_state["cherry_pick_in_progress"] = (git_dir / "CHERRY_PICK_HEAD").exists()
        merge_msg_path = git_dir / "MERGE_MSG"
        if merge_msg_path.exists():
            special_state["merge_msg"] = merge_msg_path.read_text(encoding="utf-8", errors="replace")

    _, staged_stat, _ = run(["diff", "--staged", "--stat"], repo)
    _, unstaged_stat, _ = run(["diff", "--stat"], repo)
    _, staged_diff_raw, _ = run(["diff", "--staged"], repo)
    _, unstaged_diff_raw, _ = run(["diff"], repo)

    staged_diff, staged_truncated = truncate(staged_diff_raw, args.max_diff_lines)
    unstaged_diff, unstaged_truncated = truncate(unstaged_diff_raw, args.max_diff_lines)

    secrets_found = scan_secrets(staged_diff_raw) + scan_secrets(unstaged_diff_raw)
    sensitive_files = [
        f for f in (staged + unstaged + untracked)
        if any(re.search(p, f) for p in SENSITIVE_FILENAME_PATTERNS)
    ]

    result = {
        "repo_path": repo,
        "branch": branch,
        "ahead": ahead,
        "behind": behind,
        "special_state": special_state,
        "status": {
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked,
            "conflicted": conflicted,
            "nothing_to_commit": not (staged or unstaged or untracked),
        },
        "staged_diff_stat": staged_stat,
        "unstaged_diff_stat": unstaged_stat,
        "staged_diff": staged_diff,
        "staged_diff_truncated": staged_truncated,
        "unstaged_diff": unstaged_diff,
        "unstaged_diff_truncated": unstaged_truncated,
        "issue_refs_from_branch": extract_issue_refs(branch),
        "security": {
            "possible_secrets": secrets_found,
            "sensitive_filenames": sensitive_files,
        },
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
