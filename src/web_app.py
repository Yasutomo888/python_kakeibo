from flask import Flask, request
import sqlite3
from pathlib import Path
from collections import defaultdict
from flask import url_for
from flask import Flask, request, Response, url_for
import io
import csv

app = Flask(__name__)

DB_PATH = Path("data/kakeibo.db")


def query_report(month: str | None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    where = ""
    params = ()
    if month:
        where = "WHERE date LIKE ?"
        params = (month + "%",)

    cur.execute(f"SELECT COALESCE(SUM(amount),0) FROM expenses {where}", params)
    total = cur.fetchone()[0]

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

    conn.close()
    return total, rows_cat, rows_date


@app.get("/")
def index():
    return """
    <!doctype html>
    <html lang="ja">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>python_kakeibo</title>
        <style>
          body { font-family: system-ui, -apple-system, sans-serif; padding: 16px; line-height: 1.6; }
          input, button { font-size: 16px; padding: 8px; }
          table { border-collapse: collapse; margin-top: 12px; }
          th, td { border: 1px solid #ddd; padding: 8px; }
          th { background: #f5f5f5; }
        </style>
      </head>
      <body>
        <h1>python_kakeibo</h1>
        <p>月を入力して集計します（例: 2026-01）。空欄なら全期間の合計を表示。</p>

        <form action="/report" method="get">
          <label for="month">対象月（YYYY-MM）</label><br>
          <input id="month" name="month" type="text" inputmode="numeric" placeholder="2026-01">
          <button type="submit">集計</button>
        </form>

        <p style="margin-top: 16px;">
          <a href="/report">全期間を表示</a>
        </p>
      </body>
    </html>
    """

@app.get("/report")
def report():
    month = request.args.get("month", "").strip() or None

    if not DB_PATH.exists():
        return f"""
        <h1>DBが見つかりません</h1>
        <p>{DB_PATH} が存在しません。</p>
        <pre>python src/import_sqlite.py --input data/kakeibo.csv --db data/kakeibo.db</pre>
        <p><a href="/">戻る</a></p>
        """

    total, rows_cat, rows_date = query_report(month)

    def pct(v: int) -> str:
        return f"{(v / total * 100):.1f}%" if total else "0.0%"

    title = f"レポート（月: {month}）" if month else "レポート（全期間）"

    rows_cat_html = "\n".join(
        f"<tr><td>{cat}</td><td>{v}</td><td>{pct(v)}</td></tr>"
        for cat, v in rows_cat
    )
    rows_date_html = "\n".join(
        f"<tr><td>{d}</td><td>{v}</td></tr>"
        for d, v in rows_date
    )

    download_url = url_for("download", month=month or "")

    return f"""
    <!doctype html>
    <html lang="ja">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
      </head>
      <body>
        <h1>{title}</h1>
        <p>合計: <strong>{total}</strong></p>

        <p><a href="{download_url}">CSVをダウンロード</a></p>

        <h2>カテゴリ別</h2>
        <table border="1" cellspacing="0" cellpadding="6">
          <thead><tr><th>カテゴリ</th><th>金額</th><th>割合</th></tr></thead>
          <tbody>
            {rows_cat_html or "<tr><td colspan='3'>データなし</td></tr>"}
          </tbody>
        </table>

        <h2>日付別</h2>
        <table border="1" cellspacing="0" cellpadding="6">
          <thead><tr><th>日付</th><th>金額</th></tr></thead>
          <tbody>
            {rows_date_html or "<tr><td colspan='2'>データなし</td></tr>"}
          </tbody>
        </table>

        <p style="margin-top: 16px;"><a href="/">戻る</a></p>
      </body>
    </html>
    """
@app.get("/download")
def download():
    month = request.args.get("month", "").strip() or None

    if not DB_PATH.exists():
        return "DBが見つかりません", 404

    total, rows_cat, rows_date = query_report(month)

    # メモリ上でCSVを作る
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["section", "key", "value"])
    w.writerow(["total", "total", total])

    for cat, v in rows_cat:
        w.writerow(["category", cat, v])

    for d, v in rows_date:
        w.writerow(["date", d, v])

    filename = f"report_{month}.csv" if month else "report_all.csv"
    csv_text = buf.getvalue()
    buf.close()

    return Response(
        csv_text,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)