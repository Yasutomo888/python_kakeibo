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

def list_months() -> list[str]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT SUBSTR(date,1,7) AS month
        FROM expenses
        ORDER BY month
    """)
    months = [r[0] for r in cur.fetchall()]
    conn.close()
    return months

def query_report(month: str | None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    def list_months() -> list[str]:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT SUBSTR(date, 1, 7) AS month
            FROM expenses
            ORDER BY month
        """)
        months = [row[0] for row in cur.fetchall()]
        conn.close()
        return months

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
    months = list_months() if DB_PATH.exists() else []
    options = "\n".join(f'<option value="{m}">{m}</option>' for m in months)

    return f"""
    <!doctype html>
    <html lang="ja">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>python_kakeibo</title>
        <style>
          body {{ font-family: system-ui, -apple-system, sans-serif; padding: 16px; line-height: 1.7; }}
          a, button, select {{ font-size: 16px; }}
          select, button {{ padding: 8px; }}
          /* Skip link */
          .skip-link {{
            position: absolute; left: -999px; top: 0;
            background: #000; color: #fff; padding: 8px;
          }}
          .skip-link:focus {{ left: 8px; top: 8px; z-index: 9999; }}
          /* Focus visible */
          :focus-visible {{ outline: 3px solid #005fcc; outline-offset: 2px; }}
          .help {{ color: #444; font-size: 14px; }}
          .btn {{ padding: 10px 12px; }}
        </style>
      </head>
      <body>
        <a class="skip-link" href="#main">本文へスキップ</a>

        <header>
          <h1>python_kakeibo</h1>
          <p>月を選択して集計します。空欄なら全期間を表示します。</p>
        </header>

        <main id="main">
          <form action="/report" method="get" novalidate>
            <label for="month">対象月（YYYY-MM）</label><br>
            <select id="month" name="month" aria-describedby="month-help">
              <option value="">（全期間）</option>
              {options}
            </select>
            <div id="month-help" class="help">
              DBに登録されている月から選択できます
            </div>
            <p>
              <button class="btn" type="submit">集計</button>
            </p>
          </form>

          <p><a href="/report">全期間を表示</a></p>
        </main>
      </body>
    </html>
    """

@app.get("/report")
def report():
    month = request.args.get("month", "").strip() or None

    import re
    ...
    month_raw = request.args.get("month", "").strip()
    month = month_raw or None

    if month_raw and not re.fullmatch(r"\d{4}-\d{2}", month_raw):
        return f"""
        <h1>入力エラー</h1>
        <p role="alert">対象月は YYYY-MM 形式で入力してください（例: 2026-01）。</p>
        <p><a href="/">戻る</a></p>
        """, 400

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
        <table>
          <caption>カテゴリごとの合計と割合</caption>
          <thead>
            <tr>
              <th scope="col">カテゴリ</th>
              <th scope="col">金額</th>
              <th scope="col">割合</th>
            </tr>
          </thead>
          <tbody>
            {rows_cat_html or "<tr><td colspan='3'>データなし</td></tr>"}
          </tbody>
        </table>

        <h2>日付別</h2>
        <table>
          <caption>日付ごとの合計</caption>
          <thead>
             <tr>
               <th scope="col">日付</th>
               <th scope="col">金額</th>
             </tr>
          </thead>
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