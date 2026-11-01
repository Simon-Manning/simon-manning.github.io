#!/usr/bin/env python3
"""Build pulse/index.html from saved X search results (data/ai.txt, data/macro.txt).
Picks + takeaways are curated in PICKS; engagement numbers are read from the data files."""
import json, html, datetime, zoneinfo, pathlib
D = pathlib.Path(__file__).parent
def load(f):
    t = open(D/'data'/f).read(); d = json.loads(t[t.find('{'):t.rfind('}')+1])
    u = {x['id']: x['username'] for x in d.get('includes', {}).get('users', [])}
    return {p['id']: dict(p, user=u[p['author_id']]) for p in d['data']}
POSTS = {**load('ai.txt'), **load('macro.txt')}
AI_SUM = ("A heavy launch week. OpenAI shipped GPT-6.1 Terra (cheaper, better computer use), Google DeepMind released both the Genie 4 world model and its new frontier model Gemini 4 Carbon, and Anthropic showed Claude doing drug-discovery work. Safety was the other big story: both OpenAI and Anthropic published new ways of monitoring their own models for misuse and bad behaviour.")
MAC_SUM = ("Inflation is back. The Fed held at 3.75–4.00% on 28 Oct, but it was a \"hawkish pause\": markets now price roughly a 75% chance of a December hike. The ECB also held at 2.50% with a December hike widely expected, and Lagarde announced she will step down early. US tech stocks sold off hard on 30 Oct. Closer to home, the RBNZ kept the OCR on hold, and NZ economist Michael Reddell questioned how much attention it is paying to oil rather than core inflation.")
AI = [
 ("2114780711664398349","OpenAI released GPT-6.1 Terra: cheaper and better at operating apps on your screen."),
 ("2115114028338962672","DeepMind's Genie 4 generates explorable, interactive 3D worlds with sound in real time."),
 ("2115489356437651654","Google's new top model, Gemini 4 Carbon, claims state-of-the-art results in cybersecurity and long tasks."),
 ("2115178675050307942","Anthropic is working with six drug developers and has started its own drug-discovery work using Claude."),
 ("2114365361068138990","Elon Musk says Grok Bot can now phone a person or business for you and summarise the call."),
 ("2115871889549865429","Claude now runs a quick safety check on each of its conversations to flag possible misuse."),
 ("2115896329645723836","OpenAI says its monitoring system caught a model trying to reach the live internet during training."),
 ("2115277286123704654","Ethan Mollick: new closed benchmarks suggest open-weight models are falling further behind the leaders."),
]
MAC = [
 ("2116240066142154894","Nasdaq 100 fell nearly 5% in one day on 30 Oct, as midterm election odds shifted."),
 ("2115424565086093615","Fed-day preview: expect a hold now with groundwork laid for a December hike."),
 ("2116261977559544282","Markets now see about a 75% chance of a December Fed hike. A year ago they expected three cuts in 2026."),
 ("2114709406537355693","WSJ's Nick Timiraos: the case for hiking was stronger than markets thought, after hot CPI and PPI."),
 ("2116206415534563715","St. Louis Fed's Musalem: further rate rises will be needed, \"and soon\"."),
 ("2115819361004916894","ECB held at 2.50%, possibly ahead of a final hike in December, with little sign yet that energy costs are pushing up wages."),
 ("2115755126468010326","Christine Lagarde will leave the ECB early, in February 2027, which opens a leadership race."),
 ("2116153643720167727","Some relief: German inflation came in at 2.8%, below the 3.0% forecast."),
 ("2115530123235770549","NZ: Michael Reddell says recent RBNZ OCR statements focus on oil prices, not core inflation."),
]
def fmt(n): return f"{n/1e6:.1f}M" if n>=1e6 else f"{n/1e3:.1f}K" if n>=1e3 else str(n)
def card(pid, take):
    p = POSTS[pid]; m = p['public_metrics']
    d = datetime.datetime.fromisoformat(p['created_at'].replace('Z','+00:00')).astimezone(zoneinfo.ZoneInfo('Pacific/Auckland'))
    url = f"https://x.com/{p['user']}/status/{pid}"
    return (f'<article><div class="meta"><a href="https://x.com/{p["user"]}">@{p["user"]}</a> · {d:%-d %b}</div>'
            f'<p>{html.escape(take)}</p><div class="eng">♥ {fmt(m["like_count"])} · ⟲ {fmt(m["retweet_count"])}'
            f'{" · 👁 "+fmt(m["impression_count"]) if m.get("impression_count") else ""} · <a href="{url}">View post →</a></div></article>')
def section(title, summ, items):
    return f'<h2>{title}</h2><div class="nut"><strong>Week in a nutshell.</strong> {html.escape(summ)}</div>' + ''.join(card(*i) for i in items)
now = datetime.datetime.now(zoneinfo.ZoneInfo('Pacific/Auckland'))
out = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI &amp; Macro Pulse · Simon Manning</title><style>
body{{margin:0;font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#222;background:#fafafa;line-height:1.6}}
main{{max-width:640px;margin:0 auto;padding:64px 24px}}
h1{{font-weight:600;font-size:2.2rem;margin:0 0 4px}} .sub{{color:#777;margin:0 0 8px}}
h2{{font-size:.8rem;letter-spacing:.15em;text-transform:uppercase;color:#999;margin:44px 0 12px}}
.nut{{background:#fff;border-left:3px solid #222;padding:12px 16px;margin-bottom:16px;font-size:.95rem}}
article{{background:#fff;border:1px solid #e4e4e4;border-radius:10px;padding:12px 16px;margin:10px 0}}
article p{{margin:4px 0}} .meta,.eng{{font-size:.85rem;color:#888}} a{{color:#222}}
footer{{margin-top:56px;color:#aaa;font-size:.85rem}}
</style></head><body><main>
<p><a href="../">← Simon Manning</a></p>
<h1>AI &amp; Macro Pulse</h1>
<p class="sub">The week's most-engaged posts on X about AI and the economy, with a one-line takeaway for each.</p>
<p class="sub">Last updated: {now:%-d %B %Y, %-I:%M %p} NZT · covers the past 7 days</p>
{section("Artificial intelligence", AI_SUM, AI)}
{section("Macroeconomics", MAC_SUM, MAC)}
<footer>Data from public X posts via Grok Bot. Engagement figures are a snapshot taken when the page was built. © 2026 Simon Manning</footer>
</main></body></html>'''
pathlib.Path(pathlib.Path(__file__).parent).mkdir(exist_ok=True)
open(pathlib.Path(__file__).parent/'index.html','w').write(out); print('ok', len(AI)+len(MAC))
