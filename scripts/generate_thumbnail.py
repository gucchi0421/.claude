"""
記事サムネイル生成スクリプト

Pollinations.ai（デフォルト）または Pillow でサムネイルを生成し、
WP-CLI 経由で WordPress にアップロード・アイキャッチ設定まで行う。

Usage:
  # Pollinations で生成してWPにアップ（推奨）
  python generate_thumbnail.py --title "タイトル" --category "Web制作" --post_id 69

  # Pillow（テキスト画像）でWPにアップ
  python generate_thumbnail.py --title "タイトル" --post_id 69 --mode pillow

  # ファイル保存のみ（WPアップなし）
  python generate_thumbnail.py --title "タイトル" --output /tmp/thumb.jpg --no-upload
"""

import argparse
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# --- Pillow は任意依存 ---
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# Pillow 用設定
WIDTH = 1200
HEIGHT = 675
FONT_PATH_MAIN = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"
FONT_PATH_FALLBACK = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"
BG_COLOR = (239, 236, 228)
ACCENT_COLOR = (165, 122, 68)
DARK_COLOR = (17, 17, 17)
WHITE = (255, 255, 255)

# Docker コンテナ名
WP_CONTAINER = "wordpress"


# ------------------------------------------------------------------ #
# Pollinations.ai
# ------------------------------------------------------------------ #

def fetch_pollinations(prompt: str, output: str, width: int = 1200, height: int = 675, seed: int = 42) -> str:
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model=flux&seed={seed}"
    print("[Pollinations] 生成中...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as f:
        f.write(data)
    print(f"[Pollinations] 保存: {output} ({len(data):,} bytes)")
    return output


def build_prompt(title: str, category: str) -> str:
    """記事タイトル・カテゴリから英語プロンプトを組み立てる"""
    category_map = {
        "Web制作": "web design office professional",
        "SEO": "search engine optimization digital marketing",
        "マーケティング": "digital marketing business strategy",
        "WordPress": "wordpress website development",
        "デザイン": "graphic design creative studio",
    }
    theme = category_map.get(category, "business professional")
    return (
        f"japan cityscape {theme}, photorealistic, wide angle, "
        "clean modern, golden hour lighting, no text, no watermark, no logo"
    )


# ------------------------------------------------------------------ #
# Pillow（フォールバック）
# ------------------------------------------------------------------ #

def get_font(size):
    for path in [FONT_PATH_MAIN, FONT_PATH_FALLBACK]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    lines, current = [], ""
    for char in text:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def generate_pillow(title: str, category: str, output: str, site_name: str = "e-webseisaku.com") -> str:
    if not HAS_PILLOW:
        sys.exit("[ERROR] Pillow が未インストールです: python3 -m pip install Pillow")
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw.rectangle([(900, 0), (WIDTH, HEIGHT)], fill=ACCENT_COLOR)
    draw.rectangle([(895, 0), (900, HEIGHT)], fill=WHITE)
    draw.rectangle([(60, 50), (840, 56)], fill=ACCENT_COLOR)
    draw.rectangle([(60, HEIGHT - 56), (840, HEIGHT - 50)], fill=ACCENT_COLOR)

    font_cat = get_font(24)
    cat_bbox = draw.textbbox((0, 0), category, font=font_cat)
    cat_w = cat_bbox[2] - cat_bbox[0]
    px, py = 20, 8
    draw.rectangle([(60, 90), (60 + cat_w + px * 2, 90 + cat_bbox[3] - cat_bbox[1] + py * 2)], fill=ACCENT_COLOR)
    draw.text((60 + px, 90 + py), category, font=font_cat, fill=WHITE)

    font_title = get_font(52)
    lines = wrap_text(title, font_title, 760, draw)
    line_height = 68
    title_y = max(160, (HEIGHT - len(lines) * line_height) // 2 - 20)
    for i, line in enumerate(lines):
        draw.text((60, title_y + i * line_height), line, font=font_title, fill=DARK_COLOR)

    font_site = get_font(22)
    site_img = Image.new("RGBA", (HEIGHT, 60), (0, 0, 0, 0))
    site_draw = ImageDraw.Draw(site_img)
    site_draw.text((20, 10), site_name, font=font_site, fill=WHITE)
    site_rotated = site_img.rotate(90, expand=True)
    img.paste(site_rotated, (940, (HEIGHT - site_rotated.height) // 2), site_rotated)

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    img.save(output, "PNG", optimize=True)
    print(f"[Pillow] 保存: {output}")
    return output


# ------------------------------------------------------------------ #
# WordPress アップロード
# ------------------------------------------------------------------ #

def upload_to_wp(local_path: str, post_id: int, title: str) -> int:
    container_path = f"/tmp/{Path(local_path).name}"

    print("[WP] Docker にコピー中...")
    subprocess.run(["docker", "cp", local_path, f"{WP_CONTAINER}:{container_path}"], check=True)

    print("[WP] メディアインポート中...")
    result = subprocess.run(
        [
            "docker", "exec", "-u", "www-data", WP_CONTAINER,
            "wp", "media", "import", container_path,
            f"--post_id={post_id}",
            f"--title={title}",
            "--featured_image",
            "--porcelain",
            "--allow-root",
        ],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[WP ERROR] {result.stderr}")
        sys.exit(1)

    attachment_id = result.stdout.strip()
    print(f"[WP] アップロード完了 attachment_id={attachment_id}, post_id={post_id}")
    return int(attachment_id)


# ------------------------------------------------------------------ #
# メイン
# ------------------------------------------------------------------ #

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True, help="記事タイトル")
    parser.add_argument("--category", default="Web制作", help="記事カテゴリ")
    parser.add_argument("--post_id", type=int, help="WP投稿ID（アップロード先）")
    parser.add_argument("--output", default="/tmp/thumbnail.jpg", help="保存先パス")
    parser.add_argument("--mode", choices=["pollinations", "pillow"], default="pollinations")
    parser.add_argument("--no-upload", action="store_true", help="WPアップをスキップ")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--site", default="e-webseisaku.com")
    args = parser.parse_args()

    if args.mode == "pollinations":
        prompt = build_prompt(args.title, args.category)
        fetch_pollinations(prompt, args.output, seed=args.seed)
    else:
        generate_pillow(args.title, args.category, args.output, args.site)

    if not args.no_upload:
        if not args.post_id:
            sys.exit("[ERROR] --post_id を指定してください（--no-upload で省略可）")
        upload_to_wp(args.output, args.post_id, args.title)


if __name__ == "__main__":
    main()

