# FM Lite (Schedule + SQLite)

サッカー経営ゲームのMVP。ラウンドロビン日程を生成し、SQLiteに保存します。

## セットアップ
```bash
python -m venv .venv
. .venv/bin/activate      # Windowsは .venv\Scripts\activate
pip install -r requirements.txt
```

## 使い方
```bash
python scripts/setup_schedule.py
```

## テスト
```bash
pytest -q
```

## ディレクトリ
- app/: ライブラリコード
- scripts/: CLIスクリプト
- sql/: スキーマDDL
- data/: 初期データ
- tests/: テスト
