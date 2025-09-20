# Line Guardrail

このプロジェクトはAWS Bedrock Agentsを使用したガードレールシステムです。

## 🚀 GitHub Codespaces での開発

### 開始方法

1. **Codespaces の起動**
   ```
   GitHub リポジトリページで "Code" > "Codespaces" > "Create codespace on main" をクリック
   ```

2. **自動セットアップ**
   - Python 3.13 環境
   - uv パッケージマネージャー
   - AWS CLI
   - SAM CLI
   - 必要な依存関係

3. **AWS認証情報の設定**
   ```bash
   # .env ファイルを編集
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   ```

### 開発コマンド

```bash
# 依存関係のインストール
uv sync

# アプリケーションの実行
uv run python main.py
```

## 📦 依存関係

- Python 3.13+
- strands-agents
- boto3 (AWS SDK)
- aws-lambda-powertools

## 🔧 ローカル開発

### uvのインストール

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

詳細: https://docs.astral.sh/uv/getting-started/installation/

### セットアップ

```bash
# 依存関係のインストール
uv sync

# 環境変数の設定
cp .env.template .env
# .env ファイルを編集
```