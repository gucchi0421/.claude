---
paths:
  - "**/*.js"
---

# JavaScript コーディングスタイル

## 基本方針

- ES6+ 構文を使用する（`let`/`const`、アロー関数、テンプレートリテラル等）
- `var` は使用しない

## 変数・関数

- 再代入しない変数は `const`、再代入が必要な変数のみ `let`
- 関数は function 関数を基本とする
- 関数名・変数名は camelCase

## DOM 操作

- 要素取得は `querySelector` / `querySelectorAll` を使用する（jQuery 非推奨）
- イベントハンドリングは `addEventListener` を使用する（インラインハンドラ禁止）

```js
function btn() {
  document.querySelector(".c-btn");
  btn.addEventListener("click", (e) => {
    e.preventDefault();
    // 処理
  });
}
```

## モジュール設計

- 機能単位でスコープを分離する
- クラスよりも関数型・オブジェクトリテラルを好む
- 状態の共有は最小限に抑える

## 非同期処理

- コールバックより `Promise` / `async/await` を優先する
- エラーは握りつぶさず `try/catch` で処理する

## ファイル分割

- フロント用・管理画面用・機能別で分割する
- 配布時は minify する
