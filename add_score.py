#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import csv

def to_float(x):
    try:
        return float(x)
    except:
        return float('nan')

def ratio(val, avg, mn):
    den = (avg - mn)
    if den == 0 or den != den:  # den==0 or NaN
        return 0.0
    r = (avg - val) / den
    return max(r, -1.0)  # 下限 -1，不設上限

def main():
    if len(sys.argv) != 3:
        print("Usage: python add_score.py <in.csv> <out.csv>")
        sys.exit(1)

    in_csv, out_csv = sys.argv[1], sys.argv[2]

    # ---- 讀入所有列 ----
    rows = []
    with open(in_csv, 'r') as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        for row in reader:
            rows.append(row)

    if not rows:
        # 空檔案，仍然寫出 header+score
        with open(out_csv, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=header + ['score'])
            writer.writeheader()
        return

    # ---- 收集三個欄位的數值 ----
    cps   = [to_float(r['clock_period']) for r in rows]
    areas = [to_float(r['area_um2'])     for r in rows]
    wls   = [to_float(r['wirelength_um']) for r in rows]

    # 簡單平均/最小（忽略 NaN）
    def finite(vals):
        return [v for v in vals if v == v]  # v==v 代表不是 NaN

    def avg_of(vals):
        vs = finite(vals)
        return sum(vs) / float(len(vs)) if vs else float('nan')

    def min_of(vals):
        vs = finite(vals)
        return min(vs) if vs else float('nan')

    cp_avg, cp_min = avg_of(cps),   min_of(cps)
    ar_avg, ar_min = avg_of(areas), min_of(areas)
    wl_avg, wl_min = avg_of(wls),   min_of(wls)

    # ---- 計算 score 並寫出 ----
    out_header = list(header)
    if 'score' not in out_header:
        out_header.append('score')

    with open(out_csv, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=out_header)
        writer.writeheader()

        for r in rows:
            cp = to_float(r['clock_period'])
            ar = to_float(r['area_um2'])
            wl = to_float(r['wirelength_um'])

            r_cp = ratio(cp, cp_avg, cp_min)
            r_ar = ratio(ar, ar_avg, ar_min)
            r_wl = ratio(wl, wl_avg, wl_min)

            score = 15.0 * (r_cp + r_ar + r_wl) / 3.0

            r_out = dict(r)
            # 想保留完整小數可用 str(score)；這裡四捨五入到 3 位
            r_out['score'] = "{:.3f}".format(score)
            writer.writerow(r_out)

if __name__ == '__main__':
    main()
