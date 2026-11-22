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
    "Anthropic’s week. It priced its initial public offering at $83 a share, above the marketed range, and "
    "began trading on Nasdaq on 19 November; X’s news summaries put the raise at $81.3 billion, the largest "
    "IPO on record, with a first-day close of $97.17, up 17%. Its 72-second listing-day thank-you film was the "
    "most-liked AI post of the week, at about 119,000 likes. By Friday the stock was 27% below its post-IPO "
    "high and close to the issue price as tech shares slid. On 20 November Anthropic mathematician Levent "
    "Alpöge announced a proof of the Riemann Hypothesis worked out with Claude and written in the Lean proof "
    "language; X’s news summaries report that Lean and Mathlib maintainers have checked that the code compiles, "
    "while human review goes on. OpenAI released GPT-6.2 Astra and Sol (about 36,000 likes), published "
    "research on stopping others from “distilling” its models, and its chief scientist Jakub Pachocki shared "
    "pretraining progress figures and proposed common limits across labs, which Sam Altman called “the most "
    "important thing OpenAI has published in awhile.” Google rolled out Gemini 4 Neon, which sits between "
    "Carbon and Hydrogen, and Isomorphic Labs raised $5 billion for AI drug design."
)
MAC_SUM = (
    "A risk-off week. The S&P 500 fell for seven days in a row, its first such run since 2020, and a 3.7% drop "
    "on Friday 20 November took the week’s loss of market value to about $6 trillion. The Nasdaq Composite "
    "turned negative for 2026 after being up 19%, and the Nasdaq 100 entered a bear market, 21% below its "
    "October peak. Nvidia was at the centre: it is down about 45% since 6 October, a $2.8 trillion loss, amid "
    "the Jensen Huang affair and a new SEC inquiry into its accounting. Taiwan’s market fell 18% in the week, "
    "and regulators there restricted short selling. President Trump threatened a “tremendous tax” on US "
    "companies that build data centres abroad, and he met Presidents Putin and Xi in the first three-way "
    "meeting of sitting US, Russian and Chinese leaders. Commodities fell too: US oil dropped below $82 a "
    "barrel, gold below $3,550 an ounce and silver below $42. Minutes of the last Fed meeting showed almost "
    "all officials saw “further action” as appropriate, and a couple were open to more than 25 basis points "
    "in December. Even so, the rush to safety pulled the US 10-year yield down 24 basis points on the week, "
    "to 4.91%."
)
PETTIS_SUM = (
    "Pettis’s accounting identity did most of the work this week. China’s October data showed fixed-asset "
    "investment down 8.1% in the first ten months and private investment down 11.4%, while retail sales rose "
    "just 0.4% on the year, or 2.5% excluding cars, against GDP growth of 4.5%. When production outruns "
    "consumption and investment is shrinking, Pettis notes, “a rising trade surplus is the obverse of "
    "declining investment.” The gap has to be exported, or production falls and unemployment rises. Beijing’s "
    "response came on 22 November, when the planning agency urged local governments to speed up construction "
    "projects. Pettis said the purpose of such projects “is less to serve the needs of the underlying economy "
    "and more to achieve the politically-determined GDP growth target.” He also sized the spillover. China’s "
    "$1.5 trillion surplus, net of gold imports, equals 1.4% of the rest of the world’s GDP, “the rough "
    "equivalent of a fiscal contraction” for everyone else, which helps explain why fiscal deficits elsewhere "
    "must rise. He said the same applies to Taiwan, which keeps wages growing more slowly than productivity, "
    "and he shared Stanford economist Xu Chenggang’s complaint that making households pay more social "
    "insurance weakens demand further. On the deficit side, his thread on Ruchir Sharma’s finding that 80% "
    "of global equity flows this year went into US stocks argues that foreign buying of US assets must, by "
    "accounting, widen the US current-account deficit. The US then adjusts through more household or fiscal "
    "debt, or through higher unemployment. On this page’s reading, not his, that also frames the week’s US "
    "sell-off: the same inflows that lifted AI valuations and the US deficit can reverse. His latest Substack "
    "essay is still “Rebalancing and Technological Breakthroughs” (7 November)."
)
PETTIS_PUSHBACK = (
    "Much of this week’s China story is state-made. Local governments are told to build to hit a growth "
    "target, soft budget constraints leave contractors unpaid, and households face a social-insurance squeeze "
    "instead of broad tax reform. A market-oriented reader can accept Pettis’s diagnosis but would rather "
    "remove those distortions than add new administered transfers: hard budget constraints, market-set "
    "interest rates, a freer yuan and a smaller tax wedge on workers. On the US side, the critic would say "
    "the 80% share of global equity flows reflected where investors expected returns, and this week’s "
    "sell-off shows markets correcting that view on their own. Managing capital inflows, as Pettis has "
    "proposed, would add a new distortion rather than remove one."
)

