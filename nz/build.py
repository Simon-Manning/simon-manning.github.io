#!/usr/bin/env python3
"""Refresh data for the NZ Economy Explorer (nz/index.html).

Official sources only:
  * Stats NZ "CSV files for download" (HLFS, LCI, QES, CPI, BoP, GDP, OTI, international migration)
  * RBNZ statistics B1 (exchange rates / TWI) and B20 (mortgage rates) xlsx files
  * Immigration NZ "Work applications decided" statistics pack (PDF)

Usage (from repo root):   python3 nz/build.py
Needs: python3 with openpyxl + playwright (RBNZ blocks plain HTTP clients, so the
RBNZ files are downloaded through a real Chrome via Playwright), and pdftotext (poppler).
If a source fails, the previous nz/data/<id>.json is kept and the failure is recorded
in nz/data/meta.json ("gaps"/"stale"). Nothing is ever estimated or filled in.
"""
import csv, io, json, os, re, subprocess, sys, tempfile, zipfile, datetime, urllib.request, html as H

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'data')
TMP = tempfile.mkdtemp(prefix='nzbuild_')
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36'}
START = 2015
STATS = 'https://www.stats.govt.nz'
TODAY = datetime.date.today().isoformat()
log = []


def get(url, binary=True):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        b = r.read()
    return b if binary else b.decode('utf-8', 'replace')


def tnum(period):
    """Stats NZ period 'YYYY.MM' or 'YYYY-MM' -> label 'YYYY-MM'."""
    y, m = re.split(r'[.-]', str(period))[:2]
    return f"{int(y):04d}-{int(m):02d}"


def write(id_, obj):
    obj['id'] = id_
    obj['fetched'] = TODAY
    with open(os.path.join(OUT, id_ + '.json'), 'w') as f:
        json.dump(obj, f, separators=(',', ':'))
    log.append(('ok', id_))


# ---------------- Stats NZ ----------------
_links = None
def stats_link(pattern):
    global _links
    if _links is None:
        s = H.unescape(get(STATS + '/large-datasets/csv-files-for-download/', False))
        _links = [l.replace('\\/', '/') for l in re.findall(r'"DocumentLink":"([^"]+)"', s)]
    for l in _links:
        if re.search(pattern, l.split('/')[-1], re.I):
            return STATS + l
    raise RuntimeError('no Stats NZ file matching ' + pattern)


_rel = {}
def release_info(link):
    """Release page + date, derived from the asset folder name."""
    folder = link.split('/assets/Uploads/')[1].split('/')[1].lower()
    url = f'{STATS}/information-releases/{folder}/'
    if url not in _rel:
        try:
            s = get(url, False)
            m = re.search(r'\b(\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December) 20\d\d)', s)
            d = datetime.datetime.strptime(m.group(1), '%d %B %Y').date().isoformat() if m else None
        except Exception:
            d = None
        title = folder.replace('-', ' ').capitalize()
        _rel[url] = {'release': title, 'release_url': url, 'release_date': d, 'file_url': link}
    return dict(_rel[url])


def stats_csv(pattern, member=None):
    link = stats_link(pattern)
    b = get(link)
    if member:
        z = zipfile.ZipFile(io.BytesIO(b))
        name = [n for n in z.namelist() if re.search(member, n)][0]
        b = z.read(name)
    return list(csv.DictReader(io.StringIO(b.decode('utf-8-sig', 'replace')))), release_info(link)


def series(rows, ref, start=START):
    out = []
    for r in rows:
        if r['Series_reference'] == ref and r['Data_value'] not in ('', None):
            p = tnum(r['Period'])
            if int(p[:4]) >= start - 1:
                out.append([p, float(r['Data_value'])])
    out.sort()
    if not out:
        raise RuntimeError('empty series ' + ref)
    return out


def yoy(pts, lag=4):
    return [[pts[i][0], round((pts[i][1] / pts[i - lag][1] - 1) * 100, 2)] for i in range(lag, len(pts))]


