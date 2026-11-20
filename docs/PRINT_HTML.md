# 印刷用HTMLの生成

既存の `scripts/libparser.py` に `--html` オプションを追加しました。

```sh
python scripts/libparser.py --html < src/SegTree.cpp > SegTree.html
```

出力はCSSを内包する単独HTMLです。ブラウザーの通常の印刷機能を使います（印刷用ボタンはありません）。

## 対象コード

- スコープ外の通常コードと `expl` / `comp` / `text` を表示します。
- `include` スコープと、テスト用のスコープは表示しません。
- `//// @shade lazy` と記載すると、`lazy` スコープの `//// ! lazy` / `//// !! lazy` を**元の位置**に網掛け表示します。表示名は指定しません。
- `@name` と `@expl` は見出し・概要に使い、`@url`・`@check`・スコープ名・メタ記法は表示しません。
- 行番号は表示するコード行に対して1から付け直し、メタ記法は行番号に数えません。
- `expl` / `comp` / `text` の直前、またはファイル末尾にある連続空行だけ削除します。

`@shade` は印刷用の指定で、従来の `-s` / `-c` / `-u` とコード抽出の意味を変更しません。存在しないスコープを指定するとエラーになります。

```sh
python -m unittest discover -s tests -p 'test_print_html.py'
```

色に依存しないよう、網掛けの左端には斜線も描画しています。

## CIでのHTML生成

GitHub Actionsの `build_html` ジョブが `verify` ジョブと並列に実行されます。
`scripts/build_site.py` は `src/` の全ライブラリを既存の `libparser.py` で解析し、
`dist/index.html` と `dist/lib/*.html` を生成します。
成果物は Actions Artifact `library-print-html` として保存されます。
通常の `verify` ジョブの成功に依存せず、HTML生成の成否も独立にCIに反映されます。

```sh
python scripts/build_site.py --output dist
```

一覧ページは `@name` と `@expl` のみを用い、カテゴリーや機能の意味を推測しません。
印刷用HTMLには `include` スコープの内容が入りません。
