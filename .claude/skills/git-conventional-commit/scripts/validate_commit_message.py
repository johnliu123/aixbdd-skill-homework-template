#!/usr/bin/env python3
"""
validate_commit_message.py — Validation Before Commit script.

Validates a drafted commit message against Conventional Commits v1.0.0
rules plus the @commitlint/config-conventional stylistic defaults, plus a
few extra semantic/anti-pattern checks this skill cares about (vague
subjects, "and"-joined subjects, misclassified breaking changes).

Usage:
    python validate_commit_message.py --file msg.txt [options]
    python validate_commit_message.py --message "feat(api): add x" [options]
    echo "feat: add x" | python validate_commit_message.py

Options:
    --types feat,fix,docs,...     Allowed type list (default: Angular 11 set)
    --scopes a,b,c                Allowed scope list (default: no restriction)
    --header-max N                Max header length, error threshold (default 100)
    --body-line-max N             Max body/footer line length (default 100)
    --allow-any-type              Skip type-enum check entirely (project uses free-form types)

Exit code: 0 if no errors (warnings do not fail), 1 if any error.
Output: JSON {"valid", "errors", "warnings", "parsed"} on stdout.
"""
import argparse
import json
import re
import sys

# Windows consoles default to a legacy codepage (e.g. cp950) that cannot encode
# CJK/emoji bytes that show up in commit messages. Force UTF-8 stdout/stdin so
# this never crashes regardless of the host OS/console.
for _stream in (sys.stdout, sys.stderr, sys.stdin):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_TYPES = ["build", "chore", "ci", "docs", "feat", "fix", "perf", "refactor", "revert", "style", "test"]
VAGUE_SUBJECTS = {
    "wip", "fix bug", "fixed bug", "bug fix", "update", "updates", "changes",
    "misc", "minor fix", "stuff", "fix stuff", "small fix", "various fixes",
    "cleanup", "test", "tmp", "temp", "asdf", "xxx", "fix issue", "改動", "修正",
    "更新", "調整", "修改", "wip commit",
}
HEADER_RE = re.compile(r"^(?P<type>[^(!:\s]+)(?:\((?P<scope>[^()]+)\))?(?P<bang>!)?:\s(?P<description>.*)$")


def classify_case(s):
    if not s:
        return "empty"
    if s.isupper():
        return "upper-case"
    words = s.split()
    if len(words) > 1 and all(w[:1].isupper() for w in words if w[:1].isalpha()):
        return "start-case"
    if s[:1].isupper() and s[1:2].islower():
        # Could be sentence-case (rest lower) vs PascalCase (multiple caps mid-word)
        if re.search(r"[a-z][A-Z]", s):
            return "pascal-case"
        return "sentence-case"
    return "lower-or-camel-case"


