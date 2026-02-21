import csv
import argparse 
from collections import defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", help="YYYY-MM で絞り込み（例: 2026-01）")
    parser.add_argument("--input",default="data/kakeibo.csv",help="入力CSVのパス（例: data/kakeibo.csv）")
    parser.add_argument("--out",default="",help="出力CSVのパス（例: out/report_2026-01.csv）。指定しない場合は保存しない")

    args = parser.parse_args()
    target_month = args.month
    csv_path = Path(args.input)

    total = 0
    by_cat = defaultdict(int)
    by_date = defaultdict(int)
    by_month = defaultdict(int)
    rows: list[dict[str, str]] = []

    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # amountが空/変な文字でも落ちないように
            try:
                amount = int(row["amount"])
            except (KeyError, ValueError, TypeError):
                continue
            date = row.get("date", "")
            if target_month and not date.startswith(target_month):
                continue

            total += amount
            by_cat[row.get("category", "unknown")] += amount
            by_date[row.get("date", "unknown")] += amount
            month = row.get("date", "")[:7] # "YYYY-MM"
            by_month[month] += amount

            # rowsにも「数値化したamount」を入れておく（後で楽）
            row["amount"] = str(amount)
            rows.append(row)

    print("合計:", total)
    if args.out:
       out_path = Path(args.out)
       out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)

        # サマリー
        w.writerow(["section", "key", "value"])
        w.writerow(["total", "total", total])

        # 月別
        for m, v in sorted(by_month.items()):
            w.writerow(["month", m, v])

        # カテゴリ別
        for cat, v in sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True):
            w.writerow(["category", cat, v])

        # 日付別
        for d, v in sorted(by_date.items()):
            w.writerow(["date", d, v])

    print(f"\n✅ レポート保存: {out_path}")

    if args.out:
       out_path = Path(args.out)
       out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)

        w.writerow(["section", "key", "value"])
        w.writerow(["total", "total", total])

        for m, v in sorted(by_month.items()):
            w.writerow(["month", m, v])

        for cat, v in sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True):
            w.writerow(["category", cat, v])

        for d, v in sorted(by_date.items()):
            w.writerow(["date", d, v])

    print(f"\n✅ レポート保存: {out_path}")

    print("\nカテゴリ別（割合）:")
    for k, v in sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True):
        pct = v / total * 100 if total else 0
        print(f"  {k}: {v}円 ({pct:.1f}%)")

    print("\n日付別:")
    for d, v in sorted(by_date.items()):
        print(f"  {d}: {v}円")

    if by_cat:
        top_cat = max(by_cat.items(), key=lambda kv: kv[1])
        print("\n一番多いカテゴリ:", top_cat[0], top_cat[1], "円")

    print("\n明細:")
    for r in rows:
        memo = r.get("memo", "")
        print(f'{r.get("date","")} {r.get("category","")} {r.get("amount","")}円 {memo}')

    # ✅ TOP3（mainの中に置く！）
    print("\n明細TOP3（支出が多い順）:")
    top_rows = sorted(rows, key=lambda r: int(r["amount"]), reverse=True)[:3]
    for r in top_rows:
        memo = r.get("memo", "")
        print(f'{r.get("date","")} {r.get("category","")} {r["amount"]}円 {memo}')
    print("\n月別:")
    for m, v in sorted(by_month.items()):
        print(f" {m}: {v}円")

if __name__ == "__main__":
    main()