def trim(pts):
    return [p for p in pts if int(p[0][:4]) >= START]


def build_labour():
    rows, rel = stats_csv(r'labour-market-statistics-.*\.zip', r'lms-.*tables\.csv$')
    write('unemployment', dict(title='Unemployment rate (seasonally adjusted)', unit='%', freq='quarterly',
          source='Stats NZ, Household Labour Force Survey (HLFQ.S1F3S)', **rel,
          series={'Unemployment rate': trim(series(rows, 'HLFQ.S1F3S'))}))
    lci_rows, _ = stats_csv(r'labour-market-statistics-.*\.zip', r'lci-.*\.csv$')
    qes_rows, _ = stats_csv(r'labour-market-statistics-.*\.zip', r'qes-.*\.csv$')
    lci = trim(series(lci_rows, 'LCIQ.SG53Z9AC'))  # published annual % change
    qes = trim(yoy(series(qes_rows, 'QEMQ.SAAZ9A')))
    return lci, qes, rel


def build_cpi():
    rows, rel = stats_csv(r'consumers-price-index-.*-quarter-index-numbers\.csv')
    return trim(yoy(series(rows, 'CPIQ.SE9A'))), rel


def build_wages():
    lci, qes, rel_l = build_labour()
    cpi, rel_c = build_cpi()
    cmap = dict(cpi)
    real = [[p, round(v - cmap[p], 2)] for p, v in qes if p in cmap]
    # Latest real wage uses the latest CPI (the model baseline), even when CPI is a quarter ahead of QES.
    real_note = None
    if qes and cpi and cpi[-1][0] > qes[-1][0]:
        import calendar
        mq = lambda per: calendar.month_abbr[int(per[5:7])]
        real = [r for r in real if r[0] != qes[-1][0]] + [[qes[-1][0], round(qes[-1][1] - cpi[-1][1], 2)]]
        real_note = (f'{mq(qes[-1][0])}-qtr QES less {mq(cpi[-1][0])}-qtr CPI '
                     f'({qes[-1][1]:.2f} - {cpi[-1][1]:.2f}), matching the CPI the model starts from')
    write('wages', dict(title='Wage growth vs CPI inflation (annual % change)', unit='%', freq='quarterly',
          source='Stats NZ: Labour Cost Index all salary & wage rates, annual % (LCIQ.SG53Z9AC), QES average ordinary-time hourly earnings (QEMQ.SAAZ9A), CPI all groups (CPIQ.SE9A). Annual % = same quarter previous year. Real = QES - CPI.',
          **rel_l, release2=rel_c, real_latest_note=real_note,
          series={'LCI wage rates': lci, 'QES avg hourly earnings': qes, 'CPI inflation': cpi, 'Real wage growth (QES - CPI)': real}))


def build_bop():
    rows, rel = stats_csv(r'balance-of-payments-and-international-investment-position-.*\.csv')
    m = lambda ref: [[p, round(v / 1000, 2)] for p, v in trim(series(rows, ref))]  # $m -> $b
    write('current_account', dict(title='Current account balance', unit='% of GDP', freq='quarterly (annual, year ended)',
          source='Stats NZ, Balance of payments: current account balance % GDP (BOPQ.S06AR00CABTOGDP); year-ended balance (BOPQ.S06AC200000000D)',
          **rel, series={'Current account % GDP': trim(series(rows, 'BOPQ.S06AR00CABTOGDP')),
                         'Current account, $b (yr ended)': m('BOPQ.S06AC200000000D')}))
    write('trade_balance', dict(title='Goods & services trade balance (year ended)', unit='NZ$ billion', freq='quarterly (annual, year ended)',
          source='Stats NZ, Balance of payments year-ended balances: goods & services (BOPQ.S06AC10000000D1), goods (BOPQ.S06AC3000000D11), services (BOPQ.S06AC3000000D12)',
          **rel, series={'Goods & services': m('BOPQ.S06AC10000000D1'), 'Goods': m('BOPQ.S06AC3000000D11'), 'Services': m('BOPQ.S06AC3000000D12')}))


