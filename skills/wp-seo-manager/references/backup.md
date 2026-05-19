# バックアップ手順

実行フェーズ前に必ず行う。バックアップ完了を確認してから execute.md へ進む。

## 1. WPvivid が使える場合

管理画面 URL: `/wp/wp-admin/admin.php?page=WPvivid`

1. ページを開く
2. 「Backup」タブを選択
3. 「Backup Now」ボタンをクリック
4. バックアップ完了メッセージ（または一覧に新しいエントリ）を確認
5. 完了したらユーザーに報告して execute.md へ進む

## 2. WPvivid が未インストールの場合（All-in-One WP Migration）

管理画面 URL: `/wp/wp-admin/admin.php?page=site-migration-export`

1. ページを開く
2. 「EXPORT TO」→「File」を選択
3. エクスポートファイルの生成完了を待つ
4. ダウンロードリンクが表示されたら完了確認
5. 完了したらユーザーに報告して execute.md へ進む

## 注意

- どちらのプラグインも未インストールの場合はユーザーに確認を取る
- バックアップ未完了のまま実行フェーズに進んではならない
