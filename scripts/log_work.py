#!/usr/bin/env python3
"""
PostToolUse hook: Edit/Write/Bash(rm) 実行後に .claude/logs/work/ へ自動追記する。

settings.json への設定例:
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write|Bash(rm *)",
      "hooks": [{"type": "command", "command": "python3 ~/.claude/scripts/log_work.py"}]
    }]
  }
"""

import json
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def find_logs_dir() -> Path:
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".claude").exists():
            logs = parent / ".claude" / "logs" / "work"
            logs.mkdir(parents=True, exist_ok=True)
            return logs
    fallback = cwd / ".claude" / "logs" / "work"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def to_relative(file_path: str) -> str:
    try:
        return str(Path(file_path).relative_to(Path.cwd()))
    except ValueError:
        return file_path


def is_in_project(file_path: str) -> bool:
    try:
        Path(file_path).relative_to(Path.cwd())
        return True
    except ValueError:
        return False


def is_new_file(rel_path: str) -> bool:
    """git で未追跡なら新規ファイルと判断する。"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", rel_path],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip().startswith("??")
    except Exception:
        return False


def get_session_file(logs_dir: Path, now: datetime) -> Path:
    today = now.strftime("%Y%m%d")
    existing = sorted(logs_dir.glob(f"{today}*_session.md"))
    if existing:
        return existing[-1]
    new_name = f"{now.strftime('%Y%m%d%H%M%S')}_session.md"
    session_file = logs_dir / new_name
    session_file.write_text(f"# セッション {now.strftime('%Y-%m-%d %H:%M')}\n\n## 作業ログ\n")
    return session_file


def make_diff_block(file_path: str, old_str: str, new_str: str) -> str:
    try:
        content = Path(file_path).read_text(errors="replace")
    except OSError:
        return ""

    idx = content.find(new_str)
    if idx == -1:
        old_lines = old_str.splitlines() if old_str else []
        new_lines = new_str.splitlines() if new_str else []
        lines = [f"  - {l}" for l in old_lines] + [f"  + {l}" for l in new_lines]
        return "\n".join(lines)

    start_line = content[:idx].count("\n")
    file_lines = content.splitlines()
    old_lines = old_str.splitlines() if old_str else []
    new_lines = new_str.splitlines() if new_str else []

    ctx = 3
    ctx_start = max(0, start_line - ctx)
    after_start = start_line + len(new_lines)
    ctx_end = min(len(file_lines), after_start + ctx)

    result = []
    for i in range(ctx_start, start_line):
        result.append(f"{i + 1:4}      {file_lines[i]}")
    for i, line in enumerate(old_lines):
        result.append(f"{start_line + i + 1:4} -    {line}")
    for i, line in enumerate(new_lines):
        result.append(f"{start_line + i + 1:4} +    {line}")
    for i in range(after_start, ctx_end):
        result.append(f"{i + 1:4}      {file_lines[i]}")

    return "\n".join(result)


def parse_rm_files(command: str) -> list[str]:
    """rm コマンドからファイルパス一覧を取得する。"""
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split()
    files = []
    skip_next = False
    for part in parts[1:]:
        if skip_next:
            skip_next = False
            continue
        if part in ("-t", "--target-directory"):
            skip_next = True
            continue
        if part.startswith("-"):
            continue
        files.append(part)
    return files


def update_pending(pending_file: Path, op: str, rel_path: str) -> None:
    """同じパスのエントリを最新の操作でテーブル行として上書きする。"""
    if pending_file.exists() and pending_file.read_text().strip():
        lines = pending_file.read_text().splitlines()
        new_lines = []
        for line in lines:
            # データ行のみ対象（ヘッダー・区切り行はそのまま保持）
            if line.startswith("| ") and not line.startswith("| 操作") and "---" not in line:
                parts = [p.strip() for p in line.strip().strip("|").split("|")]
                if len(parts) == 2 and parts[1] == rel_path:
                    continue  # 同じパスの古いエントリを除去
            new_lines.append(line)
        new_lines.append(f"| {op} | {rel_path} |")
        pending_file.write_text("\n".join(new_lines) + "\n")
    else:
        pending_file.write_text(
            f"| 操作 | ファイル |\n|------|----------|\n| {op} | {rel_path} |\n"
        )


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    now = datetime.now()
    logs_dir = find_logs_dir()
    session_file = get_session_file(logs_dir, now)
    pending = logs_dir.parent / "deploy" / ".pendings.md"
    pending.parent.mkdir(parents=True, exist_ok=True)

    if tool_name == "Edit":
        file_path = tool_input.get("file_path", "")
        if not file_path:
            return
        rel_path = to_relative(file_path)
        diff = make_diff_block(file_path, tool_input.get("old_string", ""), tool_input.get("new_string", ""))
        label = f"Update({rel_path})"
        body = f"```diff\n{diff}\n```" if diff else "(diff生成不可)"
        op = "Edit"

    elif tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        if not file_path:
            return
        rel_path = to_relative(file_path)
        op = "Create" if is_new_file(rel_path) else "Edit"
        label = f"{op}({rel_path})"
        body = ""

    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        # && / || / ; で分割して rm サブコマンドを抽出
        import re
        rm_files: list[str] = []
        for part in re.split(r"&&|\|\||;", command):
            part = part.strip()
            if part.startswith("rm ") or part == "rm":
                rm_files.extend(parse_rm_files(part))
        if not rm_files:
            return
        for f in rm_files:
            rel = to_relative(f)
            with open(session_file, "a") as sf:
                sf.write(f"\n### {now.strftime('%H:%M')} - Delete({rel})\n")
            if is_in_project(f):
                update_pending(pending, "Delete", rel)
        return

    else:
        return

    with open(session_file, "a") as f:
        f.write(f"\n### {now.strftime('%H:%M')} - {label}\n{body}\n")

    if is_in_project(file_path):
        update_pending(pending, op, rel_path)


if __name__ == "__main__":
    main()
