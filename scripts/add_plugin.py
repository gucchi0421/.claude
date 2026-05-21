#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "")

m = re.match(r"^\s*claude plugin install\s+(\S+)", cmd)
if not m:
    sys.exit(0)

plugin = m.group(1)

# プラグイン名に不正文字が含まれていれば拒否
if not re.match(r'^[\w\-\/]+$', plugin):
    sys.exit(0)

script = Path.home() / "documents/dotfiles/packages/claude/.claude/scripts/setup-plugins.sh"

content = script.read_text()

# codex は末尾で個別インストールしているので除外
if plugin == "codex":
    sys.exit(0)

# 既に含まれていればスキップ
if re.search(rf"^\s+{re.escape(plugin)}\s*$", content, re.MULTILINE):
    sys.exit(0)

# PLUGINS配列の閉じ括弧の直前に追記
marker = "\n)\n\nfor plugin"
if marker not in content:
    sys.exit(0)

new_content = content.replace(marker, f"\n  {plugin}{marker}", 1)

script.write_text(new_content)
print(f"✓ {plugin} を setup-plugins.sh に追記しました")
