import argparse
import sqlite3
from pathlib import Path


def print_rows(title: str, rows: list[tuple]) -> None:
    print(f"\n{title}")
    for r in rows:
        print("  " + " ".join(str(x) for x in r))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/kakeibo.db", help="DBパス")
    parser.add_argument("--month", default="", help="YYYY-MMで絞り込み（例: 2026-01）")
    parser.add_argument("--out",default="",help="出力CSVのパス（例: out/sql_report_2026-01.csv）。指定しない場合は保存しない")
    args = parser.parse_args()

    db_path = Path(args.db)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    where = ""
    params: tuple = ()
    if args.month:
        where = "WHERE date LIKE ?"
        params = (args.month + "%",)

    # 合計
    cur.execute(f"SELECT COALESCE(SUM(amount),0) FROM expenses {where}", params)
    total = cur.fetchone()[0]
    print("合計:", total)

    # カテゴリ別
    cur.execute(
        f"""
        SELECT category, SUM(amount) AS total
        FROM expenses
        {where}
        GROUP BY category
        ORDER BY total DESC
        """,
        params,
    )
    rows_cat = cur.fetchall()
    print_rows("カテゴリ別:", rows_cat)

    # 日付別
    cur.execute(
        f"""
        SELECT date, SUM(amount) AS total
        FROM expenses
        {where}
        GROUP BY date
        ORDER BY date
        """,
        params,
    )
    rows_date = cur.fetchall()
    print_rows("日付別:", rows_cat)

    # 月別（month指定がないときだけ全体を出す）
    rows_month = []

    if not args.month:
        cur.execute(
            """
            SELECT SUBSTR(date,1,7) AS month, SUM(amount) AS total
            FROM expenses
            GROUP BY month
            ORDER BY month
            """
        )
        rows_month = cur.fetchall()
        print_rows("月別:", rows_month)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        import csv
        with out_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["section", "key", "value"])
            w.writerow(["total", "total", total])

            for cat, v in rows_cat:
               w.writerow(["category", cat, v])

            for d, v in rows_date:
               w.writerow(["date", d, v])

            if rows_month:
               for m, v in rows_month:
                   w.writerow(["month", m, v])

    print(f"\n✅ SQLレポート保存: {out_path}")

    conn.close()


if __name__ == "__main__":
    main()