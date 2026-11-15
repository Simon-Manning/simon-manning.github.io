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
    "A launch-heavy week for Anthropic. It released Claude Fable 5.2 and Claude Mythos 5.2 (the most-liked "
    "AI post of the week, at about 96,000 likes), rolled out Claude Whiteboards, Sheets and Data, and put "
    "Claude into live video calls with Claude Meetings. It also launched the roadshow for its initial public "
    "offering; Reuters reported a range of $70–80 a share. Google answered with Gemini 4 Hydrogen, a fast "
    "everyday model, and Gemini Robotics 2.5 for physical tasks. OpenAI opened a beta that lets businesses "
    "claim a profile and build an agent inside ChatGPT, and described Control Room, a system that can stop "
    "research workloads quickly when safety or security concerns arise. Meta released Muse Ember, its "
    "smallest reasoning and agent model."
)
MAC_SUM = (
    "Inflation is back at the centre. US consumer prices rose 0.4% in October (core 0.3%), both above "
    "forecasts, and producer prices were up 6.5% on the year, the highest since November 2022. Markets moved "
    "to near-certain odds of a December Fed hike, with a small chance of 50 basis points, and Goldman added a "
    "third hike to its forecast. The US 10-year Treasury yield went back above 5% and ended the week at about "
    "5.15%. Nvidia’s chief executive Jensen Huang resigned amid a scandal, which knocked AI stocks before "
    "dip-buyers stepped in. Trade policy stayed noisy: President Trump threatened to double tariffs on Mexico, "
    "and Charlie Bilello pointed out that $128 billion of tariffs were refunded to companies without any "
    "refund to consumers. China’s October exports rose 35.2% on the year and its imports 41.6%."
)
PETTIS_SUM = (
    "China’s October numbers read like a page from Pettis’s notes. Consumer prices rose just 0.7% on the year "
    "and were flat on the month — “given weak consumption… this doesn’t come as a surprise,” he wrote — while "
    "producer prices rose 5.7%, a four-year high, so the gap keeps widening: firms are passing on higher input costs but households "
    "aren’t bidding up consumer goods. New yuan loans fell by about ¥100 billion in October, the first October "
    "contraction on record (interest.co.nz, 16 Nov). When the People’s Bank argued that its loan rates are "
    "already low by world standards, Pettis pushed back that the binding problem is weak consumer loan "
    "demand, not the price of credit. He flagged two signs of supply-side bias: labour-intensive exports are "
    "slowing even though China has among the lowest unit labour costs in the world, and plans to extend the "
    "high-speed rail network by 40% into more economically marginal regions look driven more by investment "
    "targets than economic need. On pensions, he said the household share of GDP must keep rising to fund an "
    "ageing population, which is the rebalancing question again. His latest Substack essay (7 Nov) argues "
    "that hoping for a technological breakthrough is a way to postpone that rebalancing. On the deficit side, "
    "the United States is absorbing China’s surplus with rising rates and a record $5.19 trillion of consumer "
    "credit, and Pettis called President Trump’s threat to double tariffs on Mexico “nonsense” that makes US "
    "trade policy’s impact “either zero or negative.” He also said Russia’s retreat from using the yuan "
    "fits his long-standing argument about surplus countries; as he put it in a reply, Russia cannot balance its trade surplus with ruble assets."
)
PETTIS_PUSHBACK = (
    "Much of what Pettis diagnosed this week is state-made: credit steered into marginal rail lines, local "
    "investment targets, and a central bank leaning against the yuan. A market-oriented fix is to remove those "
    "distortions — harder budget constraints for state firms and local governments, market-set deposit rates, "
    "and a freer currency — so that more income flows to households without a new round of administered "
    "transfers. Guo Shuqing’s idea of moving state-owned capital into the pension system fits both camps, "
    "because it shrinks state ownership while raising household income. On tariffs there was little to "
    "dispute: free-traders and Pettis alike see the Mexico threat as costly to the United States."
)

