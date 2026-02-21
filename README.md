# python_kakeibo（家計簿CSV集計ツール）

家計簿CSV（`date,category,amount,memo`）を読み込み、**合計・カテゴリ別・日付別・月別**の集計を表示し、必要に応じて**レポートCSVを出力**するツールです。  
業務でよくある「CSVデータの集計・レポート化」を想定して、**引数で入力ファイルや対象月を切り替え**できるようにしています。

## 機能
- 合計 / カテゴリ別（割合） / 日付別 / 月別（YYYY-MM）
- 明細一覧 / 明細TOP3（支出が多い順）
- 引数で切り替え
  - `--input`：入力CSVパス
  - `--month`：対象月（YYYY-MM）で絞り込み
  - `--out`：集計結果をCSVで出力

## 使い方

### 仮想環境を有効化
```bash
cd ~/python_kakeibo
source .venv/bin/activate
表示のみ
python src/app.py --input data/kakeibo.csv --month 2026-01
レポートCSV出力
python src/app.py --input data/kakeibo.csv --month 2026-01 --out out/report_2026-01.csv
入力CSV形式

ヘッダー行を含むCSVを想定しています。

date,category,amount,memo
2026-01-02,food,1200,昼ごはん
2026-01-02,transport,420,電車
2026-01-02,other,300,日用品

date：YYYY-MM-DD

category：カテゴリ名（例：food / transport / other）

amount：金額（数値のみ）

memo：メモ（任意）
※メモにカンマ,を含める場合はCSVとしてエスケープが必要です

今後の改善

SQLiteへ取り込み、SQLで集計

月別×カテゴリ（ピボット風）出力

入力バリデーション強化