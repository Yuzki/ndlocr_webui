# NDLOCR Web UI

[NDLOCR](https://github.com/ndl-lab/ndlocr_cli) を web UI化します。

## 使い方

### 0. ndlocr_cli の準備

https://github.com/ndl-lab/ndlocr_cli に従い、 「1. リポジトリのクローン」から「3. dockerのインストール」までを行ってください。


### 1. ファイルの置き換え
`Dockerfile`, `run_docker.sh` を置き換え、web UI 実行用の `app.py` をコピーします。
`/path/to/ndlocr_cli` は自身の環境に合わせて変えてください。

```
cp Dockerfile /path/to/ndlocr_cli/docker/Dockerfile
cp run_docker.sh /path/to/ndlocr_cli/docker/run_docker.sh
cp app.py /path/to/ndlocr_cli/app.py
```

### 2. dockerコンテナのビルド・起動

https://github.com/ndl-lab/ndlocr_cli に従い、「4. dockerコンテナのビルド」と「6. dockerコンテナの起動」を行います。

(注意)

ポートの指定は `Dockerfile` 内で行っています。必要に応じ、ビルドの前にポート番号を変更してください。


### 3. ウェブアプリの起動

docker上でウェブアプリを動かします。
IPアドレスやポート番号の変更する場合は、 `app.py` を書き換えてください。

```
docker exec -i -t --user root ocr_cli_runner python app.py
```

コマンドを実行するとURLが表示されるので、ブラウザでアクセスしてください。

## 機能説明

この web UI では、以下の3つの入力形式に対応しています。

- 単一画像: 画像1枚。Image file mode (`-s f`) に対応。 
- 複数画像: 画像複数枚。Single input dir mode (`-s s`) に対応。
- PDF: PDF。PDFから画像へ変換後、 Single input dir mode (`-s s`)。

いずれの入力形式も、推論後の出力ディレクトリをZIPしたものを出力します。
ただし、単一画像の場合は読み取ったテキストも表示します。

## 未対応
- ファイル名の保持
- Windows 環境
- エラー処理 (問題なくNDLOCRが動かせることを前提としているため)


## 参考
- [blue0620](https://github.com/blue0620) さんのノートブック https://github.com/blue0620/NDLOCR-GoogleColabVersion/blob/main/NDLOCR_googlecolabversion.ipynb
- [nakamura196](https://zenn.dev/nakamura196) さんのZenn記事1 https://zenn.dev/nakamura196/articles/a8227f4524570c
    - ノートブック https://colab.research.google.com/github/nakamura196/ndl_ocr/blob/main/ndl_ocr_folder.ipynb#scrollTo=eQa1CxUBl9Ap
- [nakamura196](https://zenn.dev/nakamura196) さんのZenn記事2 https://zenn.dev/nakamura196/articles/b6712981af3384
    - ノートブック https://colab.research.google.com/github/nakamura196/ndl_ocr/blob/main/ndl_ocr_v2.ipynb