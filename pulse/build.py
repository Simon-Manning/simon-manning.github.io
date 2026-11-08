#!/usr/bin/env python3
"""Build pulse/index.html from saved X search results and official NZ series."""
import json, html, datetime, zoneinfo, pathlib

D = pathlib.Path(__file__).parent
NZ = D.parent / "nz" / "data"

def load(f):
    t = open(D / "data" / f).read()
    d = json.loads(t[t.find("{") : t.rfind("}") + 1])
    u = {x["id"]: x["username"] for x in d.get("includes", {}).get("users", [])}
    return {p["id"]: dict(p, user=u[p["author_id"]]) for p in d["data"]}

def load_nz(name):
    return json.loads((NZ / name).read_text())

POSTS = {**load("ai.txt"), **load("macro.txt"), **load("pettis.txt")}

AI_SUM = (
    "A cybersecurity week at the frontier. OpenAI launched GPT-6 Cyber and said an autonomous "
    "pipeline patched 948 Linux-kernel privilege-escalation bugs in a single run; it also shipped "
    "ChatGPT Images 2.6 and LifeVal, a benchmark of everyday assistant tasks. Anthropic opened "
    "applications for its AI-safety residency, described how Claude “dreams” to organise memory, "
    "and released FlashProve so developers can cryptographically check that an answer came from a "
    "given model. Elon Musk said Grok Bot fixes for token efficiency and smarter behaviour are underway."
)
MAC_SUM = (
    "US tech had its sharpest one-day drop since 2020: on 5 November the Nasdaq 100 fell about 5–6% "
    "and the S&P 500 erased about $3 trillion, as investors priced tighter AI regulation after the "
    "Democratic midterm sweep. The real economy looked firmer. October payrolls rose 165,000 and "
    "unemployment fell to 4.1%; US productivity rose at a 3.5% annualised pace in the September "
    "quarter; and core capital-goods shipments jumped 11.6% year on year to a record $86 billion. "
    "Inflation is still eating real wages — prices are up 31.3% since April 2020, versus 25.9% for "
    "hourly earnings — and Cleveland Fed president Beth Hammack again called for gradual rate hikes. "
    "December hike odds fell after the crash, then the jobs report pushed them back up."
)
PETTIS_SUM = (
    "China’s planning chief, Zheng Shanjie, this week described the problem as “strong supply and "
    "weak demand” — official language for Pettis’s household-underconsumption diagnosis. The "
    "People’s Bank of China will raise the foreign-exchange reserve requirement by two percentage "
    "points, to 6%, from 15 November, a move reported to pull about $24 billion of dollars out of "
    "the market and slow the yuan’s rise. In Pettis’s terms that is a choice to protect producers: "
    "an appreciating currency would cheapen imports (a hidden subsidy to households) and tax "
    "exporters. China’s 10-year government bond yield hit a record low of 1.565%, consistent with "
    "excess savings seeking safety rather than households absorbing what the country produces. "
    "Pascal Lamy, a long-time free-trader, told Caixin that China’s industrial subsidies, weak "
    "domestic consumption and supply-chain price power have distorted open trade — and Pettis "
    "called it a good sign that even free-trade advocates now distinguish comparative from "
    "competitive advantage. On his Substack he argued that hopes of a technological breakthrough "
    "are more an excuse to postpone rebalancing than a reason it can wait, and he repeated that "
    "the household share of GDP can rise only if the business or government share falls. In the "
    "United States, the absorber of last resort, real household wages are still being squeezed "
    "while capital-goods shipments and labour productivity jumped — so some of this year’s "
    "investment may be creating real value, not only recycling surplus-country savings into "
    "asset prices. The midterm-week tech sell-off tightened financial conditions through markets "
    "rather than through a rise in US unemployment (which fell to 4.1%). Elsewhere, energy-driven "
    "inflation prompted the Reserve Bank of Australia to raise its cash rate to 4.85% and the "
    "Bank of England to 4%, another round of adjustment that lands on mortgagors in deficit countries."
)
PETTIS_PUSHBACK = (
    "Where Pettis leans toward managed trade or US capital-account intervention, a more "
    "market-oriented reading would put the distortion on China’s side of the ledger: the PBOC "
    "stopping the yuan from rising is itself the policy that keeps income away from Chinese "
    "households. Letting the currency appreciate, freeing deposit rates and enforcing harder "
    "budget constraints on state firms would raise the household share without the US adding "
    "tariffs or capital controls, which create their own rents and retaliation. The identity "
    "S − I = CA still holds; the disagreement is whether the fix is more state management in "
    "deficit countries or fewer repression-style distortions in surplus ones. This week’s US "
    "productivity gain also cautions against treating all of the capex boom as non-productive "
    "absorption — some of it may be paying for itself."
)