AI = [
    ("2123431689934291083", "On listing day Anthropic posted a 72-second thank-you film; Claude’s account said it thanks the people behind the projects shown. The most-liked AI post of the week."),
    ("2122750124543926515", "OpenAI released GPT-6.2 Astra and Sol, pitched as efficient models “built to perform where it counts”; Sam Altman singled out 6.2 Sol ultrafast."),
    ("2123167780988125621", "Sundar Pichai launched Gemini 4 Neon, with frontier-level intelligence and fast task completion for software, knowledge work and science, rolling out in the API and to paid subscribers."),
    ("2123196808675405860", "Anthropic priced its IPO at $83 a share, above the marketed range, ahead of its Nasdaq debut on 19 November."),
    ("2124010579836768572", "Ethan Mollick, as news of the Riemann proof spread: it is amazing that training a system to predict the next word in a sentence “would get us this far.”"),
    ("2122662616367853670", "Demis Hassabis announced $5 billion of funding for Isomorphic Labs to cut the time and cost of finding new medicines with AI."),
    ("2123869629164786137", "Sundar Pichai marked the AI-assisted Riemann Hypothesis proof with an image of Euler, Gauss and Riemann reading the headline."),
    ("2123461658890686863", "Dario Amodei’s IPO remarks: AI could compress a century of medical progress into a decade, and Anthropic will pace training and deployment “taking as long as is necessary” to be confident it is safe."),
    ("2124551594691932405", "Sam Altman backed chief scientist Jakub Pachocki’s post sharing OpenAI’s pretraining progress and calling for common limits across labs."),
]
MAC = [
    ("2123024053640274028", "Presidents Trump, Putin and Xi met and shook hands, the first three-way meeting of sitting US, Russian and Chinese leaders."),
    ("2123874615449768331", "Nvidia has lost $2.8 trillion of market value since its 6 October high, the largest 45-day loss for any stock on record."),
    ("2123810146006532136", "The Nasdaq Composite turned negative for 2026, wiping out a gain of 19%."),
    ("2123834118299349003", "President Trump said he will impose a “tremendous tax” on any US company that builds data centres outside the US."),
    ("2123107215477547378", "US oil fell below $82 a barrel for the first time since 27 August, and petrol prices had their largest one-day drop in 18 years."),
    ("2123601545434710165", "Gold fell below $3,550 an ounce and silver below $42 as the sell-off spread to precious metals."),
    ("2123884549574623420", "The S&P 500 fell 3.7% on 20 November, erasing about $6 trillion of market value in the week; its first seven-day losing streak since 2020."),
    ("2124190855770656830", "Taiwan restricted short selling and raised margin requirements after its market fell 18% in a week, the worst week in 35 years."),
    ("2123134143437361568", "Fed minutes: almost all officials saw “further action” as appropriate, and a couple thought a hike of more than 25 basis points may be warranted in December."),
]
PETTIS = [
    ("2122361005917237722", "Ruchir Sharma: 80% of global equity flows this year went into US stocks. Pettis’s thread: by accounting, that widens the US current-account deficit, which the US absorbs through more debt or unemployment."),
    ("2124012607048695907", "Stanford’s Xu Chenggang, shared by Pettis: squeezing ordinary people for more social insurance to plug fiscal holes “makes demand even weaker.”"),
    ("2123301813990375441", "China’s $1.5 trillion surplus, net of gold imports, equals 1.4% of the rest of the world’s GDP, roughly a fiscal contraction that forces deficits elsewhere to rise."),
    ("2123797298547204389", "Taiwan, like mainland China, keeps wages growing more slowly than productivity; a persistent double-digit surplus “undermines global growth by more than it boosts domestic growth.”"),
    ("2123672135038362005", "A line Pettis shared: if surplus countries won’t rebalance, the rest of the world must accept weaker growth, more private debt, or larger fiscal deficits."),
    ("2122373988345135251", "China’s fixed-asset investment fell 8.1% in the first ten months; Pettis: “a rising trade surplus is the obverse of declining investment.”"),
    ("2124401141987607019", "Beijing urged local governments to speed up construction; Pettis says such projects aim more at the GDP target than at the economy’s needs."),
    ("2122558847197876441", "China’s retail sales rose only 0.4% on the year in October, and 2.5% excluding cars, against GDP growth of 4.5%."),
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
        "note": "Up from +9,900 in the September 2025 year: a net gain of 60,400 non-New Zealand citizens offset a net loss of 37,800 New Zealand citizens. Latest monthly gain: +3,509 in September (provisional). No new release this week; October figures are due in December.",
        "source": "Stats NZ, International migration: September 2026",
        "url": "https://www.stats.govt.nz/information-releases/international-migration-september-2026/",
        "date": "12 Nov 2026",
        "spark": spark(series_tail(mig, "Net migration (12 months)", 36)),
    },
    {
        "label": "Unemployment rate",
        "value": "5.7%",
        "asof": "September 2026 quarter",
        "note": "Highest since September 2015, up from 5.6% in the June quarter. No new release this week; December-quarter figures are due in early February.",
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
        "date": "8 Oct 2026 (checked 23 Nov 2026; no newer release)",
        "spark": spark(series_tail(vis, "Approved, month (current FY)", 12)),
    },
]

