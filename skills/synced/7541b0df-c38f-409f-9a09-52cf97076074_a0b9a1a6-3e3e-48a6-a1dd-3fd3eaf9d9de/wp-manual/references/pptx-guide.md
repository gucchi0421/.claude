# PPTX生成ガイド（WPマニュアル用）

## 雛形PPTXの解析方法

```python
# python-pptxを使ってスライド構成を読み取る
from pptx import Presentation

prs = Presentation("template.pptx")
for i, slide in enumerate(prs.slides):
    print(f"スライド {i+1}: レイアウト={slide.slide_layout.name}")
    for shape in slide.shapes:
        if shape.has_text_frame:
            print(f"  テキスト: {shape.text_frame.text[:50]}")
```

## プレースホルダーへの挿入パターン

### テキスト置換
```python
from pptx import Presentation
from pptx.util import Inches, Pt

def replace_text(slide, placeholder_text, new_text):
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if placeholder_text in run.text:
                        run.text = run.text.replace(placeholder_text, new_text)
```

### スクリーンショット挿入
```python
from pptx.util import Inches

def add_screenshot(slide, image_path, left, top, width, height):
    slide.shapes.add_picture(
        image_path,
        Inches(left), Inches(top),
        Inches(width), Inches(height)
    )
```

### 新規スライド追加（カスタム投稿タイプ用）
```python
def add_custom_post_slide(prs, layout_index, title, content):
    layout = prs.slide_layouts[layout_index]
    slide = prs.slides.add_slide(layout)
    # タイトルとコンテンツを設定
    slide.shapes.title.text = title
    # コンテンツプレースホルダーを設定
    return slide
```

## スライド構成の標準テンプレート

雛形PPTXが提供されない場合、以下の構成でデフォルトマニュアルを作成する：

1. **表紙** — サイト名・マニュアルタイトル・作成日
2. **目次** — マニュアルの構成
3. **ログイン方法** — 管理画面URLと手順（パスワードは記載しない）
4. **ダッシュボードの見方** — 管理画面の全体説明
5. **投稿の管理** — 新規作成・編集・削除の手順
6. **固定ページの管理** — 編集手順
7. **メディアの管理** — 画像アップロード手順
8. **[カスタム投稿タイプごとにスライドを追加]**
9. **外観・メニューの変更** — 必要に応じて
10. **よくある質問** — 任意

## スクリーンショットの命名規則

取得したスクリーンショットは以下の規則で保存する：
```
ss_01_dashboard.png
ss_02_posts_list.png
ss_03_post_edit.png
ss_04_custom_post_{name}.png
...
```

## セキュリティ注意事項

- PPTXファイル内にログインパスワードを**絶対に記載しない**
- URLは記載してよいが、管理画面のURLのみ（フロントエンドURLも可）
- スクリーンショットにパスワードが映り込んでいないか確認すること
- メタデータ（作成者名等）にも機密情報が入らないよう注意