AI = [
    ("2117343929960112486", "Anthropic opened applications for a paid AI-safety residency; no machine-learning background is required, and the deadline is 22 November."),
    ("2119419126045454531", "Elon Musk says Grok Bot fixes for better token efficiency and smarter behaviour are underway."),
    ("2118124944928432327", "OpenAI launched ChatGPT Images 2.6, adding GIFs and reference images, with two faster image models coming to the API."),
    ("2118390190246879554", "OpenAI introduced GPT-6 Cyber, a security-research model already used on the Linux kernel and by teams at Mozilla and Palo Alto Networks."),
    ("2118814753154064501", "Anthropic explained how Claude uses “dreaming” to organise memory, correct mistakes and retrieve what it has learned."),
    ("2118119451401048497", "OpenAI’s researchers built an autonomous pipeline that found and patched 948 Linux-kernel privilege-escalation bugs in a single run."),
    ("2117307611338997846", "OpenAI released LifeVal, a benchmark of everyday assistant tasks shaped by feedback from thousands of ChatGPT users."),
    ("2117710942826123294", "Anthropic’s FlashProve uses cryptography so developers can verify that a given response came from a given model."),
]
MAC = [
    ("2118379488971043055", "After the midterm-week crash, The Kobeissi Letter asked what had actually changed in the economic backdrop, not just the election result."),
    ("2118455887413285205", "The Nasdaq 100 had its largest daily drop since the 2020 pandemic, and the S&P 500 erased about $3 trillion in a day."),
    ("2118698893210763689", "The US added 165,000 jobs in October (versus 64,000 expected) and unemployment fell to 4.1%, which lifted December hike odds."),
    ("2118147600847118353", "US consumer prices are up 31.3% since April 2020, while average hourly earnings rose only 25.9% over the same stretch."),
    ("2119181497529684135", "The Fed’s balance sheet rose by $3 billion in the week to 4 November, to $6.75 trillion."),
    ("2119249539873886436", "US non-defence capital-goods shipments excluding aircraft jumped 11.6% year on year in September, to a record $86 billion."),
    ("2119116014478565476", "US nonfarm labour productivity rose at a 3.5% annualised pace in the September 2026 quarter, the strongest since the same quarter of 2025."),
    ("2118370577924899272", "Markets blamed tighter AI-regulation fears after the Democratic midterm sweep: Nasdaq 100 down about 5%, chip stocks down 10%, Nvidia down 7%."),
]
PETTIS = [
    ("2119315203275846090", "Pascal Lamy, a long-time free-trader, told Caixin that China’s subsidies, weak consumption and supply-chain price power have distorted open trade."),
    ("2118656238812618918", "Pettis hopes Democrats roll back the Canada tariff fight: the US is right to stop being consumer of last resort, he says, but not this way."),
    ("2119319306047562038", "China’s planning chief admitted the economy faces “strong supply and weak demand” — Pettis’s household-underconsumption diagnosis in official language."),
    ("2118985837039714805", "In a new Substack essay, Pettis argues that hopes of a technological breakthrough are more an excuse to postpone rebalancing than a reason it can wait."),
    ("2118641505221120030", "Raising China’s household share of GDP means cutting the business or government share — which is why, he says, rebalancing keeps being deferred."),
    ("2118972600445718560", "China’s 10-year government bond yield hit a record low of 1.565% as investors fled stocks for safer assets."),
]

def fmt(n):
    return f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.1f}K" if n >= 1e3 else str(n)

def card(pid, take):
    p = POSTS[pid]
    m = p["public_metrics"]
    d = datetime.datetime.fromisoformat(p["created_at"].replace("Z", "+00:00")).astimezone(
        zoneinfo.ZoneInfo("Pacific/Auckland")
    )
    url = f"https://x.com/{p['user']}/status/{pid}"
    return (
        f'<article><div class="meta"><a href="https://x.com/{p["user"]}">@{p["user"]}</a> · {d:%-d %b}</div>'
        f"<p>{html.escape(take)}</p><div class=\"eng\">♥ {fmt(m['like_count'])} · ⟲ {fmt(m['retweet_count'])}"
        f"{' · 👁 ' + fmt(m['impression_count']) if m.get('impression_count') else ''} · "
        f'<a href="{url}">View post →</a></div></article>'
    )