def build_tot():
    rows, rel = stats_csv(r'overseas-trade-indexes-.*-quarter.*\.csv')
    write('terms_of_trade', dict(title='Goods terms of trade (index, June 2002 qtr = 1000)', unit='index', freq='quarterly',
          source='Stats NZ, Overseas trade indexes: goods terms of trade, all countries (OTPQ.STTZZ5); q/q % (OTPQ.STTZZ5PC)',
          **rel, series={'Goods terms of trade': trim(series(rows, 'OTPQ.STTZZ5')),
                         'Quarterly % change': trim(series(rows, 'OTPQ.STTZZ5PC')),
                         'Annual % change': trim(yoy(series(rows, 'OTPQ.STTZZ5'))),
                         'Export prices (SEA1E91)': trim(series(rows, 'OTPQ.SEA1E91')),
                         'Import prices (SIA1I91)': trim(series(rows, 'OTPQ.SIA1I91')),
                         'Import prices ex fuels (SIA1MH1)': trim(series(rows, 'OTPQ.SIA1MH1')),
                         'Petroleum import prices (SIA1LL1)': trim(series(rows, 'OTPQ.SIA1LL1'))}))


def build_gdp():
    rows, rel = stats_csv(r'^gross-domestic-product-.*-quarter\.csv$')
    s = trim(series(rows, 'SNEQ.SG09RSC00B01NZ', START - 1))
    g = trim(series(rows, 'SNEQ.SG01RSC00B01', START - 1))  # real GDP, $m s.a.
    pc = dict(s)
    nom = trim(series(rows, 'SNEA.SG09NAC00B15NZJ', START - 1))  # nominal GDP per capita, rolling annual $
    pop = [[p, round(v * 1e6 / pc[p] / 1e6, 4)] for p, v in g if p in pc]  # implied population, millions
    write('gdp_per_capita', dict(title='Real GDP per capita (production, chain-volume, seasonally adjusted, quarterly NZ$)', unit='NZ$ (2009/10 prices)', freq='quarterly',
          source='Stats NZ, GDP: per capita chain-volume seasonally adjusted (SNEQ.SG09RSC00B01NZ); total real GDP production s.a. (SNEQ.SG01RSC00B01); nominal GDP(E) per capita, rolling annual (SNEA.SG09NAC00B15NZJ). Population = GDP / GDP per capita (implied).', **rel,
          series={'Real GDP per capita': s, 'Real GDP ($m, quarterly)': g, 'Implied population (m)': pop, 'Nominal GDP per capita, year ended ($)': nom, 'q/q % change': [[s[i][0], round((s[i][1]/s[i-1][1]-1)*100, 2)] for i in range(1, len(s))]}))


def build_migration():
    rows, rel = stats_csv(r'international-migration-.*-estimated-migration-by-age-and-sex\.csv')
    m = {}
    for r in rows:
        if r['direction'] == 'Net' and r['sex'] == 'TOTAL' and r['age'] == 'TOTAL':
            m[r['year_month']] = float(r['estimate'])
    ks = sorted(m)
    ann = [[k, sum(m[x] for x in ks[i-11:i+1])] for i, k in enumerate(ks) if i >= 11]
    write('migration', dict(title='Net migration, annual (12-month rolling total)', unit='people', freq='monthly',
          source='Stats NZ, International migration: estimated net migration, all ages & sexes (12 months to each month; recent months provisional)',
          **rel, series={'Net migration (12 months)': [p for p in ann if int(p[0][:4]) >= START],
                         'Net migration (month)': [[k, m[k]] for k in ks if int(k[:4]) >= START]}))