AI = [
    ("2119867114450268322", "Anthropic launched Claude Fable 5.2 and Claude Mythos 5.2, with gains in coding, reasoning and vision, the most-liked AI post of the week."),
    ("2120973994191094179", "Claude Meetings joins a team’s video call and builds documents and whiteboards during the conversation; beta on Team and Enterprise plans."),
    ("2120206365759094857", "Anthropic began rolling out Claude Whiteboards, Claude Sheets and Claude Data for planning, tracking and data storytelling."),
    ("2120216592395174382", "OpenAI opened a beta that lets businesses claim a profile in ChatGPT and build a Business Agent that answers customers’ questions."),
    ("2120841731302154708", "Anthropic published its IPO prospectus link after filing a registration statement with the SEC; Reuters reported a $70–80 range a share."),
    ("2120940601319260164", "Google released Gemini 4 Hydrogen, a fast everyday model that follows instructions more closely and calls the right tools."),
    ("2119913172039868579", "OpenAI built Control Room, a central system that tracks every research model workload and can stop it quickly on safety or security grounds."),
    ("2120169787896525104", "Google DeepMind’s Gemini Robotics 2.5 learns hundreds of everyday physical skills, from folding laundry to sorting car parts."),
]
MAC = [
    ("2121234688391942348", "US producer-price inflation rose to 6.5% in October, the highest since November 2022; core PPI was 5.0%, as expected."),
    ("2120473795899126012", "Nvidia jumped more than 6% as investors bought the dip after the Jensen Huang scandal, erasing the previous day’s fall."),
    ("2120147133542125818", "US October CPI rose 0.4% on the month (0.3% expected) and core CPI 0.3% (0.2% expected); no annual figures because of last year’s shutdown."),
    ("2120851159879762064", "President Trump threatened to double tariffs on Mexico unless it stops migrant caravans heading to the US."),
    ("2120199304392700371", "The US 10-year Treasury yield rose back above 5% after the hot CPI print, and December hike odds hit a new high."),
    ("2121607597211926983", "US consumer prices are up 30.2% since January 2020, about 4% a year, double the Fed’s 2% target."),
    ("2121324139478757706", "Charlie Bilello: tariffs raised prices, then $128 billion was refunded to companies, but consumers got no refund and many prices kept rising."),
    ("2120243221406089514", "Markets began to price a possible 50-basis-point Fed hike in December (11% odds), with a 25-point hike at 84%."),
]
PETTIS = [
    ("2119952393798332848", "China’s CPI rose only 0.7% on the year in October and was flat on the month — no surprise, Pettis says, given weak consumption."),
    ("2119805695386145162", "Mohamed El-Erian: China’s PPI hit 5.7%, a four-year high, widening the gap with consumer inflation."),
    ("2120992708991037574", "Pettis on the PBOC’s claim that its loan rates are low by world standards: the real constraint is weak consumer loan demand."),
    ("2120237210687672738", "China’s labour-intensive exports slowed again despite some of the world’s lowest unit labour costs, Pettis notes from Caixin."),
    ("2121842324015911405", "On plans to extend high-speed rail by 40% into marginal regions: it is “hard to believe” this will be economically justified."),
    ("2121846858230247447", "Former regulator Guo Shuqing warned China’s pension system could run short within 20 years; Pettis ties it to the household share of GDP."),
    ("2120981900001153097", "Pettis calls the threat to double Mexico tariffs “nonsense” that leaves US trade policy’s impact “either zero or negative.”"),
    ("2120566766598496482", "Russia has effectively abandoned replacing the dollar with the yuan; Pettis says it fits his long-running argument about surplus countries."),
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
        "value": "+22,600",
        "asof": "Year to September 2026",
        "note": "Up from +9,900 in the September 2025 year: a net gain of 60,400 non-New Zealand citizens offset a net loss of 37,800 New Zealand citizens. Latest monthly gain: +3,509 in September (provisional).",
        "source": "Stats NZ, International migration: September 2026",
        "url": "https://www.stats.govt.nz/information-releases/international-migration-september-2026/",
        "date": "12 Nov 2026",
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
        "date": "8 Oct 2026 (no newer release found)",
        "spark": spark(series_tail(vis, "Approved, month (current FY)", 12)),
    },
]

