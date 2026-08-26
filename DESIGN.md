---
version: alpha
name: My Design System
description: サンプル・テンプレート用のデザインシステム定義

colors:
  primary: "#2563eb"
  on-primary: "#ffffff"
  primary-container: "#dbeafe"
  on-primary-container: "#1e3a8a"

  secondary: "#7c3aed"
  on-secondary: "#ffffff"
  secondary-container: "#ede9fe"
  on-secondary-container: "#4c1d95"

  tertiary: "#059669"
  on-tertiary: "#ffffff"
  tertiary-container: "#d1fae5"
  on-tertiary-container: "#064e3b"

  error: "#dc2626"
  on-error: "#ffffff"
  error-container: "#fee2e2"
  on-error-container: "#7f1d1d"

  surface: "#ffffff"
  on-surface: "#111827"
  surface-variant: "#f3f4f6"
  on-surface-variant: "#374151"

  outline: "#d1d5db"
  outline-variant: "#e5e7eb"

typography:
  display:
    fontFamily: "'Noto Sans JP', sans-serif"
    fontSize: 3.5rem
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: -0.02em
  headline:
    fontFamily: "'Noto Sans JP', sans-serif"
    fontSize: 2rem
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: -0.01em
  title:
    fontFamily: "'Noto Sans JP', sans-serif"
    fontSize: 1.25rem
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: "'Noto Sans JP', sans-serif"
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.75
  label:
    fontFamily: "'Noto Sans JP', sans-serif"
    fontSize: 0.875rem
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: 0.01em
  caption:
    fontFamily: "'Noto Sans JP', sans-serif"
    fontSize: 0.75rem
    fontWeight: 400
    lineHeight: 1.5

rounded:
  none: 0px
  sm: 4px
  md: 8px
  lg: 12px
  xl: 16px
  full: 9999px

spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  2xl: 64px

components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: 12px

  button-secondary:
    backgroundColor: "{colors.surface-variant}"
    textColor: "{colors.on-surface}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: 12px

  button-danger:
    backgroundColor: "{colors.error}"
    textColor: "{colors.on-error}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: 12px

  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: 24px

  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: 10px

  badge:
    backgroundColor: "{colors.primary-container}"
    textColor: "{colors.on-primary-container}"
    typography: "{typography.caption}"
    rounded: "{rounded.full}"
    padding: 4px
---

## Overview

シンプルで読みやすく、誠実さを感じさせるデザインシステムだ！
日本語コンテンツを中心に据え、情報の階層を明快に伝えることを最優先にしているのだ！
参照イメージは「良質な技術ブログ」——余白を大切にし、色は主張しすぎず、テキストが主役なのだ！

## Colors

プライマリカラーはブルー系（`#2563eb`）で、信頼・技術・知性を表現しているのだ！
セマンティックカラーは Material Design 3 の命名規約（`on-*` / `*-container`）に準拠しているのだ！

- **primary** — CTAボタン・リンク・アクセント
- **secondary** — タグ・バッジ・補助的な強調
- **tertiary** — 成功状態・ポジティブなフィードバック
- **error** — エラー・警告・削除アクション
- **surface / surface-variant** — カード背景・入力フィールド背景

## Typography

フォントは `Noto Sans JP` をベースにしているのだ！日本語と英数字の混在でも読みやすいのだ！
スケールは6段階で構成しているのだ！

| トークン | 用途 |
|---|---|
| `display` | ヒーロー見出し・LP キャッチコピー |
| `headline` | ページタイトル・セクション見出し（H1/H2） |
| `title` | カード見出し・サブセクション（H3） |
| `body` | 本文テキスト |
| `label` | ボタン・ラベル・ナビゲーション |
| `caption` | 補足・メタ情報・タイムスタンプ |

## Layout

8px グリッドをベースにしているのだ！`spacing` トークンはすべて 8 の倍数なのだ！
最大コンテンツ幅は `768px`（記事）/ `1200px`（ランディングページ）が目安なのだ！

## Elevation & Depth

影は使いすぎないのだ！カードには `box-shadow: 0 1px 3px rgba(0,0,0,0.1)` 程度にとどめるのだ！
浮き上がりよりも **境界線（`outline` カラー）** と **背景色の差** でレイヤーを表現するのだ！

## Shapes

角丸はコンポーネントの「やわらかさ」を調整するのだ！

- ボタン・入力フィールド → `rounded.md`（8px）
- カード・モーダル → `rounded.lg`（12px）
- アバター・アイコンバッジ → `rounded.full`（9999px）

## Components

コンポーネントは `button-*` / `card` / `input` / `badge` の4カテゴリが基本なのだ！
バリアントは命名規約（`button-primary-hover` 等）で表現するのだ！

## Do's and Don'ts

**Do**
- テキストと背景のコントラスト比は WCAG AA（4.5:1）以上を維持するのだ！
- スペーシングは `spacing` トークンのみを使うのだ（マジックナンバー禁止）！
- 色の意味はセマンティックトークン（`primary` / `error`）で伝えるのだ！

**Don't**
- `primary` と `secondary` を同じ画面で競合させないのだ！
- 本文フォントサイズを `body`（1rem）より小さくしないのだ！
- 角丸を混在させすぎないのだ（1画面に3種類まで）！
