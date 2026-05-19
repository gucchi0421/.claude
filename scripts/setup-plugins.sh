#!/usr/bin/env bash
# Claude Code プラグイン一括インストールスクリプト
# 新メンバーのセットアップや環境再構築時に実行する

set -euo pipefail

PLUGINS=(
  claude-code-setup
  code-simplifier
  commit-commands
  feature-dev
  figma
  frontend-design
  github
  gopls-lsp
  php-lsp
  playwright
  pyright-lsp
  security-guidance
)

for plugin in "${PLUGINS[@]}"; do
  echo "Installing: $plugin"
  claude plugin install "$plugin"
done

# openai-codex マーケットプレイスのプラグイン
claude plugin install codex

echo "Done."