nz_html = """
<h2>New Zealand</h2>
<div class="nut"><strong>Week in a nutshell.</strong> The kiwi slid to its lowest against the US dollar since March 2009 as US yields jumped, migration figures showed net gains rising again, and card spending fell for a third month as fuel bills crowded out other purchases. Banks trimmed some fixed mortgage rates, even as their economists warn rates are heading up.</div>
<div class="prose">
<p>No new goods-trade figures this week; October’s are due shortly. The latest are still for September, published on 19 October: a monthly deficit of $2.0 billion, with exports up 12% on a year earlier, to $6.5 billion, and imports up 18%, to $8.4 billion. Petroleum imports were $1.2 billion, up 96%, “predominately driven by higher prices.” The goods deficit for the year to September was about $6.2 billion. The year-ended goods-and-services balance to June 2026 was −$2.95 billion, and the current-account deficit was 3.2% of GDP, or −$14.58 billion (<a href="https://www.stats.govt.nz/information-releases/overseas-merchandise-trade-september-2026/">Stats NZ, Overseas merchandise trade: September 2026</a>, 19 Oct 2026; <a href="https://www.stats.govt.nz/information-releases/balance-of-payments-and-international-investment-position-june-2026-quarter/">Balance of payments, June 2026 quarter</a>, 16 Sep 2026).</p>
<p>The New Zealand dollar fell further. On 16 November one kiwi bought just under US$0.553, its lowest since March 2009, and the five-currency TWI was about 59.4, a 17-year low. The US dollar is at a 19-month high on rising US interest rates, with the US 10-year yield at 5.15%, up 30 basis points in the week (<a href="https://www.interest.co.nz/economy/141090/chinese-slowdown-sees-borrowing-retreat-us-ppi-stays-very-elevated-us-budget-deficit">interest.co.nz breakfast briefing</a>, 16 Nov 2026). The Reserve Bank’s October monthly averages were a 17-currency TWI of 64.05 and US$0.5632 (<a href="https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/exchange-rates-and-the-trade-weighted-index">RBNZ B1</a>, 6 Nov 2026). For households, a weaker kiwi raises the cost of the roughly 24% of consumption that is imported goods, and fuel is the clearest example: October card spending on fuel rose 4.8% while core retail spending fell 1.2% ($73 million), the third monthly fall in a row, with durables down 2.1% and hospitality down 1.6% (<a href="https://www.stats.govt.nz/information-releases/electronic-card-transactions-october-2026/">Stats NZ, Electronic card transactions: October 2026</a>, 12 Nov 2026). ASB’s Yen Nguyen said high fuel prices are “taxing consumption” (<a href="https://www.interest.co.nz/business/141061/higher-fuel-prices-and-weak-job-market-dragged-nz-electronic-card-spending-down">interest.co.nz</a>, 12 Nov 2026). Westpac noted that its own card data was stronger than the official series.</p>
<p>The terms of trade are the offset. Export prices for dairy are firm: at the 3 November Global Dairy Trade auction the index rose 3% to an average US$4,166 a tonne, with whole milk powder up 5.9% and skim milk powder up 3.1%, while butter fell 4.7% (<a href="https://www.rnz.co.nz/news/business/2330539/average-dairy-prices-rise-3-percent-overnight">RNZ</a>, 4 Nov 2026); the next auction is on 18 November. ANZ’s commodity index rose 0.6% in October, and 2.5% in NZ-dollar terms (<a href="https://www.anz.co.nz/content/dam/anzconz/documents/economics-and-market-research/2026/ANZ-CPI-20261104.pdf">ANZ Commodity Price Index</a>, 4 Nov 2026). But the latest official goods terms of trade, for the June 2026 quarter, fell 9.0% on the quarter and 9.4% on the year because import prices, especially petroleum, jumped (<a href="https://www.stats.govt.nz/information-releases/international-trade-june-2026-quarter/">Stats NZ, International trade: June 2026 quarter</a>, 3 Sep 2026). A record-low kiwi helps exporters’ NZ-dollar returns but makes the fuel bill heavier.</p>
<p>Productivity per person has not been updated: real GDP per capita was $13,410 in the June 2026 quarter (2009/10 prices), up 0.08% on the quarter and still below the September 2022 peak of $13,718 (<a href="https://www.stats.govt.nz/information-releases/gross-domestic-product-june-2026-quarter/">Stats NZ, GDP: June 2026 quarter</a>, 17 Sep 2026). September-quarter GDP is due in December.</p>
<p>Mortgages: the OCR is 2.75% after October’s 4–3 hold, and the next review is on 9 December. Banks are competing at the short end: from 11 November Westpac cut its one-year special by 20 basis points to 4.99% and trimmed its three-, four- and five-year rates, but raised its two-year special to 5.39%, and said its economists “still think interest rates are heading upwards over the next year” (<a href="https://www.1news.co.nz/2026/11/10/major-bank-cuts-most-fixed-rates-but-warns-interest-rates-will-rise/">1News</a>, 10 Nov 2026). The NZ 10-year government bond yield was 4.85%, up 6 basis points on the week (interest.co.nz, 16 Nov 2026). Carded standard rates at the end of October were 6.43% floating and 5.54% for a one-year fix (<a href="https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/new-residential-mortgage-standard-interest-rates">RBNZ B20</a>, 6 Nov 2026). Housing lending was $404.76 billion in September, up 5.4% on the year (<a href="https://www.rbnz.govt.nz/statistics/series/lending-and-monetary/registered-banks-and-non-bank-lending-institutions-sector-lending">RBNZ C5</a>, 30 Oct 2026), and house prices are roughly flat, down 0.3% on the year in the June quarter (<a href="https://www.rbnz.govt.nz/statistics/series/economic-indicators/housing">RBNZ M10</a>, 9 Oct 2026). The Reserve Bank’s Financial Stability Report is due this week.</p>
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
    "The new figure this week is migration. Net migration rose to 22,600 in the year to September, up "
    "from 9,900 a year earlier, made up of a net gain of 60,400 non-New Zealand citizens and a net loss "
    "of 37,800 New Zealand citizens. That is happening while unemployment is at an 11-year high of 5.7% "
    "(174,000 people), real hourly earnings are still falling (2.89% against CPI of 3.71%), work-visa "
    "approvals were 20,199 in September, and card spending has fallen for three months. Rising inflows "
    "of non-citizen workers into a slack labour market, alongside falling real wages, support the "
    "labour-market half of the thesis. The currency and housing half is challenged this week: the kiwi "
    "fell to a 17-year low even as migration rose, because US interest rates and the US dollar are "
    "driving it, and house prices are flat. Mortgage lending is still growing about 5% a year, which "
    "fits the idea that housing credit funds the external deficit, but this week’s data gives no sign "
    "that migration is propping up the NZD or house prices. Overall the week doesn’t change the thesis: "
    "it strengthens the labour case and weakens the near-term currency link."
)

tracker_html = f"""
<h2>NZ labour &amp; migration tracker</h2>
<div class="nut"><strong>Thesis check: doesn’t change it (supports the labour half, challenges the currency link).</strong> {html.escape(thesis)}</div>
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