def section(title, summ, items):
    return (
        f"<h2>{title}</h2><div class=\"nut\"><strong>Week in a nutshell.</strong> {html.escape(summ)}</div>"
        + "".join(card(*i) for i in items)
    )

def spark(values, w=88, h=22):
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return ""
    mn, mx = min(vals), max(vals)
    rng = mx - mn or 1
    pts = []
    for i, v in enumerate(vals):
        x = i / (len(vals) - 1) * (w - 2) + 1
        y = h - ((v - mn) / rng) * (h - 4) - 2
        pts.append(f"{x:.1f},{y:.1f}")
    return (
        f'<svg class="spark" width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true">'
        f'<polyline fill="none" stroke="#444" stroke-width="1.4" points="{" ".join(pts)}"/></svg>'
    )

def series_tail(data, key, n=24):
    return [v for _, v in data["series"][key][-n:]]

mig = load_nz("migration.json")
une = load_nz("unemployment.json")
wag = load_nz("wages.json")
vis = load_nz("work_visas.json")

def fmt_num(n, kind="int"):
    if kind == "people":
        sign = "+" if n > 0 else ""
        return f"{sign}{n:,.0f}"
    if kind == "pct":
        return f"{n:.1f}%"
    if kind == "pp":
        sign = "+" if n > 0 else ""
        return f"{sign}{n:.2f}pp"
    if isinstance(n, float) and not n.is_integer():
        return f"{n:,.2f}"
    return f"{n:,.0f}"

rows = [
    {
        "label": "Net migration, annual",
        "value": "+20,500",
        "asof": "Year to August 2026",
        "note": "Up from +9,200 in the August 2025 year. Latest monthly gain: +2,193 in August (after +5,154 in July).",
        "source": "Stats NZ, International migration: August 2026",
        "url": "https://www.stats.govt.nz/information-releases/international-migration-august-2026/",
        "date": "14 Oct 2026",
        "spark": spark(series_tail(mig, "Net migration (12 months)", 36)),
    },
    {
        "label": "Unemployment rate",
        "value": "5.7%",
        "asof": "September 2026 quarter",
        "note": "Highest since September 2015, up from 5.6% in the June quarter.",
        "source": "Stats NZ, Household Labour Force Survey",
        "url": "https://www.stats.govt.nz/information-releases/labour-market-statistics-september-2026-quarter/",
        "date": "4 Nov 2026",
        "spark": spark(series_tail(une, "Unemployment rate", 24)),
    },
    {
        "label": "Number unemployed",
        "value": "174,000",
        "asof": "September 2026 quarter",
        "note": "Up about 3,000 from 171,000 in the June quarter. Employment was 2,891,000, down from 2,896,000, even as the working-age population rose by about 13,000.",
        "source": "Stats NZ, Household Labour Force Survey",
        "url": "https://www.stats.govt.nz/information-releases/labour-market-statistics-september-2026-quarter/",
        "date": "4 Nov 2026",
        "spark": "",
    },
    {
        "label": "Wage growth vs CPI",
        "value": "LCI +2.1%; QES +2.89%; real −0.82pp",
        "asof": "September 2026 quarter",
        "note": "Labour Cost Index all salary and wage rates +2.1% year on year; QES average ordinary-time hourly earnings +2.89% to $44.86. CPI all groups was +3.71% (released 22 Oct 2026), so real average hourly earnings fell for a second quarter.",
        "source": "Stats NZ, labour market statistics and CPI",
        "url": "https://www.stats.govt.nz/information-releases/labour-market-statistics-september-2026-quarter/",
        "date": "4 Nov 2026 (CPI 22 Oct 2026)",
        "spark": spark(series_tail(wag, "Real wage growth (QES - CPI)", 24)),
    },
    {
        "label": "Work-visa approvals",
        "value": "20,199",
        "asof": "September 2026",
        "note": "July 16,289 and August 17,502; 53,990 approved in the first three months of the 2026/27 financial year. The 2025/26 year total was 201,179.",
        "source": "Immigration NZ, work applications decided",
        "url": "https://www.immigration.govt.nz/about-us/research-and-statistics/statistics/",
        "date": "8 Oct 2026",
        "spark": spark(series_tail(vis, "Approved, month (current FY)", 12)),
    },
]

