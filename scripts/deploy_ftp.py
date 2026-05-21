#!/usr/bin/env python3
"""
FTPデプロイスクリプト。

- .env から CLAUDE_FTP_HOST / CLAUDE_FTP_USERNAME / CLAUDE_FTP_PASSWORD を読む
- .claude/settings.ftp.json でローカル→リモートパスを解決
- .claude/logs/deploy/.pendings.md の操作一覧を処理
  - Edit/Create: バックアップ後アップロード
  - Delete: バックアップ後リモート削除
- 結果を .claude/logs/deploy/YYYYMMDDHHMMSS.md に記録
- 完了後 .pendings.md をリセット

使い方:
  python3 ~/.claude/scripts/ftp_deploy.py
"""

import ftplib
import json
import os
import posixpath
import sys
from datetime import datetime
from pathlib import Path


# ── 環境変数 ─────────────────────────────────────────────

def load_env(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def require_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        print(f"ERROR: 環境変数 {key} が未設定です", file=sys.stderr)
        sys.exit(1)
    return value


# ── プロジェクト構造 ──────────────────────────────────────

def find_project_root() -> Path:
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".claude").exists():
            return parent
    return cwd


def load_path_map(claude_dir: Path) -> dict:
    map_file = claude_dir / "settings.ftp.json"
    if not map_file.exists():
        print(f"ERROR: {map_file} が見つかりません", file=sys.stderr)
        sys.exit(1)
    data = json.loads(map_file.read_text())
    return {k: v for k, v in data.items() if not k.startswith("_")}


def is_safe_local_path(path_str: str) -> bool:
    p = Path(path_str)
    return not p.is_absolute() and ".." not in p.parts


def resolve_remote_path(local_path: str, path_map: dict) -> str | None:
    if not is_safe_local_path(local_path):
        return None
    matched_key = None
    for key in path_map:
        if local_path.startswith(key) and (matched_key is None or len(key) > len(matched_key)):
            matched_key = key
    if matched_key is None:
        return None
    return posixpath.normpath(path_map[matched_key] + local_path[len(matched_key):])


def parse_pending(pending_file: Path) -> list[dict]:
    """テーブル形式の .pendings.md をパースして [{op, local}] を返す。"""
    items = []
    for line in pending_file.read_text().splitlines():
        line = line.strip()
        if not line.startswith("| ") or "---" in line or line.startswith("| 操作"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) == 2:
            items.append({"op": parts[0], "local": parts[1]})
    return items


# ── FTP操作 ───────────────────────────────────────────────

def backup_remote_file(ftp: ftplib.FTP_TLS, remote_path: str, ftp_root: str, timestamp: str) -> str | None:
    """リモートファイルを {ftp_root}/.claude/backup/ 配下に階層を保ったまま移動する。"""
    p = Path(remote_path)
    backup_name = f"{p.stem}_{timestamp}_claude{p.suffix}"
    rel_path = remote_path[len(ftp_root):].lstrip("/") if remote_path.startswith(ftp_root) else remote_path.lstrip("/")
    backup_path = posixpath.normpath(
        posixpath.join(ftp_root, ".claude", "backup", posixpath.dirname(rel_path), backup_name)
    )
    ensure_remote_dirs(ftp, backup_path)
    try:
        ftp.rename(remote_path, backup_path)
        return backup_path
    except ftplib.error_perm:
        return None


def delete_remote_file(ftp: ftplib.FTP_TLS, remote_path: str, ftp_root: str, timestamp: str) -> str | None:
    """バックアップしてからリモートファイルを削除する。"""
    backup_path = backup_remote_file(ftp, remote_path, ftp_root, timestamp)
    if backup_path:
        try:
            ftp.delete(remote_path)
        except ftplib.error_perm:
            pass
    return backup_path


def ensure_remote_dirs(ftp: ftplib.FTP_TLS, remote_path: str) -> None:
    dirs = str(Path(remote_path).parent).split("/")
    current = ""
    for d in dirs:
        if not d:
            continue
        current += "/" + d
        try:
            ftp.mkd(current)
        except ftplib.error_perm:
            pass


# ── デプロイログ ──────────────────────────────────────────

