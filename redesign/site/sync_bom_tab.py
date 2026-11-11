"""Sync the BOM tab rows in app.html with redesign/team/I1/BOM.csv (vendor link, vendor name, price status).
Run after build_bom.py, then run make_index.py:  python -I redesign/site/sync_bom_tab.py"""
import csv, html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, "app.html")
CSV = os.path.join(HERE, "..", "team", "I1", "BOM.csv")
BADGE = {"CHK": "CHECKED", "CARRY": "PROPOSED", "EST": "UNVERIFIED"}

rows = {r["line"]: r for r in csv.DictReader(open(CSV, encoding="utf-8")) if r["line"] != "TOTAL"}
s = open(APP, encoding="utf-8").read()
a, b = s.index('id="bom-table"'), s.index("</table>", s.index('id="bom-table"'))
table = s[a:b]
n = 0


def fix(m):
    global n
    tr = m.group(0)
    lid = re.search(r'<td class="id">([^<]+)</td>', tr)
    r = rows.get(lid.group(1)) if lid else None
    if not r:
        return tr
    vendor = html.escape(r["vendor"])
    link = (f'<a class="ds-link" href="{html.escape(r["url"], quote=True)}" target="_blank" rel="noopener">{vendor}</a>'
            if r["url"] else vendor)
    tr2 = re.sub(r'(<td class="fam">[^<]*</td><td>)(.*?)(</td><td class="num">)', lambda k: k.group(1) + link + k.group(3), tr, count=1)
    st = r["price_status"]
    tr2 = re.sub(r'<span class="ds-badge" data-status="[A-Z]+">[A-Z]+</span>',
                 f'<span class="ds-badge" data-status="{BADGE.get(st, "UNVERIFIED")}">{html.escape(st)}</span>', tr2, count=1)
    n += tr2 != tr
    return tr2


table = re.sub(r"<tr data-group=.*?</tr>", fix, table, flags=re.S)
open(APP, "w", encoding="utf-8").write(s[:a] + table + s[b:])
print("rows updated:", n, "of", len(rows))
