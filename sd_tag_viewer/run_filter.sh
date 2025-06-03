#!/bin/bash

# 仮想環境がなければ作成
if [ ! -d "venv" ]; then
  echo "📦 仮想環境を作成中..."
  python3 -m venv venv
fi

# 仮想環境の pip で Flask をインストール
echo "📥 セットアップ中..."
./venv/bin/pip install -r requirements.txt

# アプリ起動
echo "🚀 アプリを起動します (http://localhost:5002)"
./venv/bin/python3 filter.py
