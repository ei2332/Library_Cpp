
## C++の整形

以下の定義に基づいてclang-formatで整形を行う

```.clang-format
BasedOnStyle: Google
IndentWidth: 4
UseTab: Never
AlignAfterOpenBracket: Align
BreakBeforeBraces: Attach
MaxEmptyLinesToKeep: 1
AllowShortBlocksOnASingleLine: Always
AllowShortIfStatementsOnASingleLine: AllIfsAndElse
AllowShortLoopsOnASingleLine: true
ColumnLimit: 200
SortIncludes: true
```

## ライブラリのメタ表記

ライブラリのソースコードでは、`//// <命令> <引数...>` 形式のコメントを使う。
`scripts/libparser.py` が解釈し、必要なスコープだけを抽出する。一般の C++ コメント `//` と区別する。

### 説明・メモ

| 命令 | 用途 | 必要な引数 |
| --- | --- | --- |
| `//// text ...` | 汎用メモ・数式・注意事項 | なし（省略可能） |
| `//// expl ...` | 関数・要素の説明文 | 1つ以上 |
| `//// comp ...` | 計算量 | 1つ以上 |
| `//// @expl ...` | ライブラリ全体の説明文 | 1つ以上 |

`@expl` は1ファイルにつき1回だけ指定でき、メタデータとして保持される。`text`・`expl`・`comp` の行は、選択したスコープ内であればそのまま抽出結果に残る。通常のC++コメントに置き換えられるわけではない。

**`//// @text` は未定義で使用できない。** `@` の有無は命令ごとに決まるため、他の命令にも無条件には付けられない。

### 識別子・参照・検証

| 命令 | 用途 |
| --- | --- |
| `//// @name <名前>` | ライブラリ名。1ファイルにつき1回 |
| `//// @url <URL>` | 公開元のURL。1ファイルにつき1回 |
| `//// @license <文字列>` | ライセンス情報。1ファイルにつき1回 |
| `//// @check <問題URL> [スコープ...]` | CIが実行する検証問題と、抽出時に有効にするスコープ |
| `//// @checked <問題URL> [スコープ...]` | 検証済み問題のメタ情報。現在の `verify.py` はこれをテスト対象にしない |

`@check` は複数回指定可能。`scripts/verify.py` は各 `@check` について、指定スコープで抽出したプログラムをコンパイルしてオンラインジャッジのテストケースで検証する。

### スコープ

| 命令 | 動作 |
| --- | --- |
| `//// ! <名前>` | 名前付きスコープを開始する |
| `//// end` | スコープを終了する |
| `//// !! <名前>` | **次の1行だけ**を名前付きスコープに所属させる |

スコープ外の行は常に抽出される。スコープ内の行は、対応する名前を `-s=<名前>` で指定したときだけ抽出される。複数スコープは `-s` を繰り返して指定できる。スコープの入れ子、未終了のスコープ、未定義スコープの指定はエラーになる。

例：

```cpp
//// @name SegTree
struct SegTree {
    //// expl 点更新と区間集約に対応する
    //// ! lazy
    //// expl 遅延評価時に区間更新を追加する
    void apply();
    //// end
    //// !! lazy
    void push();
};
```

```sh
python scripts/libparser.py < src/SegTree.cpp            # 通常版
python scripts/libparser.py -s=lazy < src/SegTree.cpp    # lazyスコープを含める
python scripts/libparser.py -c < src/SegTree.cpp         # @checkの数
python scripts/libparser.py -c1 < src/SegTree.cpp        # 最初の@check用のコード
python scripts/libparser.py -u < src/SegTree.cpp         # @urlを取得
```

各命令の厳密な引数チェックと抽出動作の正本は `scripts/libparser.py` とする。
