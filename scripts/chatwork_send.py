#!/usr/bin/env python3
"""Chatwork メッセージ送信スクリプト。プロジェクトルートの .env から API キーを読む。"""

import argparse
import os
import re
import sys
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path


def load_env(start_dir: Path) -> dict[str, str]:
    """カレントディレクトリから親を辿って .env を探してロードする。"""
    for directory in [start_dir, *start_dir.parents]:
        env_file = directory / ".env"
        if env_file.exists():
            env: dict[str, str] = {}
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
            return env
    return {}


def send_message(room_id: str, message: str, api_key: str) -> None:
    url = f"https://api.chatwork.com/v2/rooms/{room_id}/messages"
    data = urllib.parse.urlencode({"body": message}).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"X-ChatWorkToken": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"送信完了 (message_id: {__import__('json').loads(resp.read())['message_id']})")
    except urllib.error.HTTPError as e:
        print(f"エラー: {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chatwork にメッセージを送信する")
    parser.add_argument("room_id", help="送信先ルームID")
    parser.add_argument("message", nargs="?", help="メッセージ本文（省略時は stdin から読む）")
    args = parser.parse_args()

    env = load_env(Path.cwd())
    api_key = env.get("CLAUDE_CHATWORK_API_KEY") or os.environ.get("CLAUDE_CHATWORK_API_KEY", "")
    if not api_key:
        print("エラー: CLAUDE_CHATWORK_API_KEY が .env に見つかりません", file=sys.stderr)
        sys.exit(1)

    room_id = args.room_id.lstrip("rid")
    if not re.match(r'^\d+$', room_id):
        print("エラー: room_id は数値のみ使用できます", file=sys.stderr)
        sys.exit(1)
    args.room_id = room_id

    message = args.message if args.message else sys.stdin.read().strip()
    if not message:
        print("エラー: メッセージが空です", file=sys.stderr)
        sys.exit(1)

    send_message(args.room_id, message, api_key)


if __name__ == "__main__":
    main()