nz_html = """
<h2>New Zealand</h2>
<div class="nut"><strong>Week in a nutshell.</strong> The standout official release was the labour market. Goods trade, the dollar, export prices and mortgage rates also moved, or were updated, around households this week.</div>
<div class="prose">
<p>The latest goods-trade figures are still those for September, published on 19 October. Stats NZ recorded a monthly deficit of $2.0 billion: exports rose 12% on a year earlier, to $6.5 billion, while imports rose 18%, to $8.4 billion. Petroleum and petroleum products were $1.2 billion of those imports, up $608 million or 96% on September 2025, “predominately driven by higher prices.” For the year to September the goods deficit was about $6.2 billion. The broader balance-of-payments goods-and-services balance, year-ended June 2026, was −$2.95 billion, and the current-account deficit was 3.2% of GDP, or −$14.58 billion (<a href="https://www.stats.govt.nz/information-releases/overseas-merchandise-trade-september-2026/">Stats NZ, Overseas merchandise trade: September 2026</a>, 19 Oct 2026; <a href="https://www.stats.govt.nz/information-releases/balance-of-payments-and-international-investment-position-june-2026-quarter/">Balance of payments, June 2026 quarter</a>, 16 Sep 2026).</p>
<p>The New Zealand dollar is historically weak. On 6 November the Reserve Bank’s 17-currency trade-weighted index was 63.66 and one kiwi bought US$0.55960, after an October monthly-average TWI of 64.05 and US$0.5632 (<a href="https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/exchange-rates-and-the-trade-weighted-index">RBNZ B1</a>, 6 Nov 2026). A weaker kiwi supports exporters, but it raises the cost of the roughly 24% of household consumption that is imported goods.</p>
<p>That import-price pressure already shows up in the terms of trade. In the June 2026 quarter the goods terms of trade fell 9.0% on the quarter and 9.4% on the year, because import prices jumped — especially petroleum — not because export prices collapsed (<a href="https://www.stats.govt.nz/information-releases/international-trade-june-2026-quarter/">Stats NZ, International trade: June 2026 quarter</a>, 3 Sep 2026). Some offset arrived this week on the export side: ANZ’s world commodity-price index rose 0.6% in October (up 2.0% on the year), and the NZ-dollar index rose 2.5% because the kiwi weakened after the Reserve Bank’s late-October decision to leave the OCR unchanged. Dairy prices rose 1.6% on the month; skim milk powder was up 5.9% on the month and 51.6% on the year, while butter fell 3.3% and 29.3% respectively (<a href="https://www.anz.co.nz/content/dam/anzconz/documents/economics-and-market-research/2026/ANZ-CPI-20261104.pdf">ANZ Commodity Price Index</a>, 4 Nov 2026).</p>
<p>Productivity per person is still barely moving. Real GDP per capita was $13,410 in the June 2026 quarter (2009/10 prices), up just 0.08% on the quarter and still below the September 2022 peak of $13,718. There was no new GDP or productivity release this week (<a href="https://www.stats.govt.nz/information-releases/gross-domestic-product-june-2026-quarter/">Stats NZ, GDP: June 2026 quarter</a>, 17 Sep 2026).</p>
<p>Household mortgage costs have stopped falling in any meaningful way. The OCR remains 2.75% after the late-October hold; the next review is on 9 December. Carded standard rates at the end of October, published on 6 November, were 6.43% floating (unchanged from September) and 5.54% for a one-year fix (5.55% in September) (<a href="https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/wholesale-interest-rates">RBNZ B2</a>; <a href="https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/new-residential-mortgage-standard-interest-rates">RBNZ B20</a>, 6 Nov 2026). Housing lending was $404.76 billion in September, up 5.4% on the year (<a href="https://www.rbnz.govt.nz/statistics/series/lending-and-monetary/registered-banks-and-non-bank-lending-institutions-sector-lending">RBNZ C5</a>, 30 Oct 2026). House prices remain roughly flat: the CoreLogic index via the Reserve Bank was 3,365 in the June 2026 quarter, down 0.3% on the year (<a href="https://www.rbnz.govt.nz/statistics/series/economic-indicators/housing">RBNZ M10</a>, 9 Oct 2026).</p>
</div>
"""

tracker_rows = []
for r in rows:
    tracker_rows.append(
        "<tr>"
        f"<td><strong>{html.escape(r['label'])}</strong><div class=\"note\">{html.escape(r['note'])}</div></td>"
        f"<td class=\"num\">{html.escape(r['value'])}<div class=\"asof\">{html.escape(r['asof'])}</div></td>"
        f"<td class=\"sparkcell\">{r['spark']}</td>"
        f"<td class=\"src\"><a href=\"{r['url']}\">{html.escape(r['source'])}</a><div class=\"asof\">{html.escape(r['date'])}</div></td>"
        "</tr>"
    )

