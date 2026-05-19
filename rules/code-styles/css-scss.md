---
paths:
  - "**/*.css,**/*.scss"
---

# CSS / SCSS コーディングスタイル

**プロジェクトの担当者によってコンパイル対象にするファイルが異なるので、SCSS を記述する際はどのファイルに記述するべきかユーザーに必ず確認すること**

## アーキテクチャ: FLOCSS

ディレクトリ構成は FLOCSS に準拠する。下記はよく使用するテンプレートの例

```
scss/
  foundation/        # 変数・mixin・reset・base
    _variable.scss
    _mixin.scss
    _reset.scss
    _base.scss
    plugins/         # 外部ライブラリ上書き
  layout/            # レイアウト（l- 接頭辞）
  object/
    component/       # 汎用コンポーネント（c- 接頭辞）
    project/         # ページ固有（p- 接頭辞）
    utility/         # ユーティリティ（u- 接頭辞）
```

## 命名規則

クラス名は接頭辞 + BEM で構成する。

| 接頭辞 | 用途                                                |
| ------ | --------------------------------------------------- |
| `l-`   | レイアウト（`l-header`, `l-footer`, `l-content`）   |
| `c-`   | 汎用・再利用コンポーネント（`c-btn`, `c-card`）     |
| `p-`   | プロジェクト固有・単一用途（`p-news`, `p-contact`） |
| `u-`   | ユーティリティ（`u-text-center`, `u-mt-2`）         |

BEM の記述ルール:

- Element: `__`（`l-header__logo`）
- Modifier: `-`（`p-news -single`、セパレーターにスペースを入れてクラスを分ける）
- State: `is-` / `has-`（`is-act`, `has-child`）

```scss
.l-header {
  &__inner {
  }
  &__logo {
  }
  &.-page {
  } // Modifier はセレクタの中で &.- で記述
  &.is-act {
  } // State
}
```

## 変数管理

- 色・フォント・ブレークポイントはすべて `foundation/_variable.scss` で定義する
- カラーは用途別に命名する（`$main`, `$sub`, `$link`, `$bd` 等）
- テンプレートにカラーコードをハードコードしない

## メディアクエリ

- ブレークポイントは `$media_list` マップで一元管理する
- 呼び出しは `@include mq(サイズキー)` で統一する

```scss
$media_list: (
  "ss": "(max-width: 575.9px)",
  "xs": "(max-width: 767.9px)",
  "sm": "(max-width: 991.9px)",
  "md": "(max-width: 1199.9px)",
  "sm-": "(min-width: 992px)",
  "md-": "(min-width: 1200px)",
);

@mixin mq($media: sm) {
  @media #{map-get($media_list, $media)} {
    @content;
  }
}
```

## Mixin

共通エフェクトは mixin で統一する。

- トランジション: `@include transition($prop, $time, $delay, $media)`
- ホバー画像ズーム: `@include hover_img($scale)`
- メディアクエリ: `@include mq($key)`

個別に `transition:` を書かず、必ず mixin 経由にする。

## ネスト

- ネストは最大 4 階層程度に留める
- `&` で親セレクタを参照し、セレクタの繰り返しを避ける
- 疑似要素・疑似クラスも `&:before`, `&:hover` でネスト内に書く

## インポート順序

`style.scss` のインポート順序は以下を維持する。

1. `foundation/` （変数 → mixin → reset → base → plugins）
2. `layout/`
3. `object/component/`
4. `object/project/`
5. `object/utility/`