def split_message(raw):
    lines = raw.rstrip("\n").split("\n")
    header = lines[0] if lines else ""
    rest = lines[1:]
    body_lines, footer_lines = [], []
    footer_token_re = re.compile(r"^(BREAKING[ -]CHANGE|[A-Za-z][\w-]*)(: | #)")
    # Footers are the trailing contiguous block of footer-token lines
    # (allowing wrapped continuation lines), separated from body by a blank line.
    idx = len(rest)
    in_footer = False
    footer_start = None
    for i in range(len(rest) - 1, -1, -1):
        line = rest[i]
        if footer_token_re.match(line):
            footer_start = i
            in_footer = True
        elif in_footer and line.strip() != "":
            continue  # continuation line of a wrapped footer value
        elif in_footer and line.strip() == "":
            break
        else:
            break
    if footer_start is not None:
        # walk back further to include a contiguous footer block from footer_start
        body_lines = rest[:footer_start]
        footer_lines = rest[footer_start:]
        if body_lines and body_lines[-1].strip() == "":
            body_lines = body_lines[:-1]
    else:
        body_lines = rest
    return header, body_lines, footer_lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    parser.add_argument("--message")
    parser.add_argument("--types", default=",".join(DEFAULT_TYPES))
    parser.add_argument("--scopes", default="")
    parser.add_argument("--header-max", type=int, default=100)
    parser.add_argument("--body-line-max", type=int, default=100)
    parser.add_argument("--allow-any-type", action="store_true")
    args = parser.parse_args()

    had_bom = False
    if args.message is not None:
        raw = args.message
    elif args.file:
        raw_bytes = open(args.file, "rb").read()
        had_bom = raw_bytes.startswith(b"\xef\xbb\xbf")
        raw = raw_bytes.decode("utf-8-sig", errors="replace")
    else:
        raw = sys.stdin.read()
        had_bom = raw.startswith("\ufeff")
        raw = raw.lstrip("\ufeff")

    # Normalize CRLF/CR (common on Windows, e.g. PowerShell `Out-File`) to LF
    # before any line-based parsing, otherwise a trailing "\r" on the header
    # line falsely trips header-trim, and body/footer line-length counts skew.
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")

    errors, warnings = [], []
    if had_bom:
        warnings.append(
            "byte-order-mark: the message file starts with a UTF-8 BOM, which was stripped only "
            "for this validation run. The actual file on disk still has it, and `git commit -F "
            "<file>` will read the raw bytes -- corrupting the type/description. On Windows, avoid "
            "`Out-File -Encoding utf8` (PowerShell); write the file without a BOM instead "
            "(see references/tooling.md, 'Windows BOM pitfall')"
        )
    allowed_types = [t.strip().lower() for t in args.types.split(",") if t.strip()]
    allowed_scopes = [s.strip().lower() for s in args.scopes.split(",") if s.strip()]

    if not raw.strip():
        print(json.dumps({"valid": False, "errors": ["message is empty"], "warnings": [], "parsed": None}))
        sys.exit(1)

    header, body_lines, footer_lines = split_message(raw)
    header_stripped = header.strip()
    if header != header_stripped:
        errors.append("header-trim: header has leading/trailing whitespace")

    m = HEADER_RE.match(header_stripped)
    parsed = {"header": header_stripped, "type": None, "scope": None, "breaking_bang": False, "description": None}

    if not m:
        errors.append(
            "header-format: does not match '<type>[(scope)][!]: <description>'. "
            "Got: " + repr(header_stripped)
        )
    else:
        parsed.update(
            type=m.group("type"), scope=m.group("scope"),
            breaking_bang=bool(m.group("bang")), description=m.group("description"),
        )
        t = m.group("type")
        if not t:
            errors.append("type-empty: type is required")
        else:
            if t != t.lower():
                errors.append(f"type-case: type '{t}' must be lower-case")
            if not args.allow_any_type and t.lower() not in allowed_types:
                errors.append(f"type-enum: type '{t}' not in allowed list {allowed_types}")

        scope = m.group("scope")
        if scope:
            if scope != scope.lower() or " " in scope:
                warnings.append(f"scope-case: scope '{scope}' should be lower-case kebab-case, no spaces")
            if allowed_scopes and scope.lower() not in allowed_scopes:
                errors.append(f"scope-enum: scope '{scope}' not in allowed list {allowed_scopes}")

        desc = m.group("description")
        if not desc or not desc.strip():
            errors.append("subject-empty: description must not be empty")
        else:
            desc_stripped = desc.strip()
            case = classify_case(desc_stripped)
            if case in ("sentence-case", "start-case", "pascal-case", "upper-case"):
                warnings.append(f"subject-case: description looks like {case}; conventional style prefers lower-case start")
            if desc_stripped.endswith("."):
                errors.append("subject-full-stop: description must not end with a period")
            if desc_stripped.lower() in VAGUE_SUBJECTS:
                errors.append(f"subject-too-vague: '{desc_stripped}' does not describe a concrete change")
            if re.search(r"\band\b", desc_stripped, re.IGNORECASE):
                warnings.append("subject-contains-'and': consider whether this commit should be split in two")
            if re.search(r"\.(js|ts|py|rb|go|java|md|json|yml|yaml)\b", desc_stripped):
                warnings.append("subject-lists-filenames: describe the meaning of the change, not the files touched")

    if len(header_stripped) > args.header_max:
        errors.append(f"header-max-length: header is {len(header_stripped)} chars, max {args.header_max}")
    elif len(header_stripped) > 72:
        warnings.append(f"header-length: {len(header_stripped)} chars exceeds the classic 72-char git-tooling guideline")

    if body_lines and body_lines[0].strip() != "" and not any(l.strip() for l in body_lines[:1]) is False:
        pass  # first body line handled below
    if body_lines:
        if body_lines[0].strip() != "" and len(raw.rstrip("\n").split("\n")) > 1 and raw.split("\n")[1].strip() != "":
            warnings.append("body-leading-blank: body should begin one blank line after the description")
        for i, line in enumerate(body_lines):
            if len(line) > args.body_line_max and "http://" not in line and "https://" not in line:
                errors.append(f"body-max-line-length: body line {i+1} is {len(line)} chars (max {args.body_line_max})")

    is_breaking = parsed["breaking_bang"]
    breaking_footer_found = False
    for i, line in enumerate(footer_lines):
        if len(line) > args.body_line_max and "http://" not in line and "https://" not in line:
            errors.append(f"footer-max-line-length: footer line {i+1} is {len(line)} chars (max {args.body_line_max})")
        if re.match(r"^BREAKING[ -]CHANGE:\s", line):
            breaking_footer_found = True
            is_breaking = True
        elif re.match(r"(?i)^breaking[ -]change:\s", line):
            warnings.append("breaking-change-casing: 'BREAKING CHANGE' must be exactly UPPERCASE to be recognized by tooling")
    if footer_lines and footer_lines[0].strip() == "":
        warnings.append("footer-leading-blank: unexpected blank line at start of footer block")

    if parsed.get("type") in ("chore", "style", "docs", "test", "build", "ci") and is_breaking:
        warnings.append(
            f"type-breaking-mismatch: type '{parsed.get('type')}' combined with a BREAKING CHANGE is "
            "commonly ignored by release tooling (e.g. semantic-release) unless custom release rules are configured. "
            "Confirm this is intentional"
        )

    parsed["is_breaking_change"] = is_breaking
    parsed["breaking_change_footer_present"] = breaking_footer_found
    parsed["body"] = "\n".join(body_lines).strip()
    parsed["footer"] = "\n".join(footer_lines).strip()

    result = {"valid": len(errors) == 0, "errors": errors, "warnings": warnings, "parsed": parsed}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
