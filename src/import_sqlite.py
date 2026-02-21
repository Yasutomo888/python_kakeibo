import argparse
import csv
import sqlite3
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/kakeibo.csv", help="入力CSVパス")
    parser.add_argument("--db", default="data/kakeibo.db", help="出力DBパス")
    args = parser.parse_args()

    csv_path = Path(args.input)
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # テーブル作成
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount INTEGER NOT NULL,
            memo TEXT
        )
        """
    )

    # 既存データをクリア（毎回CSVを正として入れ直す）
    cur.execute("DELETE FROM expenses")

    inserted = 0
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = (row.get("date") or "").strip()
            category = (row.get("category") or "").strip()
            memo = (row.get("memo") or "").strip()
            amount_raw = (row.get("amount") or "").strip()

            if not date or not category or not amount_raw:
                continue

            try:
                amount = int(amount_raw)
            except ValueError:
                continue

            cur.execute(
                "INSERT INTO expenses(date, category, amount, memo) VALUES (?, ?, ?, ?)",
                (date, category, amount, memo),
            )
            inserted += 1

    conn.commit()

    # インデックス（検索/集計を速くする）
    cur.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category)")
    conn.commit()

    conn.close()
    print(f"✅ imported: {inserted} rows -> {db_path}")


if __name__ == "__main__":
    main()