#!/usr/bin/env bash
# プロジェクト初回起動時に必要なファイルを自動生成する

PROJECT_DIR="$(pwd)"
CLAUDE_DIR="$PROJECT_DIR/.claude"
GLOBAL_CLAUDE_DIR="$HOME/.claude"

# すべてのファイルが揃っていれば即終了
if [ -f "$PROJECT_DIR/.gitignore" ] && \
   [ -f "$PROJECT_DIR/.mcp.json.example" ] && \
   [ -f "$CLAUDE_DIR/settings.json" ] && \
   [ -f "$CLAUDE_DIR/settings.local.json" ] && \
   [ -f "$PROJECT_DIR/CLAUDE.local.md" ]; then
  exit 0
fi

# .gitignore
if [ ! -f "$PROJECT_DIR/.gitignore" ]; then
  if [ -f "$GLOBAL_CLAUDE_DIR/.gitignore" ]; then
    cp "$GLOBAL_CLAUDE_DIR/.gitignore" "$PROJECT_DIR/.gitignore"
    echo "[project_init] .gitignore を生成しました"
  else
    touch "$PROJECT_DIR/.gitignore"
    echo "[project_init] .gitignore を空ファイルで生成しました"
  fi
fi

# .mcp.json.example
if [ ! -f "$PROJECT_DIR/.mcp.json.example" ]; then
  if [ -f "$GLOBAL_CLAUDE_DIR/.mcp.json.example" ]; then
    cp "$GLOBAL_CLAUDE_DIR/.mcp.json.example" "$PROJECT_DIR/.mcp.json.example"
    echo "[project_init] .mcp.json.example を生成しました"
  else
    echo "{}" > "$PROJECT_DIR/.mcp.json.example"
    echo "[project_init] .mcp.json.example を空で生成しました"
  fi
fi

# .claude/settings.json
if [ ! -f "$CLAUDE_DIR/settings.json" ]; then
  mkdir -p "$CLAUDE_DIR"
  echo '{"permissions": {"allow": [], "deny": []}}' > "$CLAUDE_DIR/settings.json"
  echo "[project_init] .claude/settings.json を生成しました"
fi

# .claude/settings.local.json
if [ ! -f "$CLAUDE_DIR/settings.local.json" ]; then
  mkdir -p "$CLAUDE_DIR"
  echo '{}' > "$CLAUDE_DIR/settings.local.json"
  echo "[project_init] .claude/settings.local.json を生成しました"
fi

# CLAUDE.local.md
if [ ! -f "$PROJECT_DIR/CLAUDE.local.md" ]; then
  touch "$PROJECT_DIR/CLAUDE.local.md"
  echo "[project_init] CLAUDE.local.md を生成しました"
fi
