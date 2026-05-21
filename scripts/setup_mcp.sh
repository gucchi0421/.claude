#!/usr/bin/env bash
# MCP サーバー一括セットアップスクリプト
# 新メンバーのセットアップや環境再構築時に実行する

set -euo pipefail

claude mcp add -s user playwright -- npx -y @playwright/mcp@latest --cdp-endpoint http://localhost:9222
claude mcp add context7 -s user -- npx -y @upstash/context7-mcp
claude mcp add brave-search -s user -- npx -y @anthropic/mcp-brave-search

echo "Done."