# ---------------- RBNZ ----------------
RBNZ_PAGES = {
    'b1': 'https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/exchange-rates-and-the-trade-weighted-index',
    'b20': 'https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/new-residential-mortgage-standard-interest-rates',
    'b2': 'https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/wholesale-interest-rates',
    'c5': 'https://www.rbnz.govt.nz/statistics/series/lending-and-monetary/registered-banks-and-non-bank-lending-institutions-sector-lending',
    'm10': 'https://www.rbnz.govt.nz/statistics/series/economic-indicators/housing',
}
def rbnz_download():
    """RBNZ's site rejects scripted HTTP clients; fetch via a real browser session."""
    import asyncio
    from playwright.async_api import async_playwright
    want = {'hb1-monthly.xlsx', 'hb1-daily.xlsx', 'hb20.xlsx', 'hb2-monthly-close.xlsx', 'hb2-daily-close-1985-2017.xlsx', 'hc5.xlsx', 'hm10.xlsx'}
    got = {}
    async def run():
        async with async_playwright() as p:
            exe = '/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None
            b = await p.chromium.launch(executable_path=exe, headless=False, args=['--disable-blink-features=AutomationControlled'])
            c = await b.new_context(accept_downloads=True); pg = await c.new_page()
            for u in RBNZ_PAGES.values():
                await pg.goto(u, timeout=90000); await pg.wait_for_timeout(5000)
                links = await pg.eval_on_selector_all('a', "a=>a.map(x=>x.href)")
                for l in links:
                    n = l.split('/')[-1].split('?')[0]
                    if n in want and n not in got:
                        async with pg.expect_download(timeout=60000) as d:
                            await pg.evaluate("h=>{const a=document.createElement('a');a.href=h;document.body.appendChild(a);a.click()}", l)
                        dl = await d.value; path = os.path.join(TMP, n); await dl.save_as(path); got[n] = (path, l, u)
            await b.close()
    asyncio.run(run())
    return got


def xlsx_rows(path):
    import openpyxl
    ws = openpyxl.load_workbook(path, data_only=True)['Data']
    rows = list(ws.iter_rows(values_only=True))
    pub = None
    try:
        for r in openpyxl.load_workbook(path, data_only=True)['Table Description'].iter_rows(values_only=True):
            if r and r[0] == 'Published Date' and r[1]: pub = r[1].date().isoformat()
    except Exception:
        pass
    return rows, pub


