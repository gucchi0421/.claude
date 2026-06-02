#!/usr/bin/env bash
# pixel-agents (MIT) のスプライトを取得して halfblock JSON に変換する
# 初回のみ実行

set -e

DEST="$HOME/.local/share/nvim/claude-mascot"
mkdir -p "$DEST/chars"

echo "→ pixel-agents キャラクター画像をダウンロード中..."
BASE="https://raw.githubusercontent.com/pixel-agents-hq/pixel-agents/main/webview-ui/public/assets/characters"
for i in 0 1 2 3 4 5; do
  curl -sL "$BASE/char_${i}.png" -o "$DEST/chars/char_${i}.png"
done
echo "  ダウンロード完了"

echo "→ スプライトを halfblock JSON に変換中..."
python3 << 'PYEOF'
from PIL import Image
import json, os, sys

CHAR_DIR = os.path.expanduser("~/.local/share/nvim/claude-mascot/chars")
OUT_FILE  = os.path.expanduser("~/.local/share/nvim/claude-mascot/sprites.json")

ANIMS = {
    "walk": [(0,0),(0,1),(0,2),(0,3)],
    "idle": [(0,4),(0,5)],
    "type": [(0,6),(0,5)],
}

def frame_to_lines(img, col, row, fw=16, fh=32):
    x0, y0 = col * fw, row * fh
    lines = []
    for py in range(0, fh, 2):
        segs = []
        for px in range(fw):
            tr,tg,tb,ta = img.getpixel((x0+px, y0+py))
            br,bg_,bb,ba = img.getpixel((x0+px, y0+py+1)) if (y0+py+1) < img.height else (0,0,0,0)
            if ta < 30 and ba < 30:
                segs.append({"t":"sp"})
            elif ta < 30:
                segs.append({"t":"lo","c":[br,bg_,bb]})
            elif ba < 30:
                segs.append({"t":"up","c":[tr,tg,tb]})
            else:
                segs.append({"t":"hl","fg":[tr,tg,tb],"bg":[br,bg_,bb]})
        lines.append(segs)
    return lines

result = {}
for cid in range(6):
    path = f"{CHAR_DIR}/char_{cid}.png"
    img = Image.open(path).convert("RGBA")
    char_anims = {}
    for anim_name, frames in ANIMS.items():
        char_anims[anim_name] = [frame_to_lines(img, col, row) for row,col in frames]
    result[str(cid)] = char_anims

with open(OUT_FILE, "w") as f:
    json.dump(result, f, separators=(',',':'))
print(f"sprites.json: {os.path.getsize(OUT_FILE)//1024}KB")
PYEOF

echo "→ 完了！ ~/.local/share/nvim/claude-mascot/sprites.json"
