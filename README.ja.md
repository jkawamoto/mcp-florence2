[English](README.md) | 日本語

# Florence-2 MCP Server

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Python Application](https://github.com/jkawamoto/mcp-florence2/actions/workflows/python-app.yaml/badge.svg)](https://github.com/jkawamoto/mcp-florence2/actions/workflows/python-app.yaml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![GitHub License](https://img.shields.io/github/license/jkawamoto/mcp-florence2)](https://github.com/jkawamoto/mcp-florence2/blob/main/LICENSE)

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/jkawamoto-mcp-florence2-badge.png)](https://mseep.ai/app/jkawamoto-mcp-florence2)

**Florence-2 MCP Server** は、[Model Context Protocol（MCP）](https://modelcontextprotocol.io/)を通じて、AIアシスタントからローカルの画像認識と光学文字認識（OCR）を利用できるサーバーです。Microsoftの基盤モデル [Florence-2](https://huggingface.co/microsoft/Florence-2-large) を使い、ローカル画像、Web上の画像、複数ページのPDF文書をLLMで確認し、画像の説明や文字の抽出を行えます。処理はすべて自身のマシン上でオフラインで実行されます。

---

## ✨ 主な機能

- 🔒 **ローカルでの処理とプライバシー**: 画像と文書の処理はすべてローカルマシンで実行されます。外部の画像認識APIへの料金支払いやデータ共有、トークン数の制限はありません。
- 📄 **複数ページのPDFと画像に対応**: 一般的な画像形式（JPEG、PNG、WebPなど）に加え、複数ページのPDF文書をページごとに処理できます。
- ⚡ **ハードウェアアクセラレーション**: **Apple Silicon（MPS）**、**NVIDIA GPU（CUDA）**、**CPU**を自動的に検出して利用します。
- 🧹 **VRAMの節約**: デフォルトでは、必要に応じてサブプロセスで推論を実行し、完了後すぐにVRAMを解放します。低遅延で連続して利用する場合は、`--cache-model` フラグを指定できます。
- 🎯 **多様な画像認識タスク**: 高精度なOCR、詳細な画像の説明、Florence-2のプロンプトトークンを使った任意の視覚的な問い合わせ（物体検出や領域の説明など）を実行できます。
- 📦 **ワンクリックでインストール**: Claude Desktop用の `.mcpb` バンドル、LM Studio用のワンクリックディープリンク、Goose用の拡張機能に対応しています。

---

## 🚀 インストール

使用するMCPクライアントに応じて、以下の手順を選んでください。

### Claude Desktop

#### 方法1: 拡張機能バンドル（推奨）

1. [Releases](https://github.com/jkawamoto/mcp-florence2/releases) ページから、最新の `mcp-florence2.mcpb` バンドルをダウンロードします。
2. ダウンロードした `.mcpb` ファイルをダブルクリックするか、Claude Desktopの設定画面にドラッグ＆ドロップします。

#### 方法2: 手動設定

`claude_desktop_config.json` に以下の設定を追加します。

```json
{
  "mcpServers": {
    "florence-2": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/jkawamoto/mcp-florence2",
        "mcp-florence2"
      ]
    }
  }
}
```

> [!NOTE]
> 設定ファイルの場所:
> - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
> - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

詳しくは [Connect to local MCP servers](https://modelcontextprotocol.io/docs/develop/connect-local-servers) を参照してください。

---

### Goose

#### 方法1: ワンクリックURL

以下のリンクをクリックすると、Gooseの拡張機能インストーラーが起動します。

```text
goose://extension?cmd=uvx&arg=--from&arg=git%2Bhttps%3A%2F%2Fgithub.com%2Fjkawamoto%2Fmcp-florence2&arg=mcp-florence2&id=florence2&name=Florence-2&description=An%20MCP%20server%20for%20processing%20images%20using%20Florence-2
```

#### 方法2: 手動設定

`~/.config/goose/config.yaml` に以下の設定を追加します。

```yaml
extensions:
  florence2:
    name: Florence-2
    cmd: uvx
    args: [ --from, git+https://github.com/jkawamoto/mcp-florence2, mcp-florence2 ]
    enabled: true
    type: stdio
```

詳しくは [Using Extensions | goose](https://block.github.io/goose/docs/getting-started/using-extensions#mcp-servers) を参照してください。

---

### LM Studio

以下のボタンをクリックすると、LM Studioに直接インストールできます。

[![Add MCP Server florence-2 to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](https://lmstudio.ai/install-mcp?name=florence-2&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb20iLCJnaXQraHR0cHM6Ly9naXRodWIuY29tL2prYXdhbW90by9tY3AtZmxvcmVuY2UyIiwibWNwLWZsb3JlbmNlMiJdfQ%3D%3D)

---

### Claude Code、Cursor、Cline、その他のMCPクライアント

`stdio` を使うMCPサーバーに対応したクライアントであれば、`uvx` を使って接続できます。

```bash
uvx --from git+https://github.com/jkawamoto/mcp-florence2 mcp-florence2
```

---

## 🛠️ ツール

サーバーは、AIアシスタントに以下の画像認識機能を提供します。自然言語で依頼して利用できます。

### 1. `ocr`

画像や複数ページのPDF文書から、見えている文字をすべて抽出します。

- **依頼例:** 「`/path/to/invoice.pdf` からすべての文字を抽出してください。」
- **複数ページへの対応:** PDF文書のすべてのページを自動的に処理します。

<details>
<summary><b>ツールのスキーマとパラメーター</b></summary>

| パラメーター | 型 | 必須 | 説明 |
| :--- | :--- | :---: | :--- |
| `src` | `string` | **はい** | 画像またはPDFファイルのローカルファイルパス、またはHTTP/HTTPS URL。 |

</details>

---

### 2. `caption`

画像に写っている内容を詳しく説明するキャプションを生成します。

- **依頼例:** 「`https://example.com/photo.jpg` に何が写っているか説明してください。」
- 物体、位置関係、色、背景の景色について詳細な説明を返します。

<details>
<summary><b>ツールのスキーマとパラメーター</b></summary>

| パラメーター | 型 | 必須 | 説明 |
| :--- | :--- | :---: | :--- |
| `src` | `string` | **はい** | 画像またはPDFファイルのローカルファイルパス、またはHTTP/HTTPS URL。 |

</details>

---

### 3. `process`

入力された画像またはPDFに対して任意のFlorence-2タスクプロンプトを直接実行し、物体検出や領域の説明など、より高度な画像認識処理を行います。

- **依頼例:** 「この画像のすべての物体を検出し、バウンディングボックスを返してください。」

<details>
<summary><b>ツールのスキーマと対応するタスクプロンプト</b></summary>

#### パラメーター

| パラメーター | 型 | 必須 | 説明 |
| :--- | :--- | :---: | :--- |
| `src` | `string` | **はい** | 画像またはPDFファイルのローカルファイルパス、またはHTTP/HTTPS URL。 |
| `prompt` | `string` | **はい** | 実行する操作を指定するタスクプロンプト。 |

#### 対応するFlorence-2タスクプロンプト

| タスクプロンプト | 説明 |
| :--- | :--- |
| `<CAPTION>` | 画像を簡潔に一文で要約します。 |
| `<DETAILED_CAPTION>` | 画像の内容を中程度の長さで説明します。 |
| `<MORE_DETAILED_CAPTION>` | 画像の内容を非常に詳しく網羅的に説明します。 |
| `<OCR>` | 画像からテキストを抽出します。 |
| `<OCR_WITH_REGION>` | テキストとともにバウンディングボックスの座標を抽出します。 |
| `<OD>` | 物体とそのバウンディングボックスを検出します。 |
| `<DENSE_REGION_CAPTION>` | 複数の異なる領域について説明を生成します。 |
| `<REGION_PROPOSAL>` | 画像内の目立つ領域に対するバウンディングボックスの候補を検出します。 |

</details>

---

## ⚙️ 設定とCLIオプション

コマンドライン引数を使ってサーバーを設定できます。

```bash
mcp-florence2 [OPTIONS]
```

| オプション | 型 | デフォルト | 説明 |
| :--- | :--- | :--- | :--- |
| `--model` | `string` | `florence-community/Florence-2-large` | 読み込むHugging Faceモデルの識別子。 |
| `--cache-model` | `flag` | `false` | 繰り返し呼び出す際の速度を上げるため、モデルをVRAMに保持します。デフォルトではサブプロセスでモデルを実行し、待機中はメモリを解放します。 |
| `--version` | `flag` | - | バージョン情報を表示します。 |
| `--help` | `flag` | - | ヘルプを表示して終了します。 |

### より小さく高速なモデルの使用

GPUメモリが限られている場合や、より高速に実行したい場合は、`Florence-2-base` に切り替えます。

```json
{
  "mcpServers": {
    "florence-2": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/jkawamoto/mcp-florence2",
        "mcp-florence2",
        "--model",
        "florence-community/Florence-2-base"
      ]
    }
  }
}
```

---

## 🛡️ セキュリティ上の注意

`http://` または `https://` で始まるURLを処理するとき、サーバープロセスから直接HTTPリクエストが送信されます。信頼できないユーザーやプロンプトがURLを指定できる環境では、内部ネットワークのサービスやクラウドのメタデータエンドポイントを狙った**サーバーサイドリクエストフォージェリ（SSRF）**の対象となる可能性があります。

> [!WARNING]
> マルチテナント環境や信頼できない環境では、送信HTTP(S)通信をSSRF対策済みのフォワードプロキシ経由にしてください。例えば、[Smokescreen](https://github.com/stripe/smokescreen) や、プライベート・内部IPアドレス範囲をブロックするよう設定したSquidを利用できます。

Pythonの `requests` ライブラリは標準の環境変数を自動的に参照するため、クライアントの設定でプロキシを指定できます。

- `HTTP_PROXY` / `http_proxy`: HTTPリクエスト用のプロキシURL。
- `HTTPS_PROXY` / `https_proxy`: HTTPSリクエスト用のプロキシURL。
- `NO_PROXY` / `no_proxy`: プロキシを経由しないホストのカンマ区切りリスト。

<details>
<summary><b>プロキシの設定例</b></summary>

#### Claude Desktop

`claude_desktop_config.json` に `env` ブロックを追加します。

```json
{
  "mcpServers": {
    "florence-2": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/jkawamoto/mcp-florence2",
        "mcp-florence2"
      ],
      "env": {
        "HTTP_PROXY": "http://proxy.example.com:8080",
        "HTTPS_PROXY": "http://proxy.example.com:8080"
      }
    }
  }
}
```

#### Goose

`~/.config/goose/config.yaml` に `env` ブロックを追加します。

```yaml
extensions:
  florence2:
    name: Florence-2
    cmd: uvx
    args: [ --from, git+https://github.com/jkawamoto/mcp-florence2, mcp-florence2 ]
    env:
      HTTP_PROXY: "http://proxy.example.com:8080"
      HTTPS_PROXY: "http://proxy.example.com:8080"
    enabled: true
    type: stdio
```

</details>

---

## 💻 開発

### セットアップとテストの実行

このプロジェクトでは、高速で信頼性の高い依存関係の管理に [uv](https://github.com/astral-sh/uv) を使用しています。

```bash
# リポジトリをクローン
git clone https://github.com/jkawamoto/mcp-florence2.git
cd mcp-florence2

# 依存関係をインストールしてテストを実行
uv run pytest

# pre-commitのチェックを実行
uv run pre-commit run --all-files
```

---

## 📄 ライセンス

このアプリケーションは [MITライセンス](LICENSE) の下で公開されています。
