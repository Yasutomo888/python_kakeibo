# python_kakeibo（家計簿CSV集計ツール）

家計簿CSV（`date,category,amount,memo`）を読み込み、**合計・カテゴリ別・日付別・月別**の集計を表示し、必要に応じて**レポートCSVを出力**するツールです。  
業務でよくある「CSVデータの集計・レポート化」を想定して、**入力ファイルや対象月を引数で切り替え**できるようにしています。

さらに、CSVをSQLiteへ取り込み、**SQLで集計**する機能と、Flaskによる**Web版UI**も実装しています。

---

## 機能

### CLI版
- 合計 / カテゴリ別（割合） / 日付別 / 月別（YYYY-MM）
- 明細一覧 / 明細TOP3（支出が多い順）
- 引数で切り替え
  - `--input`：入力CSVパス
  - `--month`：対象月（YYYY-MM）で絞り込み
  - `--out`：集計結果をCSVで出力

### SQLite版
- CSV → SQLite取り込み
- SQLでカテゴリ別 / 日付別 / 月別集計
- SQL集計結果をCSVで出力

### Web版（Flask）
- 月をプルダウンから選択して集計
- ブラウザでカテゴリ別 / 日付別を表示
- 集計結果をCSVダウンロード
- アクセシビリティ対応

---

## ディレクトリ構成

```text
python_kakeibo/
├─ data/
│  └─ kakeibo_sample.csv
├─ src/
│  ├─ app.py
│  ├─ import_sqlite.py
│  ├─ report_sql.py
│  └─ web_app.py
├─ .gitignore
└─ README.md