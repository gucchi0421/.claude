#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "").strip()

if not re.match(r"claude mcp add\b", cmd):
    sys.exit(0)

# シェルメタ文字によるコマンドインジェクション防止
if re.search(r'[;&|`$<>\n\\]', cmd):
    sys.exit(0)

script = Path.home() / "documents/dotfiles/packages/claude/.claude/scripts/setup-mcp.sh"
content = script.read_text()

if cmd in content:
    sys.exit(0)

# echo "Done." の行の直前に追記
new_content = content.replace('\necho "Done."', f'\n{cmd}\necho "Done."', 1)

if new_content == content:
    sys.exit(0)

script.write_text(new_content)
print(f"✓ setup-mcp.sh に追記しました: {cmd}")