def write_deploy_log(deploy_dir: Path, timestamp: str, results: list) -> Path:
    now_str = datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# デプロイ {now_str}\n\n",
        "| 操作 | ローカル | リモート | バックアップ |\n",
        "|------|----------|----------|-------------|\n",
    ]
    for r in results:
        backup = r.get("backup") or "-"
        lines.append(f"| {r['op']} | {r['local']} | {r.get('remote', '-')} | {backup} |\n")

    success = all(r.get("ok") for r in results)
    lines.append(f"\n**ステータス**: {'成功' if success else '一部エラーあり'}\n")

    log_file = deploy_dir / f"{timestamp}_ftp.md"
    log_file.write_text("".join(lines))
    return log_file


# ── メイン ────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="接続テストのみ（アップロードしない）")
    args = parser.parse_args()

    root = find_project_root()
    load_env(root / ".env")

    host = require_env("CLAUDE_FTP_HOST")
    username = require_env("CLAUDE_FTP_USERNAME")
    password = require_env("CLAUDE_FTP_PASSWORD")

    if args.test:
        print(f"接続テスト: {host}")
        with ftplib.FTP_TLS(host) as ftp:
            ftp.login(username, password)
            ftp.prot_p()
            print("接続成功")
            print(f"カレントディレクトリ: {ftp.pwd()}\n")
            print("ディレクトリ一覧:")
            ftp.retrlines("LIST")
        return

    claude_dir = root / ".claude"
    deploy_dir = claude_dir / "logs" / "deploy"
    pending_file = deploy_dir / ".pendings.md"

    if not pending_file.exists() or not pending_file.read_text().strip():
        print("デプロイ対象ファイルがありません（.pendings.md が空）")
        sys.exit(0)

    items = parse_pending(pending_file)
    if not items:
        print("デプロイ対象ファイルがありません")
        sys.exit(0)

    path_map = load_path_map(claude_dir)
    ftp_root = path_map[min(path_map.keys(), key=len)].rstrip("/")

    # リモートパス解決
    work_list = []
    for item in items:
        lf = item["local"]
        op = item["op"]
        if not is_safe_local_path(lf):
            print(f"WARNING: {lf} は不正なパスのためスキップします。")
            continue
        remote = resolve_remote_path(lf, path_map)
        if not remote:
            print(f"WARNING: {lf} は settings.ftp.json に対応するエントリがありません。スキップします。")
            continue
        work_list.append({"op": op, "local": lf, "remote": remote})

    if not work_list:
        print("処理できるファイルがありません。settings.ftp.json を確認してください。")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    results = []

    print(f"接続中: {host}")
    with ftplib.FTP_TLS(host) as ftp:
        ftp.login(username, password)
        ftp.prot_p()
        ftp.set_pasv(True)
        print("ログイン成功\n")

        for item in work_list:
            op = item["op"]
            local_path = root / item["local"]
            remote_path = item["remote"]

            if op == "Delete":
                backup_path = delete_remote_file(ftp, remote_path, ftp_root, timestamp)
                print(f"  DELETE: {remote_path}")
                if backup_path:
                    print(f"          バックアップ: {backup_path}")
                results.append({**item, "backup": backup_path, "ok": backup_path is not None})

            else:  # Edit / Create
                if not local_path.exists():
                    print(f"  SKIP (ローカルに存在しない): {item['local']}")
                    results.append({**item, "backup": None, "ok": False})
                    continue
                backup_path = backup_remote_file(ftp, remote_path, ftp_root, timestamp)
                ensure_remote_dirs(ftp, remote_path)
                with open(local_path, "rb") as f:
                    ftp.storbinary(f"STOR {remote_path}", f)
                print(f"  {op.upper()}: {item['local']} → {remote_path}")
                if backup_path:
                    print(f"       バックアップ: {backup_path}")
                results.append({**item, "backup": backup_path, "ok": True})

    log_file = write_deploy_log(deploy_dir, timestamp, results)
    print(f"\nデプロイ完了 → {log_file.relative_to(root)}")

    # pending をリセット
    pending_file.write_text("")


if __name__ == "__main__":
    main()