nz_html = """
<h2>New Zealand</h2>
<div class="nut"><strong>Week in a nutshell.</strong> The kiwi slid to another 17-year low, just under US$0.548, as global markets sold off. October’s goods deficit widened to $2.8 billion on aircraft and fuel imports, and petrol cost 38% more than a year earlier. The Reserve Bank’s Financial Stability Report warned about global and AI risks but called housing risks “contained.” Mortgage rates barely moved ahead of the 9 December OCR decision, where Westpac expects a hike.</div>
<div class="prose">
<p>Trade: October’s goods figures came out on 19 November. Exports rose $509 million (7.9%) on a year earlier, to $7.0 billion, but imports rose $1.7 billion (21%), to $9.7 billion, leaving a monthly deficit of $2.8 billion. Two items drove the imports: aircraft and parts were up $711 million because large aircraft were delivered, and petroleum was up $445 million (49%). Leaving the aircraft out would put the deficit at roughly $2.1 billion (our arithmetic). Over the year to October, exports were $86.2 billion and imports $93.7 billion, so the annual goods deficit was $7.5 billion, up from $2.3 billion a year earlier (<a href="https://www.stats.govt.nz/information-releases/overseas-merchandise-trade-october-2026/">Stats NZ, Overseas merchandise trade: October 2026</a>, 19 Nov 2026). The broader figures haven’t changed. The year-ended goods-and-services balance to June 2026 was −$2.95 billion and the current-account deficit 3.2% of GDP, or −$14.58 billion; September-quarter figures are due in December (<a href="https://www.stats.govt.nz/information-releases/balance-of-payments-and-international-investment-position-june-2026-quarter/">Balance of payments, June 2026 quarter</a>, 16 Sep 2026).</p>
<p>The New Zealand dollar started this week at just under US$0.548, its lowest since March 2009 and down half a cent on the week. The five-currency TWI was just under 59.2, its lowest since May 2009, but the kiwi rose against the Australian dollar, to 82.7 cents, so this is mainly a strong US dollar in a flight to safety (<a href="https://www.interest.co.nz/economy/141180/eyes-wall-street-japan-inflation-china-foreign-direct-investment-inflows-slow-taiwan">interest.co.nz breakfast briefing</a>, 23 Nov 2026). The Reserve Bank’s October monthly averages were a 17-currency TWI of 64.05 and US$0.5632, and its daily series showed 63.14 and US$0.5503 on 18 November (<a href="https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/exchange-rates-and-the-trade-weighted-index">RBNZ B1</a>). For households, a weak kiwi raises the cost of the roughly 24% of consumption that is imported goods, and fuel shows it most clearly. In October petrol prices rose 11.9% in the month and 38.0% on the year, and diesel 71.2% on the year. Electricity was up 9.4%, gas 11.0% and international airfares 13.1% on the year, while food prices fell 0.4% in the month and were 2.3% higher on the year (<a href="https://www.stats.govt.nz/information-releases/selected-price-indexes-october-2026/">Stats NZ, Selected price indexes: October 2026</a>, 17 Nov 2026). Near-term expectations are rising: in the Reserve Bank’s survey of business people and forecasters, one-year-ahead inflation expectations rose to 2.92% from 2.60%, but the two-year measure barely moved, to 2.36% (<a href="https://www.rbnz.govt.nz/statistics/series/economic-indicators/survey-of-expectations">RBNZ Survey of Expectations</a>, 17 Nov 2026; <a href="https://www.westpaciq.com.au/economics/2026/11/first-impression-rbnz-survey-of-inflation-expectations-december-">Westpac</a>, 17 Nov 2026).</p>
<p>The terms of trade are mixed. At the 17 November Global Dairy Trade auction the overall index was unchanged at an average US$4,182 a tonne. Whole milk powder rose 2.7% and skim milk powder 2.2%, but butter fell 6.5%, anhydrous milk fat 8.2% and cheddar 4.1% (<a href="https://www.globaldairytrade.info/blog/behind-the-market-gdt-trading-event-416">GDT, Trading Event 416</a>, 18 Nov 2026). The next auction is on 1 December. The fat slump is already showing up in the trade data: milk-fat export prices were 15% lower in October than a year earlier. ANZ’s commodity index rose 0.6% in October, or 2.5% in NZ-dollar terms; November’s index is due in early December (<a href="https://www.anz.co.nz/content/dam/anzconz/documents/economics-and-market-research/2026/ANZ-CPI-20261104.pdf">ANZ Commodity Price Index</a>, 4 Nov 2026). On the import side, oil fell sharply: Brent started the week at about US$92.50 a barrel, down from US$95.50 a week earlier (interest.co.nz, 23 Nov 2026). The latest official goods terms of trade, for the June 2026 quarter, fell 9.0% on the quarter because of the jump in petroleum prices, and September-quarter figures are due in early December (<a href="https://www.stats.govt.nz/information-releases/international-trade-june-2026-quarter/">Stats NZ, International trade: June 2026 quarter</a>, 3 Sep 2026). Producer prices rose 0.8% in the September quarter (outputs) and 0.7% (inputs). Stats NZ also corrected past output prices for meat and dairy manufacturing upward (<a href="https://www.stats.govt.nz/information-releases/business-price-indexes-september-2026-quarter/">Stats NZ, Business price indexes</a>, 18 Nov 2026).</p>
<p>There are no new productivity figures. Real GDP per person was $13,410 in the June 2026 quarter (2009/10 prices), up 0.08% on the quarter and still below the September 2022 peak of $13,718 (<a href="https://www.stats.govt.nz/information-releases/gross-domestic-product-june-2026-quarter/">Stats NZ, GDP: June 2026 quarter</a>, 17 Sep 2026). September-quarter GDP is due in December.</p>
<p>Mortgages: the OCR is 2.75%. It was raised in July and September and held on 28 October, and the next decision, with a Monetary Policy Statement, is on 9 December at 2pm (<a href="https://www.rbnz.govt.nz/news-and-events/events/2026/december/monetary-policy-statement-and-ocr-december-2026">RBNZ</a>). Westpac still expects a hike then, citing firm core inflation. The Reserve Bank’s Financial Stability Report on 17 November said housing vulnerabilities are “present but contained” and the market has softened, especially in Auckland and Wellington, but warned that “recent cost pressures and increases in interest rates may slow or reverse” the easing in financial stress (<a href="https://www.rbnz.govt.nz/financial-stability/financial-stability-report/financial-stability-reports/2026/nov/financial-stability-report-november-2026/web-version">RBNZ FSR</a>, 17 Nov 2026). For borrowers who are refixing, the main banks’ one-year specials are at 4.99% (<a href="https://www.1news.co.nz/2026/11/12/major-bank-lowers-some-mortgage-rates/">1News</a>, 12 Nov 2026). The average major-bank two-year rate fell to 5.35% in October from 5.42%, which cut about $8 a week from payments on a lower-quartile home bought with a 20% deposit (<a href="https://www.interest.co.nz/property/141128/little-movement-overall-mortgage-affordability-first-home-buyers-banks-step-low">interest.co.nz</a>, 19 Nov 2026). Carded standard rates at the end of October were 6.43% floating and 5.54% for a one-year fix (<a href="https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/new-residential-mortgage-standard-interest-rates">RBNZ B20</a>, 6 Nov 2026), and the NZ 10-year government bond yield was 4.82%, down 3 basis points on the week. House prices are still slipping. The REINZ index was down 2.1% on the year in October (up 0.1% in the month), the median price was $763,000 (−3.4%) and sales were 23.5% lower (<a href="https://www.reinz.co.nz/Web/Web/News/News-Articles/Market-updates/Regional_price_strength_stands_out_as_October_sales_pace_slows.aspx">REINZ</a>, 13 Nov 2026). Housing lending was $404.76 billion in September, up 5.4% on the year; October’s figure is due at the end of this month (<a href="https://www.rbnz.govt.nz/statistics/series/lending-and-monetary/registered-banks-and-non-bank-lending-institutions-sector-lending">RBNZ C5</a>, 30 Oct 2026).</p>
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
    "There were no new labour or migration figures this week, so that half of the test stands where it was: "
    "net migration of +22,600 in the year to September, made up of a net gain of 60,400 non-New Zealand "
    "citizens and a net loss of 37,800 New Zealand citizens, arriving while unemployment is at an 11-year "
    "high of 5.7% (174,000 people) and real hourly earnings are falling (2.89% against CPI of 3.71%). That "
    "still supports the labour-market half of the thesis. The new figures are about trade, prices and "
    "housing. The annual goods deficit widened to $7.5 billion from $2.3 billion, but the October jump came "
    "from fuel prices and a one-off aircraft delivery rather than migration-fed spending, and housing credit "
    "growth is steady at about 5.4%. House prices fell 2.1% on the year and sales dropped 23.5% even as net "
    "migration rose, so the migration-to-house-prices link isn’t showing right now, with high listings and "
    "higher interest rates dominating. The kiwi’s new 17-year low again came from a global flight to the US "
    "dollar, not from migration flows. Overall the week doesn’t change the thesis: the labour case still "
    "holds, and the housing and currency links remain out of view while global shocks dominate."
)

tracker_html = f"""
<h2>NZ labour &amp; migration tracker</h2>
<div class="nut"><strong>Thesis check: doesn’t change it (labour half still supported; housing and currency links not visible this week).</strong> {html.escape(thesis)}</div>
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
