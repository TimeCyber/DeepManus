# 🦜🤖 DeepManus

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![WeChat](https://img.shields.io/badge/WeChat-DeepManus-brightgreen?logo=wechat&logoColor=white)](./assets/wechat_community.jpg)
[![Discord Follow](https://dcbadge.vercel.app/api/server/m3MszDcn?style=flat)](https://discord.gg/m3MszDcn)

[English](./README.md) | [简体中文](./README_zh.md) | [日本語](./README_ja.md)

> オープンソースから来て、オープンソースに戻る

DeepManusは、LangManusをベースに開発されたAI自動化フレームワークで、deepseekを大規模モデルとして使用し、サードパーティのフレームワークを減らすことで中国での使用を容易にしています。このプロジェクトはオープンソースコミュニティの素晴らしい成果の上に構築されています。プロジェクトの目標は、大規模言語モデルに手足を与えることです。

## デモビデオ

**タスク**: HuggingFace上のDeepSeek R1の影響指数を計算します。この指数は、フォロワー数、ダウンロード数、いいね数などの要素の加重和を考慮して設計できます。

**DeepManusの完全自動化計画とソリューション**:

1. **最新情報の収集**  
   オンライン検索を通じて「DeepSeek R1」、「HuggingFace」、および関連トピックに関する最新情報を取得します。

2. **HuggingFaceの公式ウェブサイトにアクセス**  
   Chromiumインスタンスを使用してHuggingFaceの公式ウェブサイトにアクセスし、「DeepSeek R1」を検索して、フォロワー数、いいね数、ダウンロード数、およびその他の関連指標を含む最新データを取得します。

3. **モデル影響力計算式の検索**  
   検索エンジンとウェブスクレイピング技術を使用して、モデル影響力を計算するための関連式や方法を探します。

4. **Pythonを使用して影響力指数を計算**  
   収集したデータに基づいて、Pythonプログラミングを使用してDeepSeek R1の影響力指数を計算します。

5. **包括的なレポートの作成**  
   分析結果を包括的なレポートにまとめ、ユーザーに提示します。

## 目次

- [クイックスタート](#クイックスタート)
- [プロジェクト声明](#プロジェクト声明)
- [アーキテクチャ](#アーキテクチャ)
- [機能](#機能)
- [なぜDeepManusなのか？](#なぜDeepManusなのか)
- [セットアップ](#セットアップ)
    - [前提条件](#前提条件)
    - [インストール](#インストール)
    - [設定](#設定)
- [使用方法](#使用方法)
- [Docker](#docker)
- [Web UI](#web-ui)
- [開発](#開発)
- [FAQ](#faq)
- [貢献](#貢献)
- [ライセンス](#ライセンス)
- [謝辞](#謝辞)

## クイックスタート

```bash
# リポジトリをクローン
git clone https://github.com/TimeCyber/DeepManus.git
cd DeepManus

# 依存関係をインストール
uv sync

# Playwrightをインストールして、デフォルトでChromiumを使用
uv run playwright install

# 環境を設定
cp .env.example .env
# .envファイルを編集して、APIキーを入力

# プロジェクトを実行
uv run main.py
```

## プロジェクト声明

このプロジェクトは、LangManusに基づいたオープンソースプロジェクトで、Deepseekモデルを参照するように変更し、Jinaを削除しました。Multi-AgentおよびDeepResearch分野のアイデアを探求し、交換することを目的としています。

- **目的**: このプロジェクトの主な目的は、大規模モデルの応用研究であり、大規模モデルに手足を与えることです。
- **財産声明**: 知的財産権は成都時光サイバーテクノロジー有限公司に帰属します。
- **無関係声明**: このプロジェクトは、Manus（会社、組織、その他のエンティティを指すかどうかにかかわらず）とは無関係です。
- **貢献管理**: 問題とPRは私たちの空き時間に対処され、遅延が発生する可能性があります。ご理解ください。
- **免責事項**: このプロジェクトはMITライセンスの下でオープンソース化されています。ユーザーはその使用に伴うすべてのリスクを負います。このプロジェクトの使用から生じる直接的または間接的な結果について、いかなる責任も負いません。

## アーキテクチャ

DeepManusは、スーパーバイザーが専門のエージェントを調整して複雑なタスクを達成する階層型マルチエージェントシステムを実装しています。

![DeepManus Architecture](./assets/architecture.png)

システムは、次のエージェントが協力して動作します。

1. **コーディネーター** - 初期のインタラクションを処理し、タスクをルーティングするエントリーポイント
2. **プランナー** - タスクを分析し、実行戦略を作成
3. **スーパーバイザー** - 他のエージェントの実行を監督および管理
4. **リサーチャー** - 情報を収集および分析
5. **コーダー** - コードの生成および修正を担当
6. **ブラウザー** - ウェブブラウジングおよび情報検索を実行
7. **レポーター** - ワークフロー結果のレポートおよび要約を生成

## 機能

### コア機能

- 🤖 **LLM統合**
    - [litellm](https://docs.litellm.ai/docs/providers)を通じて、ほとんどのモデルをサポート
    - Qwenなどのオープンソースモデルのサポート
    - Deepseek互換のAPIインターフェース
    - 異なるタスクの複雑さに対応するマルチティアLLMシステム

### ツールと統合

- 🔍 **検索と取得**
    - Tavily APIを介したウェブ検索
    - 標準スクリプトの使用
    - 高度なコンテンツ抽出

### 開発機能

- 🐍 **Python統合**
    - 組み込みのPython REPL
    - コード実行環境
    - uvによるパッケージ管理

### ワークフロー管理

- 📊 **可視化と制御**
    - ワークフローグラフの可視化
    - マルチエージェントのオーケストレーション
    - タスクの委任と監視

## なぜDeepManusなのか？

私たちはオープンソースの協力の力を信じています。このプロジェクトは、次のような素晴らしいプロジェクトの仕事なしには実現できませんでした。

- [Qwen](https://github.com/QwenLM/Qwen) - オープンソースのLLMを提供
- [Tavily](https://tavily.com/) - 検索機能を提供
- [Browser-use](https://pypi.org/project/browser-use/) - ブラウザ制御機能を提供
- その他多くのオープンソースの貢献者

私たちはコミュニティに還元することを約束し、コード、ドキュメント、バグレポート、機能提案など、あらゆる種類の貢献を歓迎します。

## セットアップ

> 01Coderが公開した[このビデオ](https://www.youtube.com/watch?v=XzCmPOfd0D0&lc=UgyNFuKmya8R6rVm_l94AaABAg&ab_channel=01Coder)も参照できます

### 前提条件

- [uv](https://github.com/astral-sh/uv) パッケージマネージャー

### インストール

DeepManusは、依存関係の管理を簡素化するために[uv](https://github.com/astral-sh/uv)を利用しています。
以下の手順に従って、仮想環境を設定し、必要な依存関係をインストールします。

```bash
# ステップ1: uvを使用して仮想環境を作成およびアクティブ化
uv python install 3.12
uv venv --python 3.12

# Unix/macOSシステムの場合：
source .venv/bin/activate

# Windowsシステムの場合：
.venv\Scripts\activate

# ステップ2: プロジェクトの依存関係をインストール
uv sync
```

### 設定

DeepManusは、推論、基本タスク、およびビジョン言語タスクに使用される3層のLLMシステムを使用しており、プロジェクトのルートディレクトリにあるconf.yamlファイルを使用して設定します。設定を開始するには、`conf.yaml.example`を`conf.yaml`にコピーできます：
```bash
cp conf.yaml.example conf.yaml
```

```yaml
# trueに設定するとconf.yamlの設定を読み取り、falseに設定すると元の.envの設定を使用します。デフォルトはfalseです（既存の設定と互換性があります）
USE_CONF: true

# LLM 設定
## litellmの設定パラメータに従ってください: https://docs.litellm.ai/docs/providers 。具体的なプロバイダのドキュメントをクリックして、completionパラメータの例を参照できます
REASONING_MODEL:
  model: "volcengine/ep-xxxx"
  api_key: $REASONING_API_KEY # .envファイル内の環境変数ENV_KEYを$ENV_KEYを使って参照することができます
  api_base: $REASONING_BASE_URL

BASIC_MODEL:
  model: "azure/gpt-4o-2024-08-06"
  api_base: $AZURE_API_BASE
  api_version: $AZURE_API_VERSION
  api_key: $AZURE_API_KEY

VISION_MODEL:
  model: "azure/gpt-4o-2024-08-06"
  api_base: $AZURE_API_BASE
  api_version: $AZURE_API_VERSION
  api_key: $AZURE_API_KEY
```

プロジェクトのルートディレクトリに.envファイルを作成し、以下の環境変数を設定することができます。.env.exampleファイルをテンプレートとしてコピーして始めることができます：
```bash
cp .env.example .env
```
```ini
# ツールのAPIキー
TAVILY_API_KEY=your_tavily_api_key
JINA_API_KEY=your_jina_api_key  # オプション

# ブラウザ設定
CHROME_INSTANCE_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome  # オプション、Chromeの実行可能ファイルのパス
CHROME_HEADLESS=False  # オプション、デフォルトは False
CHROME_PROXY_SERVER=http://127.0.0.1:10809  # オプション、デフォルトは None
CHROME_PROXY_USERNAME=  # オプション、デフォルトは None
CHROME_PROXY_PASSWORD=  # オプション、デフォルトは None
```


> **注意：**
>
> - システムは異なるタイプのタスクに対して異なるモデルを使用します：
>     - 推論用のLLMは複雑な意思決定と分析に用いられます
>     - 基本的なLLMは簡単なテキストタスクに用いられます
>     - 視覚言語LLMは画像理解に関連するタスクに用いられます
> - すべてのLLMの設定は独立してカスタマイズすることができます
> - Tavily検索のデフォルト設定は最大5つの結果を返すことです（[app.tavily.com](https://app.tavily.com/) でこのキーを取得できます）

### プリコミットフックの設定

DeepManusには、各コミット前にリントとフォーマットチェックを実行するプリコミットフックが含まれています。設定するには：

1. プリコミットスクリプトを実行可能にする：

```bash
chmod +x pre-commit
```

2. プリコミットフックをインストールする：

```bash
ln -s ../../pre-commit .git/hooks/pre-commit
```

プリコミットフックは自動的に次のことを行います：

- リントチェックを実行（`make lint`）
- コードフォーマットを実行（`make format`）
- 再フォーマットされたファイルをステージングエリアに追加
- リントまたはフォーマットエラーがある場合、コミットを防止

## 使用方法

### 基本的な実行

デフォルト設定でDeepManusを実行するには：

```bash
uv run main.py
```

### APIサーバー

DeepManusは、ストリーミングレスポンスをサポートするFastAPIベースのAPIサーバーを提供します：

```bash
# APIサーバーを起動
make serve

# または直接実行
uv run server.py
```

APIサーバーは次のエンドポイントを提供します：

- `POST /api/chat/stream`：ストリーミングレスポンスを備えたLangGraph呼び出し用のチャットエンドポイント
    - リクエストボディ：
  ```json
  {
    "messages": [{ "role": "user", "content": "ここにクエリを入力してください" }],
    "debug": false
  }
  ```
    - エージェントのレスポンスを含むServer-Sent Events（SSE）ストリームを返します

### 高度な設定

DeepManusは、`src/config`ディレクトリ内のさまざまな設定ファイルを通じてカスタマイズできます：

- `env.py`：LLMモデル、APIキー、ベースURLを設定
- `tools.py`：Tavily検索結果の制限などのツール固有の設定を調整
- `agents.py`：チーム構成とエージェントシステムプロンプトを変更

### エージェントプロンプトシステム

DeepManusは、`src/prompts`ディレクトリ内の洗練されたプロンプトシステムを使用して、エージェントの動作と責任を定義します：

#### コアエージェントの役割

- **スーパーバイザー（[`src/prompts/supervisor.md`](src/prompts/supervisor.md)）**：リクエストを分析し、どのエキスパートが処理するかを決定することでチームを調整し、タスクを割り当てます。タスクの完了とワークフローの遷移を決定する責任があります。

- **リサーチャー（[`src/prompts/researcher.md`](src/prompts/researcher.md)）**：ウェブ検索とデータ収集を通じて情報を収集することに特化しています。Tavily検索とウェブスクレイピング機能を使用し、数学的計算やファイル操作は避けます。

- **コーダー（[`src/prompts/coder.md`](src/prompts/coder.md)）**：PythonとBashスクリプトに焦点を当てたプロフェッショナルなソフトウェアエンジニアの役割。以下を処理します：
    - Pythonコードの実行と分析
    - シェルコマンドの実行
    - 技術的問題解決と実装

- **ファイルマネージャー（[`src/prompts/file_manager.md`](src/prompts/file_manager.md)）**：マークダウンコンテンツを適切にフォーマットして保存することに重点を置いて、すべてのファイルシステム操作を処理します。

- **ブラウザー（[`src/prompts/browser.md`](src/prompts/browser.md)）**：ウェブインタラクションの専門家で、以下を処理します：
    - ウェブサイトのナビゲーション
    - ページインタラクション（クリック、入力、スクロール）
    - ウェブページからのコンテンツ抽出

#### プロンプトシステムのアーキテクチャ

プロンプトシステムは、テンプレートエンジン（[`src/prompts/template.py`](src/prompts/template.py)）を使用して：

- 特定の役割のマークダウンテンプレートを読み込む
- 変数置換（現在の時間、チームメンバー情報など）を処理する
- 各エージェントのシステムプロンプトをフォーマットする

各エージェントのプロンプトは個別のマークダウンファイルで定義されており、基盤となるコードを変更せずに動作と責任を簡単に変更できます。

## Docker

DeepManusはDockerコンテナで実行できます。デフォルトでは、APIサーバーはポート8000で実行されます。

```bash
docker build -t DeepManus .
docker run --name DeepManus -d --env-file .env -e CHROME_HEADLESS=True -p 8000:8000 DeepManus
```

Dockerを使用してCLIを直接実行することもできます：

```bash
docker build -t DeepManus .
docker run --rm -it --env-file .env -e CHROME_HEADLESS=True DeepManus uv run python main.py
```

## Web UI

DeepManusはデフォルトのウェブインターフェースを提供しています。

詳細については、[DeepManus/DeepManus-web](https://github.com/DeepManus/DeepManus-web)プロジェクトを参照してください。

## Docker Compose（フロントエンドとバックエンドを含む）

DeepManusは、バックエンドとフロントエンドの両方を簡単に実行するためのdocker-compose設定を提供しています：

```bash
# バックエンドとフロントエンドを起動
docker-compose up -d

# バックエンドは http://localhost:8000 で利用可能
# フロントエンドは http://localhost:3000 で利用可能で、ブラウザを通じてアクセス可能
```

これにより：
1. DeepManusバックエンドコンテナのビルドと起動
2. DeepManus Web UIコンテナのビルドと起動
3. 共有ネットワークでの接続

サービスを開始する前に、必要なAPIキーを含む`.env`ファイルが準備されていることを確認してください。

## 開発

### テスト

テストスイートを実行する：

```bash
# すべてのテストを実行
make test

# 特定のテストファイルを実行
pytest tests/integration/test_workflow.py

# カバレッジテストを実行
make coverage
```

### コード品質

```bash
# リントチェックを実行
make lint

# コードをフォーマット
make format
```

## FAQ

詳細については、[FAQ.md](docs/FAQ_zh.md)を参照してください。

## 貢献

あらゆる種類の貢献を歓迎します！誤字の修正、ドキュメントの改善、新機能の追加など、どのような形でも、あなたの助けに感謝します。開始するには、[貢献ガイドライン](CONTRIBUTING.md)をご覧ください。

## ライセンス

このプロジェクトはオープンソースで、[MITライセンス](LICENSE)の下で利用可能です。

## 謝辞

DeepManusを可能にしたすべてのオープンソースプロジェクトと貢献者に感謝します。私たちは巨人の肩の上に立っています。

特に以下のプロジェクトに感謝します：
- [LangChain](https://github.com/langchain-ai/langchain)：LLMの対話とチェーン操作の基礎となる優れたフレームワークを提供
- [LangGraph](https://github.com/langchain-ai/langgraph)：複雑なマルチエージェントのオーケストレーションをサポート
- [Browser-use](https://pypi.org/project/browser-use/)：ブラウザ制御機能を提供
- [LangManus](https://github.com/LangManus/LangManus)：このプロジェクトはLangManusに基づいています

これらの優れたプロジェクトはDeepManusの基盤を形成し、オープンソース協力の力を示しています。

## スター履歴

[![Star History Chart](https://api.star-history.com/svg?repos=DeepManus/DeepManus&type=Date)](https://www.star-history.com/#DeepManus/DeepManus&Date)
