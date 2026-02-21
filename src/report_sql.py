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
    print_rows("カテゴリ別:", cur.fetchall())

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
    print_rows("日付別:", cur.fetchall())

    # 月別（month指定がないときだけ全体を出す）
    if not args.month:
        cur.execute(
            """
            SELECT SUBSTR(date,1,7) AS month, SUM(amount) AS total
            FROM expenses
            GROUP BY month
            ORDER BY month
            """
        )
        print_rows("月別:", cur.fetchall())

    conn.close()


if __name__ == "__main__":
    main()