def build_rbnz():
    got = rbnz_download()
    # FX
    pm, lm, um = got['hb1-monthly.xlsx']
    rows, pub = xlsx_rows(pm)
    ids = rows[4]; ci = {v: i for i, v in enumerate(ids)}
    twi, usd = [], []
    for r in rows[5:]:
        if isinstance(r[0], datetime.datetime) and r[0].year >= START:
            p = r[0].strftime('%Y-%m')
            if r[ci['EXRT.MS41.NZB17']] is not None: twi.append([p, r[ci['EXRT.MS41.NZB17']]])
            if r[ci['EXR.MS11.D06']] is not None: usd.append([p, round(r[ci['EXR.MS11.D06']], 4)])
    latest = None
    if 'hb1-daily.xlsx' in got:
        drows, dpub = xlsx_rows(got['hb1-daily.xlsx'][0]); di = {v: i for i, v in enumerate(drows[4])}
        last = [r for r in drows[5:] if isinstance(r[0], datetime.datetime) and r[di['EXR.DS11.D06']] is not None][-1]
        latest = {'date': last[0].date().isoformat(), 'TWI': last[di['EXRT.DS41.NZB17']], 'NZD/USD': last[di['EXR.DS11.D06']]}
    write('fx', dict(title='NZD trade-weighted index and NZD/USD (monthly average)', unit='index / USD', freq='monthly',
          source='RBNZ statistics B1: TWI-17 (EXRT.MS41.NZB17), NZD/USD (EXR.MS11.D06)', release='RBNZ B1 Exchange rates and TWI',
          release_url=um, release_date=pub, file_url=lm, latest_daily=latest, series={'TWI (17 currency)': twi, 'NZD/USD': usd}))
    # Mortgage
    p20, l20, u20 = got['hb20.xlsx']
    rows, pub = xlsx_rows(p20)
    ci = {v: i for i, v in enumerate(rows[4])}
    fl, f1 = [], []
    for r in rows[5:]:
        if isinstance(r[0], datetime.datetime) and r[0].year >= START:
            p = r[0].strftime('%Y-%m')
            if r[ci['MTGE.MBI.F']] is not None: fl.append([p, r[ci['MTGE.MBI.F']]])
            if r[ci['MTGE.MBI.T09']] is not None: f1.append([p, r[ci['MTGE.MBI.T09']]])
    write('mortgage', dict(title='New residential mortgage standard rates (end of month)', unit='% p.a.', freq='monthly',
          source='RBNZ statistics B20: floating (MTGE.MBI.F), 1-year fixed (MTGE.MBI.T09); carded standard rates, excl. specials',
          release='RBNZ B20 New residential mortgage standard interest rates', release_url=u20, release_date=pub, file_url=l20,
          series={'Floating': fl, '1-year fixed': f1}))
    # OCR, housing credit, house prices
    def cols(name, ids):
        p, l, u = got[name]; rows, pub = xlsx_rows(p); ci = {v: i for i, v in enumerate(rows[4])}
        out = {k: [] for k in ids}
        for r in rows[5:]:
            if isinstance(r[0], datetime.datetime) and r[0].year >= START - 1:
                for k in ids:
                    if r[ci[k]] is not None: out[k].append([r[0].strftime('%Y-%m'), r[ci[k]]])
        return out, pub, l, u
    o, pub, l, u = cols('hb2-monthly-close.xlsx', ['INM.MP1.N.nae'])
    ocr = trim(o['INM.MP1.N.nae'])
    if 'hb2-daily-close-1985-2017.xlsx' in got:  # monthly file starts 2018; month-end OCR from the historical daily file
        rows, _ = xlsx_rows(got['hb2-daily-close-1985-2017.xlsx'][0])
        ci = [i for i, v in enumerate(rows[4]) if str(v).startswith('INM.DP1')][0]
        me = {}
        for r in rows[5:]:
            if isinstance(r[0], datetime.datetime) and r[0].year >= START and r[ci] is not None: me[r[0].strftime('%Y-%m')] = r[ci]
        have = {p for p, _ in ocr}
        ocr = sorted([[p, v] for p, v in me.items() if p not in have] + ocr)
    write('ocr', dict(title='Official Cash Rate (month end)', unit='% p.a.', freq='monthly', source='RBNZ statistics B2: Official Cash Rate (INM.MP1.N.nae)',
          release='RBNZ B2 Wholesale interest rates', release_url=u, release_date=pub, file_url=l, series={'OCR': ocr}))
    o, pub, l, u = cols('hc5.xlsx', ['CRDS.MALP1', 'CRDS.MALP1.ay'])
    write('housing_credit', dict(title='Housing lending by banks and NBLIs (household mortgage debt)', unit='NZ$ billion / annual %', freq='monthly',
          source='RBNZ statistics C5 Sector lending: housing lending total (CRDS.MALP1, $m) and break-adjusted annual growth (CRDS.MALP1.ay)',
          release='RBNZ C5 Sector lending (registered banks and NBLIs)', release_url=u, release_date=pub, file_url=l,
          series={'Housing lending ($b)': trim([[p, round(v / 1000, 2)] for p, v in o['CRDS.MALP1']]), 'Annual growth (%)': trim(o['CRDS.MALP1.ay'])}))
    o, pub, l, u = cols('hm10.xlsx', ['HPI.Q.H01T0.ia'])
    h = o['HPI.Q.H01T0.ia']
    write('house_prices', dict(title='House price index (CoreLogic, via RBNZ M10)', unit='index', freq='quarterly',
          source='RBNZ statistics M10 Housing: house price index (HPI.Q.H01T0.ia), source CoreLogic', release='RBNZ M10 Housing',
          release_url=u, release_date=pub, file_url=l, series={'House price index': trim(h), 'Annual % change': trim(yoy(h))}))


