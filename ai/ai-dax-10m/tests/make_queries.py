"""Writes the correctness queries: expected values from the rows (no time intelligence) and one query per version."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__)); DAX = os.path.join(os.path.dirname(HERE), "dax")
# name, start, end, extra filter on Sales' related columns (as CALCULATE filter args), filter for the measure query
CTX = [("A 2024", "2024-01-01", "2024-12-31", [], ["'Date'[Year] = 2024"]),
       ("B 2024 Audio", "2024-01-01", "2024-12-31", ['Product[Category] = "Audio"'], ["'Date'[Year] = 2024", 'Product[Category] = "Audio"']),
       ("C Mar 2024", "2024-03-01", "2024-03-31", [], ['\'Date\'[Year Month] = "March 2024"']),
       ("D 2024 Germany", "2024-01-01", "2024-12-31", ['Customer[Country] = "Germany"'], ["'Date'[Year] = 2024", 'Customer[Country] = "Germany"']),
       ("E 2017", "2017-01-01", "2017-12-31", [], ["'Date'[Year] = 2017"])]
COLS = ["Sales LY", "Sales YTD", "# New Customers", "Sales Growth %", "Avg Delivery Days", "# Returning Customers", "Category Share %", "Sales 30D Avg"]
d = lambda s: 'dt"%s"' % s

def expected():
    rows = []
    for name, s, e, f, _ in CTX:
        y = int(s[:4]); ly_s, ly_e = f"{y-1}{s[4:]}", f"{y-1}{e[4:]}"
        ff = "".join(", " + x for x in f)
        per = f"Sales[Order Date] >= {d(s)}, Sales[Order Date] <= {d(e)}"
        rows.append(f'''ROW ( "Context", "{name}",
  "Sales LY", CALCULATE ( [Sales Amount], REMOVEFILTERS (), Sales[Order Date] >= {d(ly_s)}, Sales[Order Date] <= {d(ly_e)}{ff} ),
  "Sales YTD", CALCULATE ( [Sales Amount], REMOVEFILTERS (), Sales[Order Date] >= {d(f"{y}-01-01")}, Sales[Order Date] <= {d(e)}{ff} ),
  "# New Customers", VAR C = CALCULATETABLE ( VALUES ( Sales[CustomerKey] ), REMOVEFILTERS (), {per}{ff} ) RETURN COUNTROWS ( FILTER ( FirstEver, [@f] >= {d(s)} && [@f] <= {d(e)} && Sales[CustomerKey] IN C ) ),
  "Sales Growth %", VAR Cur = CALCULATE ( [Sales Amount], REMOVEFILTERS (), {per}{ff} ) VAR Prev = CALCULATE ( [Sales Amount], REMOVEFILTERS (), Sales[Order Date] >= {d(ly_s)}, Sales[Order Date] <= {d(ly_e)}{ff} ) RETURN ( Cur - Prev ) / Prev,
  "Avg Delivery Days", AVERAGEX ( CALCULATETABLE ( SUMMARIZE ( Sales, Sales[Order Number], Sales[Order Date], Sales[Delivery Date] ), REMOVEFILTERS (), {per}{ff} ), DATEDIFF ( Sales[Order Date], Sales[Delivery Date], DAY ) ),
  "# Returning Customers", VAR C = CALCULATETABLE ( VALUES ( Sales[CustomerKey] ), REMOVEFILTERS (), {per}{ff} ) RETURN COUNTROWS ( FILTER ( FirstEver, [@f] < {d(s)} && Sales[CustomerKey] IN C ) ),
  "Category Share %", {"1" if not any("Category" in x for x in f) else f"CALCULATE ( [Sales Amount], REMOVEFILTERS (), {per}{ff} ) / CALCULATE ( [Sales Amount], REMOVEFILTERS (), {per}{''.join(', ' + x for x in f if 'Category' not in x)} )"},
  "Sales 30D Avg", CALCULATE ( [Sales Amount], REMOVEFILTERS (), Sales[Order Date] > {d(e)} - 30, Sales[Order Date] <= {d(e)}{ff} ) / 30 )''')
    return ("DEFINE\n VAR FirstEver = GROUPBY ( Sales, Sales[CustomerKey], \"@f\", MINX ( CURRENTGROUP (), Sales[Order Date] ) )\nEVALUATE\nUNION (\n"
            + ",\n".join(rows) + "\n)\n")

def version(path):
    text = open(path, encoding="utf-8").read()
    body = re.search(r"DEFINE(.*?)```", text + "```", re.S)[1]
    rows = []
    for name, *_, filt in CTX:
        cols = ", ".join(f'"{c}", [{c}]' for c in COLS)
        rows.append(f'CALCULATETABLE ( ROW ( "Context", "{name}", {cols} ), {", ".join(filt)} )')
    return "DEFINE" + body.rstrip() + "\nEVALUATE\nUNION (\n" + ",\n".join(rows) + "\n)\n"

if __name__ == "__main__":
    open(os.path.join(HERE, "expected.dax"), "w", encoding="utf-8").write(expected())
    for v in ("sonnet", "haiku", "reference"):
        p = os.path.join(DAX, f"draft-{v}.dax" if v != "reference" else "reference.dax")
        if os.path.exists(p): open(os.path.join(HERE, f"test-{v}.dax"), "w", encoding="utf-8").write(version(p))
    print("ok")
