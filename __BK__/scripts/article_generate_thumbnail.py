"""
記事サムネイル生成スクリプト

Pollinations.ai でサムネイルを生成し、(pwd)/.claude/articles/[slug].jpg に保存する。
WP へのアップロードはエージェント（wp-operator）が行う。

Usage:
  # スラッグ指定で保存（推奨）
  python generate_thumbnail.py \
    --title "縁日ゲームレンタル完全ガイド" \
    --slug ennichi-game-rental-guide \
    --scene "Japanese ennichi festival stall at dusk, wooden game booth counter, shooting gallery targets, ring toss pegs, goldfish scooping tank, colorful prize toys, glowing paper lanterns" \
    --style ghibli

  # 保存先を明示指定
  python generate_thumbnail.py --title "タイトル" --scene "..." --style ghibli \
    --output /path/to/thumb.jpg

品質基準（プロンプト作成ルール）:
  - --scene は英語50語以上で書く
  - 具体的な物体・色・光源・雰囲気を列挙する
  - no people は自動付加されるので書かなくてよい
  - フォトリアル系キーワード（photorealistic, realistic, photograph）は使わない
  - デフォルトスタイルは ghibli
"""

import argparse
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

STYLE_PRESETS = {
    "ghibli": (
        "Studio Ghibli anime style, soft watercolor background, "
        "hand-drawn illustration, warm gentle tones, painterly texture"
    ),
    "ink_watercolor": (
        "detailed ink illustration with watercolor wash, "
        "editorial illustration style, warm amber tones, clean linework"
    ),
    "flat_vector": (
        "flat vector illustration, bold outlines, pastel color palette, "
        "minimal geometric shapes, modern graphic design"
    ),
    "ukiyo_e": (
        "ukiyo-e woodblock print style, bold outlines, limited flat color palette, "
        "traditional Japanese art, decorative patterns"
    ),
}


def fetch_pollinations(prompt: str, output: str, width: int = 1200, height: int = 675, seed: int = 42) -> str:
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model=flux&enhance=true&seed={seed}"
    print(f"[Pollinations] 生成中... seed={seed}")
    print(f"[Pollinations] prompt={prompt[:120]}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as f:
        f.write(data)
    print(f"[Pollinations] 保存: {output} ({len(data):,} bytes)")
    return output


def build_prompt(title: str, scene: str = "", style: str = "ghibli") -> str:
    base = scene if scene else title
    style_str = STYLE_PRESETS.get(style, STYLE_PRESETS["ghibli"])
    return f"{base}, {style_str}, no people, no text, no watermark, no logo"


def upload_to_wp(local_path: str, post_id: int, title: str, ssh_config: dict) -> int:
    filename = Path(local_path).name
    wp_args = [
        "wp", "media", "import", f"/tmp/{filename}",
        f"--post_id={post_id}",
        f"--title={title}",
        "--featured_image",
        "--porcelain",
        "--allow-root",
    ]

    if ssh_config.get("local"):
        container = ssh_config["container"]
        remote_path = f"/tmp/{filename}"
        print("[WP] Docker にコピー中...")
        subprocess.run(["docker", "cp", local_path, f"{container}:{remote_path}"], check=True)
        print("[WP] メディアインポート中...")
        result = subprocess.run(
            ["docker", "exec", "-u", "www-data", container] + wp_args,
            capture_output=True, text=True
        )
    else:
        connection = ssh_config["connection"]
        remote_path = f"/tmp/{filename}"
        print("[WP] サーバーにコピー中...")
        subprocess.run(["scp", "-F", ssh_config.get("config", "~/.ssh/config"), local_path, f"{connection}:{remote_path}"], check=True)
        print("[WP] メディアインポート中...")
        wp_cmd = " ".join(wp_args)
        result = subprocess.run(
            ["ssh", "-F", ssh_config.get("config", "~/.ssh/config"), connection, f"cd {ssh_config['allowed_dirs'][0]} && {wp_cmd}"],
            capture_output=True, text=True
        )

    if result.returncode != 0:
        print(f"[WP ERROR] {result.stderr}")
        sys.exit(1)

    attachment_id = result.stdout.strip()
    print(f"[WP] アップロード完了 attachment_id={attachment_id}, post_id={post_id}")
    return int(attachment_id)


def resolve_output(slug: str, output: str) -> str:
    """保存先パスを解決する。--output 未指定時は (pwd)/.claude/articles/[slug].jpg"""
    if output:
        return output
    if not slug:
        return "/tmp/thumbnail.jpg"
    articles_dir = Path.cwd() / ".claude" / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    return str(articles_dir / f"{slug}.jpg")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True, help="記事タイトル")
    parser.add_argument("--slug", default="", help="記事スラッグ（出力先 .claude/articles/[slug].jpg に使用）")
    parser.add_argument("--scene", default="", help="シーン描写（英語50語以上推奨）。省略時はtitleをそのまま使う")
    parser.add_argument("--style", default="ghibli", choices=list(STYLE_PRESETS.keys()),
                        help=f"スタイルプリセット。選択肢: {', '.join(STYLE_PRESETS.keys())} (default: ghibli)")
    parser.add_argument("--output", default="", help="保存先パスを明示指定（省略時は --slug から自動解決）")
    parser.add_argument("--seed", type=int, default=42)
    # 後方互換: --prompt は --scene の別名として残す
    parser.add_argument("--prompt", default="", help="(非推奨) --scene を使うこと")
    # 後方互換: WPアップ系オプション（現在は wp-operator が担当するため無視）
    parser.add_argument("--ssh-config", dest="ssh_config", default="", help="(非推奨) wp-operator が担当")
    parser.add_argument("--container", default="", help="(非推奨) wp-operator が担当")
    parser.add_argument("--post_id", type=int, help="(非推奨) wp-operator が担当")
    parser.add_argument("--no-upload", action="store_true", help="(非推奨) デフォルトでアップしない")
    args = parser.parse_args()

    scene = args.scene or args.prompt
    prompt = build_prompt(args.title, scene, args.style)
    output = resolve_output(args.slug, args.output)
    fetch_pollinations(prompt, output, seed=args.seed)
    print(f"[完了] 保存先: {output}")


if __name__ == "__main__":
    main()