# ---------------- Immigration NZ ----------------
INZ_PDF = 'https://www.immigration.govt.nz/assets/inz/documents/statistics/statistics-work-applications-decided.pdf'
def build_visas():
    pdf = os.path.join(TMP, 'wad.pdf'); open(pdf, 'wb').write(get(INZ_PDF))
    txt = subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True, text=True).stdout.splitlines()
    prepared = None
    for l in txt[:40]:
        m = re.search(r'Report prepared:\s*(\d{1,2} \w+ \d{4})', l)
        if m: prepared = datetime.datetime.strptime(m.group(1), '%d %B %Y').date().isoformat(); break
    num = lambda s: int(s.replace(',', ''))
    # First table = applications. Financial-year Total rows: approved is every 3rd number.
    fy, fy_labels, i = [], [], 0
    totals = [k for k, l in enumerate(txt) if l.startswith('Total')]
    for k in totals[:2]:
        labs = []
        for j in range(k - 1, 0, -1):
            f = re.findall(r'\b(20\d\d/\d\d)\b', txt[j])
            if len(f) >= 2 and 'Data for period' not in txt[j]:
                labs = f; break
        nums = [num(x) for x in re.findall(r'[\d,]+', txt[k][5:])]
        for n, lab in enumerate(labs):
            fy.append([lab, nums[3 * n]])
    # Monthly (current financial year), applications table
    mon = []
    for k in totals:
        labs = None
        for j in range(k - 1, max(0, k - 140), -1):
            f = re.findall(r'\b(20\d\d-\d\d)\b', txt[j])
            if len(f) >= 1 and 'Data for period' not in txt[j]:
                labs = f; break
            if txt[j].startswith('Total'): break
        if labs:
            nums = [num(x) for x in re.findall(r'[\d,]+', txt[k][5:])]
            mon = [[lab, nums[3 * n]] for n, lab in enumerate(labs)]
            break
    if not fy: raise RuntimeError('INZ parse failed')
    write('work_visas', dict(title='Work visa applications approved', unit='applications', freq='annual (Jul-Jun) + monthly for current year',
          source='Immigration NZ statistics pack "Work applications decided" (applications approved, all criteria)',
          release='INZ: Work applications decided', release_url='https://www.immigration.govt.nz/about-us/research-and-statistics/statistics/',
          release_date=prepared, file_url=INZ_PDF,
          series={'Approved, financial year': fy, 'Approved, month (current FY)': mon},
          note='Monthly figures are only published for the current financial year; 2015/16 and earlier are not in this pack. Latest FY is partial.'))


STEPS = [('migration', build_migration), ('wages+unemployment', build_wages), ('bop', build_bop), ('terms_of_trade', build_tot),
         ('gdp_per_capita', build_gdp), ('rbnz', build_rbnz), ('work_visas', build_visas)]

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]
    failed = []
    for name, fn in STEPS:
        if only and name not in only: continue
        try:
            fn(); print('ok  ', name)
        except Exception as e:
            failed.append({'step': name, 'error': str(e)[:300]}); print('FAIL', name, e)
    meta_p = os.path.join(OUT, 'meta.json')
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    meta.update({'built': TODAY, 'failed_last_run': failed,
                 'gaps': ['Work-visa approvals: monthly history before the current financial year and anything before 2016/17 are not in the INZ statistics pack (the Migration Data Explorer is an interactive app with no stable file URL).']})
    json.dump(meta, open(meta_p, 'w'), indent=1)
    sys.exit(1 if failed else 0)