thesis = (
    "This week’s standout release is the 4 November labour-market report. Unemployment rose to "
    "5.7% — the highest since September 2015 — with 174,000 people out of work, while employment "
    "fell by about 5,000 even as the working-age population rose by about 13,000. Real average "
    "hourly earnings are still falling (2.89% versus CPI of 3.71%). At the same time, net migration "
    "is rising again (an annual gain of 20,500 in the year to August, up from 9,200 a year earlier) "
    "and work-visa approvals were 20,199 in September. That combination — more unemployed New "
    "Zealanders, weak real wages, and still-easy migrant hiring — supports the labour-market half "
    "of the thesis. The housing-and-trade half is less newly confirmed this week. Mortgage debt is "
    "still growing (5.4% year on year, to $405 billion in September), which fits the idea that "
    "housing credit absorbs the external deficit, but house prices are roughly flat rather than "
    "inflating, and September’s $2.0 billion goods-trade deficit was driven mainly by a near-doubling "
    "of the fuel-import bill, not by a fresh migration spike. The kiwi is already weak, so households "
    "are paying more for the imported share of spending even without a further migration-driven "
    "move in the currency."
)

tracker_html = f"""
<h2>NZ labour &amp; migration tracker</h2>
<div class="nut"><strong>Thesis check: supports.</strong> {html.escape(thesis)}</div>
<table class="tracker">
<thead><tr><th>Indicator</th><th>Latest</th><th>Trend</th><th>Source</th></tr></thead>
<tbody>
{''.join(tracker_rows)}
</tbody>
</table>
"""

now = datetime.datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland"))
out = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI &amp; Macro Pulse · Simon Manning</title><style>
body{{margin:0;font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#222;background:#fafafa;line-height:1.6}}
main{{max-width:720px;margin:0 auto;padding:64px 24px}}
h1{{font-weight:600;font-size:2.2rem;margin:0 0 4px}} .sub{{color:#777;margin:0 0 8px}}
h2{{font-size:.8rem;letter-spacing:.15em;text-transform:uppercase;color:#999;margin:44px 0 12px}}
.nut{{background:#fff;border-left:3px solid #222;padding:12px 16px;margin-bottom:16px;font-size:.95rem}}
article{{background:#fff;border:1px solid #e4e4e4;border-radius:10px;padding:12px 16px;margin:10px 0}}
article p{{margin:4px 0}} .meta,.eng{{font-size:.85rem;color:#888}} a{{color:#222}}
.prose p{{margin:0 0 12px}} .push{{background:#fff;border:1px dashed #bbb;border-radius:10px;padding:12px 16px;margin:12px 0 8px;font-size:.95rem}}
table.tracker{{width:100%;border-collapse:collapse;background:#fff;font-size:.92rem}}
table.tracker th,table.tracker td{{border-bottom:1px solid #eee;padding:10px 8px;vertical-align:top;text-align:left}}
table.tracker th{{font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;color:#888;font-weight:600}}
.note,.asof{{color:#888;font-size:.82rem;margin-top:4px;font-weight:400}}
td.num{{white-space:nowrap}} td.sparkcell{{width:96px}} svg.spark{{display:block}}
footer{{margin-top:56px;color:#aaa;font-size:.85rem}}
</style></head><body><main>
<p><a href="../">← Simon Manning</a></p>
<h1>AI &amp; Macro Pulse</h1>
<p class="sub">The week's most-engaged posts on X about AI and the economy, with a Pettis reading, official New Zealand figures, and a labour-and-migration thesis check.</p>
<p class="sub">Last updated: {now:%-d %B %Y, %-I:%M %p} NZT · covers the past 7 days</p>
{section("Artificial intelligence", AI_SUM, AI)}
{section("Macroeconomics", MAC_SUM, MAC)}
<h2>Pettis lens</h2>
<div class="nut"><strong>Week in a nutshell.</strong> {html.escape(PETTIS_SUM)}</div>
<div class="push"><strong>A market-oriented counterpoint.</strong> {html.escape(PETTIS_PUSHBACK)}</div>
{''.join(card(*i) for i in PETTIS)}
{nz_html}
{tracker_html}
<footer>Data from public X posts via Grok Bot and from Stats NZ, the Reserve Bank of New Zealand, Immigration NZ and ANZ as linked. Engagement figures are a snapshot taken when the page was built. © 2026 Simon Manning</footer>
</main></body></html>"""

(D / "index.html").write_text(out)
print("ok", len(AI) + len(MAC) + len(PETTIS), "posts;", now.isoformat())
