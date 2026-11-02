// NZ Economy Explorer: data loading, linked annual model, charts. No backend.
const IDS=['migration','unemployment','wages','work_visas','current_account','trade_balance','terms_of_trade','fx','gdp_per_capita','mortgage','ocr','housing_credit','house_prices','meta'];
const END=2031.0,D={};
const t=p=>{const[y,m]=p.split('-').map(Number);return y+(m-0.5)/12};
const last=a=>a[a.length-1];
const fmt=(v,d=1)=>v==null||isNaN(v)?'–':(+v).toLocaleString('en-NZ',{minimumFractionDigits:d,maximumFractionDigits:d});
const sg=(v,d=1)=>(v>0?'+':v<0?'−':'')+fmt(Math.abs(v),d);
const money=(v,d)=>(v<0?'−':'')+'$'+fmt(Math.abs(v),d)+'b';
const C={k:'#111',b:'#2f6fb5',r:'#c0392b',g:'#2e8b57',o:'#d98c1f',p:'#7b3fc4'};
const xy=pts=>pts.map(p=>({x:t(p[0]),y:p[1]}));
const at=(s,p)=>{const f=s.find(q=>q[0]==p);return f?f[1]:null};
const yoy=(s,lag)=>s.slice(lag).map((p,i)=>[p[0],(p[1]/s[i][1]-1)*100]);

// ---------- Drivers ----------
const DRV=[["mig","Net migration (people/yr)",null,-40000,140000,2500,"",0],
 ["ocr","OCR",null,0.25,7,0.25,"%",2],
 ["prod","Productivity trend, real GDP per head",0.8,-1,6,0.1,"%/yr",1,"default = 2016–25 average"],
 ["ai","Investment in automation & AI",3.8,0,8,0.1,"% GDP",1,'default 3.8% = NZ ICT investment share, 2017 (<a href="https://www.oecd.org/content/dam/oecd/en/publications/reports/2019/04/ict-investments-in-oecd-countries-and-partner-economies_cd7935de/bcb82cff-en.pdf">OECD 2019</a>)'],
 ["tot","Terms of trade change",null,-8,8,0.5,"%/yr",1,null]];
// ---------- Elasticities ----------
// [id,label,value,min,max,step,source/method,confidence]
const AN13='<a href="https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/publications/analytical-notes/2013/an2013-10.pdf">RBNZ Analytical Note AN2013/10, "Migration and the housing market"</a>';
const CLL='<a href="https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/publications/discussion-papers/2007/dp07-12.pdf">Coleman &amp; Landon-Lane (2007), RBNZ DP2007/12</a>';
const EL=[
["ePop","Population growth per 1% of population net migration",1.05,0.5,1.5,0.05,"Estimated from 2015–26 data: regression of annual population growth on net migration/population, 2016–25 (R² 0.89). The intercept, 0.44%, is natural increase.","high"],
["nat","Natural increase (% of population per year)",0.44,0,1,0.02,"Estimated from 2015–26 data (intercept of the regression above).","high"],
["eHm","House prices, % per 1% of population migration above the 2016–25 average (0.9%)",8,0,15,0.5,"Published: "+AN13+" finds a 1%-of-population inflow raises real house prices about 8% (over about 3 years). "+CLL+" find 8–12% after one year. The 2015–26 annual data alone show no stable link (R² 0.07), because the 2020–21 boom came with zero migration.","medium"],
["eHo","House prices, % per 1pp OCR above 3%",-3.95,-8,0,0.05,"Estimated from 2015–26 data: house-price growth on migration rate and OCR, 2016–25 (R² 0.40).","medium"],
["h0","Baseline house-price growth at average migration and 3% OCR (%/yr)",3,-2,6,0.25,"Estimated from 2015–26 data: the fitted value of the same regression at a 3% OCR (3.1%).","low"],
["cH","Mortgage-credit growth per 1% house-price growth",0.137,0,0.4,0.01,"Estimated from 2015–26 data: C5 housing lending growth (Dec) = 7.05 + 0.137×HPI growth − 0.60×OCR, 2016–25 (R² 0.90).","high"],
["cO","Mortgage-credit growth per 1pp OCR",-0.60,-1.5,0,0.05,"Estimated from 2015–26 data (same regression).","high"],
["c0","Mortgage-credit growth intercept (%)",7.05,4,10,0.05,"Estimated from 2015–26 data (same regression).","high"],
["cP","Mortgage-credit growth per 1pp population growth above 1.4%",1.0,-0.5,2,0.05,"Assumption: new households borrow at about the average debt per head. The 2015–26 regression actually gives −0.3 (credit on migration and OCR, R² 0.68), because migration and credit booms did not coincide in this window.","low"],
["eAI","Productivity growth, pp per 1% of GDP of automation/AI investment above 3.8%",0.15,0,0.6,0.01,"Assumption, from growth accounting: extra output growth ≈ net return on the capital × extra investment/GDP, with a net return on ICT/AI capital of about 15%. I did not use a published NZ estimate, because I didn't find one. The baseline 3.8% of GDP is NZ's ICT investment share (OECD 2019 report, 2017 data). AI-specific investment is not separately measured.","low"],
["eY","Demand impulse (% of GDP) per 1pp productivity growth above 0.8%",0.5,0,1,0.05,"Assumption: higher productivity raises real incomes and wages. Households and firms spend part of the expected gain ahead of the extra supply, the permanent-income effect, so demand runs above potential and unemployment falls through the Okun link. I have no published NZ estimate for this.","low"],
["mInv","Import share of automation/AI investment spending",0.5,0,1,0.05,"Assumption: much ICT and automation equipment is imported. I did not find a published Stats NZ import share of ICT investment, so I haven't cited one.","low"],
["dil","Capital dilution: productivity per head lost per 1pp population growth above 1.4%",0.3,0,1,0.05,"Assumption (Solow-style capital dilution with a capital share of about 0.3). The 2015–26 data do not show it: the slope of GDP-per-head growth on population growth is +0.13 (R² 0.01, excl. 2020–21).","low"],
["psi","Demand impulse (% of GDP) per 1pp population growth above 1.4%",0.8,0,2,0.1,"Published: "+AN13+": a 1%-of-population migration shock raises the output gap by about 0.8% at its peak.","medium"],
["lam","Share of excess mortgage borrowing (debt growth above nominal GDP) that is spent",0.5,0,1,0.05,"Assumption.","low"],
["mImp","Import share of extra spending",0.25,0.1,0.4,0.01,"Your framing: households spend about 25% of income on imports. This is close to imports' share of NZ GDP (Stats NZ BoP), but I have not checked it against a published input-output table.","medium"],
["caR","Current-account mean reversion per year",0.2,0,0.6,0.05,"Assumption (reflects the NZD and other adjustment).","low"],
["caS","Long-run current account (% of GDP)",-4.0,-7,-1,0.1,"Estimated from 2015–26 data (average 2015–26 is about −4%).","medium"],
["caT","Current account, pp of GDP per 1% terms-of-trade gain",0.2,0,0.5,0.01,"Assumption (goods exports are about 20% of GDP). The 2015–26 data give +0.21 jointly with credit (weak, R² 0.37).","low"],
["okun","Okun: unemployment pp per 1% demand above potential",-0.25,-0.6,0,0.01,"Estimated from 2015–26 data: annual change in unemployment on real GDP growth, 2016–25 excl. 2020–21 (slope −0.25, R² 0.45).","medium"],
["fxR","NZD TWI %, per 1pp OCR change",2,0,5,0.25,"Assumption. The 2015–26 annual data show no stable TWI link to the OCR or ToT (R² ≤ 0.05).","low"],
["fxT","NZD TWI %, per 1% terms-of-trade change",0.5,0,1.5,0.05,"Assumption (as above).","low"],
["fxC","NZD TWI %/yr, per 1pp current account below its long-run level",0.5,0,2,0.1,"Assumption: wider deficits weaken the NZD.","low"],
["pt","Import-price pass-through from the NZD",0.7,0,1,0.05,"Assumption (partial pass-through within a year).","low"],
["rho","CPI persistence (weight on last year's inflation)",0.75,0,0.95,0.05,"Assumption. The RBNZ's Monetary Policy Statement, September 2026 (finalised 2 September 2026), (Table 6.1) projects annual CPI of 2.4% in Sep 2027 and 2.0% in Sep 2028 and Sep 2029. The actual figure for Sep 2026 was 3.7%. At 0.75 the model gives about 3.2% (2027) and 2.8% (2028), slower than the RBNZ path, which rho ≈ 0.5 roughly reproduces (2.6%, 2.1%). The default leans towards slower disinflation than the RBNZ expects.","low"],
["phi","CPI pp per 1pp unemployment below 4.5%",0.3,0,1,0.05,"Assumption (Phillips curve; the 4.5% level is my assumption, not an RBNZ figure).","low"],
["om","Wage growth pp per 1pp unemployment above 4.5%",0.5,0,1.5,0.05,"Assumption (wage Phillips curve). Note that 2015–26 real wages rose with population growth (+1.08 slope, R² 0.41), not against it.","low"],
["hh","People per additional dwelling",2.5,1.5,6,0.1,"Published: "+AN13+" (NZ has about 2.5 people per household; it found one new house per about six migrants in the short run).","medium"]];
const V={},DEF={},E={},EDEF={};

// ---------- Base state from data ----------
let B;
function base(){const G=D.gdp_per_capita.series,pop=G['Implied population (m)'],nom=G['Nominal GDP per capita, year ended ($)'];
 const hc=D.housing_credit.series,nl=last(nom),pl=pop.find(p=>p[0]==nl[0])||last(pop);
 const debtGDP=at(hc['Housing lending ($b)'],nl[0])/(nl[1]*pl[1]/1000)*100;
 const W=D.wages.series;
 B={pop:last(pop),debt:debtGDP,u:last(D.unemployment.series['Unemployment rate'])[1],ca:last(D.current_account.series['Current account % GDP'])[1],
  ocr:last(D.ocr.series.OCR)[1],cpi:last(W['CPI inflation'])[1],c:last(hc['Annual growth (%)'])[1],h:last(D.house_prices.series['Annual % change'])[1],
  ng:(last(nom)[1]/nom[nom.length-2][1]-1)*100+(pop.length>4?(last(pop)[1]/pop[pop.length-5][1]-1)*100:0)}}

// ---------- The model ----------
// One step per year, k = 1..6. All rates are in % (annual). Levels compound from each series' latest value.
function model(){const K=6,o=[];let s={pop:B.pop[1],debt:B.debt,u:B.u,ca:B.ca,ocrPrev:B.ocr,cpi:B.cpi,ng:B.ng};
 const pbar=1.4,mbar=0.9,ustar=4.5;
 for(let k=1;k<=K;k++){
  const mr=V.mig/(s.pop*1e6)*100;                       // migration, % of population
  const pg=E.nat+E.ePop*mr;                              // population growth
  const lp=V.prod+E.eAI*(V.ai-3.8)-E.dil*(pg-pbar);                       // productivity per head (potential)
  const gp=pg+lp;                                        // potential GDP growth
  const h=E.h0+E.eHm*(mr-mbar)+E.eHo*(V.ocr-3);          // house prices
  const c=E.c0+E.cH*h+E.cO*V.ocr+E.cP*(pg-pbar);                        // mortgage-credit growth
  const ngRef=pg+0.8+s.cpi;                              // nominal income growth at baseline productivity (0.8%)
  const exD=(c-ngRef)/100*s.debt;                        // borrowing above baseline income growth, % of GDP
  const XY=E.eY*(lp-0.8);                                // income/wage channel: productivity gains lift consumption demand
  const XI=k==1?(V.ai-3.8):0;                            // automation/AI investment spending (level step, felt in year 1)
  const X=E.lam*exD+E.psi*(pg-pbar)+0.1*V.tot+XY;        // domestic demand impulse, % of GDP
  const g=gp+(1-E.mImp)*X+(1-E.mInv)*XI;                 // real GDP growth
  const ca=s.ca+E.caR*(E.caS-s.ca)-E.mImp*X-E.mInv*XI+E.caT*V.tot; // current account % GDP
  const du=E.okun*(g-gp);const u=Math.max(2,s.u+du);     // unemployment
  const twi=E.fxR*(V.ocr-s.ocrPrev)+E.fxT*V.tot+E.fxC*(ca-E.caS); // NZD TWI % change
  const imp=2-E.pt*twi;                                  // import prices (2% foreign inflation)
  const cpi=E.rho*s.cpi+(1-E.rho)*(2+E.mImp*(imp-2)+E.phi*(ustar-u)); // CPI (persistence rho)
  const w=2+lp-E.om*(u-ustar);const rw=w-cpi;            // wages, real wages
  const ng=g+cpi;const debt=s.debt*(1+c/100)/(1+ng/100);
  const r={k,mr,pg,lp,gp,h,c,exD,X,g,gpc:g-pg,ca,du,u,twi,imp,cpi,w,rw,ng,debt,ddebt:debt-s.debt,pop:s.pop*(1+pg/100),dwell:s.pop*1e6*pg/100/E.hh};
  o.push(r);s={pop:r.pop,debt,u,ca,ocrPrev:V.ocr,cpi,ng}}
 return o}

// ---------- Charts ----------
const shade={id:'shade',beforeDraw(ch){const s=ch.options.plugins.shade;if(!s)return;const{ctx,chartArea:a,scales:{x}}=ch;const x0=Math.max(a.left,x.getPixelForValue(s.from));ctx.save();ctx.fillStyle='rgba(123,63,196,.07)';ctx.fillRect(x0,a.top,a.right-x0,a.bottom-a.top);ctx.restore()}};
Chart.register(shade);
function ds(label,data,color,proj,extra={}){return Object.assign({label,data,borderColor:color,backgroundColor:color,borderWidth:proj?1.8:2,pointRadius:proj?(c=>c.raw&&c.raw.a?2:0):0,borderDash:proj?[6,4]:[],tension:0,spanGaps:true},extra)}
const CH={};
function mk(id,yLab,y2){const c=new Chart(document.getElementById(id),{type:'line',data:{datasets:[]},options:{responsive:true,maintainAspectRatio:false,animation:false,interaction:{mode:'nearest',intersect:false,axis:'x'},
 plugins:{legend:{labels:{boxWidth:12,font:{size:10}}},shade:{from:2100},tooltip:{callbacks:{label:i=>i.dataset.label+': '+fmt(i.parsed.y,Math.abs(i.parsed.y)>=100?0:2)}}},
 scales:Object.assign({x:{type:'linear',min:2015,max:END,ticks:{stepSize:1,callback:v=>Number.isInteger(v)&&v<2031&&(v%2==1)?"'"+String(v).slice(2):'',font:{size:10},maxRotation:0,autoSkip:false},grid:{color:'#f0f0f0'}},y:{title:{display:!!yLab,text:yLab,font:{size:10}},ticks:{font:{size:10}},grid:{color:'#f0f0f0'}}},y2?{y2:{position:'right',title:{display:true,text:y2,font:{size:10}},ticks:{font:{size:10}},grid:{display:false}}}:{})}});CH[id]=c}
// projection helpers: rate path (model value each year) and level path (compound from last datum)
// Smooth bridge: cubic Hermite through the latest actual and the annual model points, sampled quarterly.
// Start tangent blends the recent historical slope with the first projected step, so there is no sharp vertex at the join.
function hslope(s){const n=s.length;if(n<3)return 0;const a=s[n-1],b=s[n-3];const dt=t(a[0])-t(b[0]);return dt>0?(a[1]-b[1])/dt:0}
function smooth(P,m0){if(P.length<2)return P;const n=P.length,m=P.map((p,i)=>i==0?m0:i==n-1?(P[i].y-P[i-1].y)/(P[i].x-P[i-1].x):(P[i+1].y-P[i-1].y)/(P[i+1].x-P[i-1].x));
 const o=[{x:P[0].x,y:P[0].y}];for(let i=0;i<n-1;i++){const h=P[i+1].x-P[i].x;for(let q=1;q<=4;q++){const u=q/4,h00=2*u**3-3*u*u+1,h10=u**3-2*u*u+u,h01=-2*u**3+3*u*u,h11=u**3-u*u;
  o.push({x:P[i].x+u*h,y:h00*P[i].y+h10*h*m[i]+h01*P[i+1].y+h11*h*m[i+1],a:q==4})}}return o}
function bridge(s,P){const seg=P.length>1?(P[1].y-P[0].y)/(P[1].x-P[0].x):0;return smooth(P,0.5*hslope(s)+0.5*seg)}
function pr(s,M,f){const x0=t(last(s)[0]);const o=[{x:x0,y:last(s)[1]}];M.forEach(r=>{if(x0+r.k<=END+0.01)o.push({x:x0+r.k,y:f(r)})});return bridge(s,o)}
function pl(s,M,f){const x0=t(last(s)[0]);let v=last(s)[1];const o=[{x:x0,y:v}];M.forEach(r=>{v*=1+f(r)/100;if(x0+r.k<=END+0.01)o.push({x:x0+r.k,y:v})});return bridge(s,o)}
function cite(d){const r=d.release_date?new Date(d.release_date+'T00:00').toLocaleDateString('en-NZ',{day:'numeric',month:'short',year:'numeric'}):'n/a';
 let s=`Source: ${d.source}. Release: <a href="${d.release_url}">${d.release}</a>, ${r}`;
 if(d.release2){const r2=new Date(d.release2.release_date+'T00:00').toLocaleDateString('en-NZ',{day:'numeric',month:'short',year:'numeric'});s+=`; <a href="${d.release2.release_url}">${d.release2.release}</a>, ${r2}`}
 return s+'. Data: <a href="'+d.file_url+'">file</a>.'}
function debtHist(){const G=D.gdp_per_capita.series,hc=D.housing_credit.series['Housing lending ($b)'];
 return G['Nominal GDP per capita, year ended ($)'].map(([p,v])=>{const c=at(hc,p),pp=at(G['Implied population (m)'],p);return c&&pp?[p,c/(v*pp/1000)*100]:null}).filter(Boolean)}
function popYoy(){return yoy(D.gdp_per_capita.series['Implied population (m)'],4)}
const CHARTS=[
 ['c_mig','Net migration, 12-month total (people)','people',['migration'],M=>{const s=D.migration.series['Net migration (12 months)'];return[ds('Net migration',xy(s),C.b),ds('Scenario',pr(s,M,()=>V.mig),C.b,1)]}],
 ['c_debt','Mortgage debt (% of GDP, left) and house prices (index, right)','% GDP',['housing_credit','house_prices'],M=>{const s=debtHist(),h=D.house_prices.series['House price index'];return[ds('Mortgage debt / GDP',xy(s),C.r),ds('House prices',xy(h),C.grey||'#999',0,{yAxisID:'y2',borderWidth:1.2}),ds('Debt scenario',pr(s,M,r=>r.debt),C.r,1),ds('HPI scenario',pl(h,M,r=>r.h),'#999',1,{yAxisID:'y2'})]},'HPI'],
 ['c_gpc','Real GDP per head (quarterly, chain-volume NZ$)','NZ$',['gdp_per_capita'],M=>{const s=D.gdp_per_capita.series['Real GDP per capita'];return[ds('Real GDP per head',xy(s),C.g),ds('Scenario',pl(s,M,r=>r.gpc),C.g,1)]}],
 ['c_ca','Current account balance (% of GDP)','% GDP',['current_account'],M=>{const s=D.current_account.series['Current account % GDP'];return[ds('Current account',xy(s),C.k),ds('Scenario',pr(s,M,r=>r.ca),C.k,1)]}],
 ['c_un','Unemployment rate (%)','%',['unemployment'],M=>{const s=D.unemployment.series['Unemployment rate'];return[ds('Unemployment',xy(s),C.r),ds('Scenario',pr(s,M,r=>r.u),C.r,1)]}],
 ['c_rw','Wages vs CPI (annual %)','%',['wages'],M=>{const W=D.wages.series,w=W['QES avg hourly earnings'],c=W['CPI inflation'],r=W['Real wage growth (QES - CPI)'];return[ds('Wages (QES)',xy(w),C.b),ds('CPI',xy(c),C.o),ds('Real wage growth',xy(r),C.k,0,{borderWidth:2.5}),ds('Wages scen.',pr(w,M,q=>q.w),C.b,1),ds('CPI scen.',pr(c,M,q=>q.cpi),C.o,1),ds('Real scen.',pr(r,M,q=>q.rw),C.k,1)]},null,'wide']];
// ---------- Annual history (June years) ----------
function hist(){const J=(s,y)=>at(s,y+'-06');const dh=debtHist();const out=[];
 for(let y=2016;y<=2026;y++){const d=J(dh,y),d0=J(dh,y-1),u=J(D.unemployment.series['Unemployment rate'],y),u0=J(D.unemployment.series['Unemployment rate'],y-1);
  const P=D.gdp_per_capita.series['Implied population (m)'];
  if(d==null||u==null)continue;out.push({y,ca:J(D.current_account.series['Current account % GDP'],y),debt:d,ddebt:d-d0,du:u-u0,u,
   mig:J(D.migration.series['Net migration (12 months)'],y),mr:J(D.migration.series['Net migration (12 months)'],y)/(J(P,y-1)*1e6)*100,c:J(D.housing_credit.series['Annual growth (%)'],y),h:J(D.house_prices.series['Annual % change'],y)})}
 return out}
function verdict(dd,du,ca){if(dd>=0.5&&du<0.2)return['1: debt','vd'];if(dd<0.5&&du>=0.2)return['2: unemp.','vu'];if(dd>=0.5&&du>=0.2)return['Both','vb'];return['Neither','vc']}
function corr(a,b){const n=a.length,ma=a.reduce((x,y)=>x+y)/n,mb=b.reduce((x,y)=>x+y)/n;let s=0,sa=0,sb=0;for(let i=0;i<n;i++){s+=(a[i]-ma)*(b[i]-mb);sa+=(a[i]-ma)**2;sb+=(b[i]-mb)**2}return s/Math.sqrt(sa*sb)}

// ---------- Render ----------
function render(){const M=model();
 for(const[id,,,,fn]of CHARTS){const c=CH[id];c.data.datasets=fn(M);const p=c.data.datasets.find(x=>x.borderDash.length);c.options.plugins.shade.from=p?p.data[0].x:2100;c.update()}
 const y0=Math.floor(t(last(D.unemployment.series['Unemployment rate'])[0]));
 // adjustment (model)
 document.getElementById('adjm').innerHTML='<tr><th>Year</th><th>CA</th><th>Δ debt</th><th>Δ unemp.</th><th>Path</th></tr>'+M.slice(0,4).map(r=>{const v=verdict(r.ddebt,r.du,r.ca);return`<tr><td>${y0+r.k}</td><td>${fmt(r.ca)}</td><td>${sg(r.ddebt)}</td><td>${sg(r.du,2)}</td><td class="verdict ${v[1]}">${v[0]}</td></tr>`}).join('');
 const L=M[3];const cum=M.slice(0,4).reduce((a,r)=>[a[0]+r.ddebt,a[1]+r.du],[0,0]);
 document.getElementById('adjtxt').innerHTML=`By ${y0+4}: current account <b>${fmt(L.ca)}% of GDP</b>, mortgage debt/GDP <b>${sg(cum[0])}pp</b> to ${fmt(L.debt,0)}%, unemployment <b>${sg(cum[1])}pp</b> to ${fmt(L.u)}%. `+
  (cum[0]>2&&cum[1]<0.5?'In this scenario the identity balances mainly through <b>path 1, more household debt</b>.':cum[1]>=0.5&&cum[0]<2?'In this scenario the identity balances mainly through <b>path 2, higher saving and unemployment</b>.':cum[0]>2&&cum[1]>=0.5?'In this scenario <b>both paths</b> operate: debt and unemployment both rise.':'In this scenario the deficit narrows <b>without much of either path</b>, through the model’s NZD and mean-reversion terms.');
 for(const d of DRV){const v=V[d[0]];document.getElementById('o_'+d[0]).textContent=(d[0]=='mig'?fmt(v,0):fmt(v,d[7]))+(d[6]?' '+d[6]:'')}
 for(const e of EL){document.getElementById('oe_'+e[0]).textContent=fmt(E[e[0]],e[5]<0.1?2:e[5]<1?1:0)}}

function slider(box,id,lab,v,mn,mx,st,hint,store){box.insertAdjacentHTML('beforeend',`<div class="dial"><label for="i_${id}"><span>${lab}</span><b id="o_${id}"></b></label><input type="range" id="i_${id}" min="${mn}" max="${mx}" step="${st}" value="${v}">${hint?`<small>${hint}</small>`:''}</div>`);
 document.getElementById('i_'+id).addEventListener('input',e=>{store[id.replace(/^e_/,'')]=+e.target.value;render()})}
function buildControls(){const T=D.terms_of_trade,TS=T.series,tL=last(TS['Goods terms of trade']),tQ=last(TS['Quarterly % change']),TA=TS['Annual % change'],tY=last(TA),tY2=TA[TA.length-2];
 // ToT default: average of the y/y % changes of the latest two quarters, rounded to the 0.5 step and clamped to the slider range.
 const tAvg=(tY[1]+tY2[1])/2,totDef=Math.min(8,Math.max(-8,Math.round(tAvg/0.5)*0.5));
 const qn=p=>['Mar','Jun','Sep','Dec'][Math.floor((+p.slice(5,7)-1)/3)]+' '+p.slice(0,4)+' qtr';
 const rd=(([y,m,d])=>+d+' '+'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ')[m-1]+' '+y)(T.release_date.split('-'));
 const totNote=`default = 2-quarter average of goods ToT annual changes (${qn(tY2[0])} ${sg(tY2[1])}% y/y, ${qn(tY[0])} ${sg(tY[1])}% y/y → ${sg(tAvg,2)}%), rounded to the 0.5 step and clamped to ±8.<br><b>Latest goods ToT: ${qn(tL[0])} ${fmt(tL[1])}, ${sg(tQ[1])}% q/q, ${sg(tY[1])}% y/y</b> (provisional, <a href="${T.release_url}">Stats NZ</a>, released ${rd})`;
 const dyn={mig:Math.round(last(D.migration.series['Net migration (12 months)'])[1]/2500)*2500,ocr:B.ocr,tot:totDef},dynNote={tot:totNote};
 const box=document.getElementById('drv');
 for(const d of DRV){const v=d[2]==null?dyn[d[0]]:d[2];DEF[d[0]]=V[d[0]]=v;slider(box,d[0],d[1],v,d[3],d[4],d[5],d[8]||dynNote[d[0]]||'default = latest published value',V)}
 const a=document.getElementById('asm');
 for(const e of EL){EDEF[e[0]]=E[e[0]]=e[2];a.insertAdjacentHTML('beforeend',`<div class="el"><div class="dial" style="margin:0"><label for="i_e_${e[0]}"><span>${e[1]} <span class="conf ${e[7]}">${e[7]}</span></span><b id="oe_${e[0]}"></b></label><input type="range" id="i_e_${e[0]}" min="${e[3]}" max="${e[4]}" step="${e[5]}" value="${e[2]}"></div><small>${e[6]}</small></div>`);
  document.getElementById('i_e_'+e[0]).addEventListener('input',ev=>{E[e[0]]=+ev.target.value;render()})}
 document.getElementById('eqs').innerHTML=`<p>m = net migration ÷ population (%). Population growth pg = nat + ePop·m. Productivity per head lp = trend + eAI·(AI investment − 3.8) − dil·(pg − 1.4). Potential growth = pg + lp.<br>
House prices h = h0 + eHm·(m − 0.9) + eHo·(OCR − 3). Mortgage credit c = c0 + cH·h + cO·OCR + cP·(pg − 1.4). Excess borrowing = (c − baseline nominal income growth [pg + 0.8 + CPI₋₁]) × debt/GDP.<br>
Demand impulse X = lam·excess borrowing + psi·(pg − 1.4) + 0.1·ToT + eY·(lp − 0.8). Investment impulse XI = AI investment − 3.8 (year 1). GDP growth = potential + (1 − mImp)·X + (1 − mInv)·XI.<br>
Current account CA = CA₋₁ + caR·(caS − CA₋₁) − mImp·X − mInv·XI + caT·ToT. Unemployment Δu = okun·(GDP − potential).<br>
TWI % = fxR·ΔOCR + fxT·ToT + fxC·(CA − caS). Import prices = 2 − pt·TWI%. CPI = rho·CPI₋₁ + (1 − rho)·(2 + mImp·(import prices − 2) + phi·(4.5 − u)). Projection lines are drawn as a smooth cubic (Hermite) bridge from the latest actual through the annual model points, sampled quarterly.<br>
Wages = 2 + lp − om·(u − 4.5). Real wages = wages − CPI. Debt/GDP grows by (1 + c)/(1 + nominal GDP growth).</p>`}

function snapshot(){const r=[];const L=(k,s)=>last(D[k].series[s]);const fx=D.fx.latest_daily;const dh=last(debtHist());
 r.push(['Net migration, 12 months to',L('migration','Net migration (12 months)')[0],fmt(L('migration','Net migration (12 months)')[1],0),D.migration]);
 r.push(['Unemployment rate (s.a.)',L('unemployment','Unemployment rate')[0]+' qtr',fmt(L('unemployment','Unemployment rate')[1])+'%',D.unemployment]);
 r.push(['QES avg hourly earnings, annual',L('wages','QES avg hourly earnings')[0]+' qtr',sg(L('wages','QES avg hourly earnings')[1])+'%',D.wages]);
 r.push(['CPI inflation, annual',L('wages','CPI inflation')[0]+' qtr',fmt(L('wages','CPI inflation')[1])+'%',Object.assign({},D.wages,D.wages.release2)]);
 r.push(['Real wage growth (QES − CPI), annual',D.wages.real_latest_note||(L('wages','Real wage growth (QES - CPI)')[0]+' qtr'),sg(L('wages','Real wage growth (QES - CPI)')[1],2)+'pp',D.wages]);
 r.push(['Housing lending (C5), annual growth',L('housing_credit','Annual growth (%)')[0],money(L('housing_credit','Housing lending ($b)')[1],1)+', '+sg(L('housing_credit','Annual growth (%)')[1])+'%',D.housing_credit]);
 r.push(['Mortgage debt / nominal GDP',dh[0]+' (yr)',fmt(dh[1])+'%',D.housing_credit]);
 r.push(['House prices (CoreLogic HPI), annual',L('house_prices','Annual % change')[0]+' qtr',sg(L('house_prices','Annual % change')[1])+'%',D.house_prices]);
 r.push(['Current account, year ended',L('current_account','Current account % GDP')[0]+' qtr',money(L('current_account','Current account, $b (yr ended)')[1],1)+' ('+fmt(L('current_account','Current account % GDP')[1])+'% GDP)',D.current_account]);
 r.push(['Goods & services balance, year ended',L('trade_balance','Goods & services')[0]+' qtr',money(L('trade_balance','Goods & services')[1],2),D.trade_balance]);
 r.push(['OCR',L('ocr','OCR')[0],fmt(L('ocr','OCR')[1],2)+'%',D.ocr]);
 r.push(['Mortgage: floating / 1-yr fixed',L('mortgage','Floating')[0],fmt(L('mortgage','Floating')[1],2)+'% / '+fmt(L('mortgage','1-year fixed')[1],2)+'%',D.mortgage]);
 if(fx)r.push(['NZD TWI / NZD/USD (daily)',fx.date,fmt(fx.TWI,2)+' / '+fmt(fx['NZD/USD'],3),D.fx]);
 r.push(['Goods terms of trade, q/q',L('terms_of_trade','Quarterly % change')[0]+' qtr',sg(L('terms_of_trade','Quarterly % change')[1])+'%',D.terms_of_trade]);
 r.push(['Real GDP per head, q/q',L('gdp_per_capita','q/q % change')[0]+' qtr',sg(L('gdp_per_capita','q/q % change')[1])+'%',D.gdp_per_capita]);
 const W=D.work_visas.series;r.push(['Work-visa applications approved',last(W['Approved, month (current FY)'])[0]+' (month)',fmt(last(W['Approved, month (current FY)'])[1],0),D.work_visas]);
 document.getElementById('snap').innerHTML='<tr><th>Indicator</th><th>Period</th><th>Value</th><th>Source</th></tr>'+r.map(x=>`<tr><td>${x[0]}</td><td>${x[1]}</td><td>${x[2]}</td><td class="m"><a href="${x[3].release_url}">${x[3].release||'source'}</a></td></tr>`).join('')}

function thesis(){const H=hist();
 document.getElementById('adjh').innerHTML='<tr><th>June</th><th>CA</th><th>Debt/GDP</th><th>Δ unemp.</th><th>Path</th></tr>'+H.map(r=>{const v=verdict(r.ddebt,r.du,r.ca);return`<tr><td>${r.y}</td><td>${fmt(r.ca)}</td><td>${fmt(r.debt,0)}% (${sg(r.ddebt)})</td><td>${sg(r.du)}</td><td class="verdict ${v[1]}">${v[0]}</td></tr>`}).join('');
 const K=H.filter(r=>r.y!=2020&&r.y!=2021);const k=(f)=>K.map(f);const A=(f)=>H.map(f);
 const cMH=corr(A(r=>r.mr),A(r=>r.h)),cMH2=corr(k(r=>r.mr),k(r=>r.h)),cHC=corr(A(r=>r.h),A(r=>r.c)),cCC=corr(A(r=>r.c),A(r=>-r.ca)),cDU=corr(A(r=>r.ddebt),A(r=>r.du));
 const pk=H.reduce((a,b)=>b.debt>a.debt?b:a),lt=last(H),hc=D.housing_credit.series['Annual growth (%)'];const hcPk=hc.filter(p=>p[0]>='2020').reduce((a,b)=>b[1]>a[1]?b:a),hcLo=hc.filter(p=>p[0]>='2022').reduce((a,b)=>b[1]<a[1]?b:a);
 const M=D.migration.series['Net migration (12 months)'];const mpk=M.reduce((a,b)=>b[1]>a[1]?b:a);
 document.getElementById('thesis').innerHTML=`<p>The identity (current account = national saving − investment) holds by definition. What is tested here is <b>which path</b> balanced it each year: higher household mortgage debt (path 1) or higher saving through weaker demand and unemployment (path 2). The data are June years ${H[0].y}–${lt.y} (n = ${H.length}). The links below are correlations over one cycle, not causal estimates.</p><ul>
<li><b>Migration → house prices:</b> correlation ${fmt(cMH,2)} (${fmt(cMH2,2)} excluding 2020–21). <b>Weak in this sample.</b> The biggest house-price boom (2020–21) happened with the border closed, and was driven by a 0.25% OCR. The 2023 migration surge (peak ${fmt(mpk[1],0)} in the 12 months to ${mpk[0]}) arrived while prices were falling under a 5.5% OCR. The longer-run RBNZ research (8–12% per 1% of population) is stronger evidence than this short window.</li>
<li><b>House prices → mortgage debt:</b> correlation ${fmt(cHC,2)}. <b>Supported.</b> C5 housing-credit growth fell from ${fmt(hcPk[1])}% (${hcPk[0]}) to ${fmt(hcLo[1])}% (${hcLo[0]}) and has recovered to ${fmt(last(hc)[1])}% (${last(hc)[0]}), even though house prices are flat.</li>
<li><b>Path 1 (debt) and the deficit:</b> the correlation between credit growth and the deficit in the same year is ${fmt(cCC,2)}. The deficit lagged the credit boom: credit growth peaked in 2021, while the deficit was widest in 2022–23 (−8.9% of GDP, Dec 2022). Mortgage debt rose to <b>${fmt(pk.debt,0)}% of GDP</b> (June ${pk.y}) and is ${fmt(lt.debt,0)}% now. <b>Partly supported:</b> the timing fits with a lag, but the post-COVID import and fiscal boom also widened the deficit.</li>
<li><b>Which path, year by year:</b> the correlation between the change in debt/GDP and the change in unemployment is ${fmt(cDU,2)}. The adjustment table shows <b>path 1 (debt)</b> in most years to 2022, <b>path 2 (unemployment)</b> in 2023–24 as debt/GDP fell, and <b>both</b> in 2025–26: debt/GDP is rising again while unemployment also keeps rising (${fmt(lt.u)}%, June ${lt.y}). That pattern is <b>consistent with the two-path framing</b>.</li>
<li><b>Population growth → lower productivity and real wages:</b> <b>not supported by this window.</b> GDP per head has been flat since 2022, which fits. But year by year, real wage growth was <i>higher</i> in high-population-growth years (2023–24), because inflation was falling faster than wage growth.</li></ul>
<p><b>Market-oriented counterpoint:</b> the same numbers also fit a supply story. Migrants added labour (unemployment rose from its 2022 low as the surge arrived, which cooled wages), and housing took the strain because zoning and infrastructure funding make supply inelastic. Free up supply and keep fiscal policy tight, and migration means more building rather than more leverage. A floating NZD also does part of the adjustment.</p>`}

function sources(){const ul=document.getElementById('srcs');for(const k of IDS.slice(0,-1)){const d=D[k];ul.insertAdjacentHTML('beforeend',`<li><b>${d.title}</b>: ${cite(d)} Retrieved ${d.fetched}.</li>`)}
 ul.insertAdjacentHTML('beforeend',`<li><b>Research cited in the model:</b> ${AN13}; ${CLL}.</li>`);
 const g=(D.meta.gaps||[]).concat(['House prices use the CoreLogic HPI as republished by RBNZ (M10). The REINZ HPI is not openly downloadable as a data file.','The OCR is month-end. Before 2018 it comes from RBNZ B2 historical daily closes.','Population is implied (real GDP ÷ real GDP per head), not the Stats NZ estimated resident population series.','Mortgage debt is C5 housing lending by banks and NBLIs. The level includes series breaks (see RBNZ C5 notes); the annual growth series is break-adjusted by RBNZ.','Import prices are model-only; the Stats NZ import price index is not charted.','Elasticities are estimated from about 10 annual observations. Treat them as illustrative.']);
 for(const f of (D.meta.failed_last_run||[]))g.push('Last refresh failed for '+f.step+' (kept previous data): '+f.error);
 document.getElementById('gaps').innerHTML=g.map(x=>`<li>${x}</li>`).join('');document.getElementById('built').textContent='Data last refreshed '+D.meta.built+'.'}

Promise.all(IDS.map(k=>fetch('data/'+k+'.json').then(r=>r.json()).then(j=>D[k]=j))).then(()=>{
 base();const box=document.getElementById('charts');
 for(const[id,title,,keys,,,cls]of CHARTS)box.insertAdjacentHTML('beforeend',`<div class="card ${cls||''}"><h3>${title}</h3><div class="cw"><canvas id="${id}"></canvas></div><p class="cite">Source: ${keys.map(k=>`<a href="${D[k].release_url}">${D[k].release}</a>`).join('; ')}</p></div>`);
 for(const[id,,yl,,,y2]of CHARTS)mk(id,yl,y2);
 buildControls();snapshot();thesis();sources();render();
 document.getElementById('reset').onclick=()=>{for(const k in DEF){V[k]=DEF[k];document.getElementById('i_'+k).value=DEF[k]}for(const k in EDEF){E[k]=EDEF[k];document.getElementById('i_e_'+k).value=EDEF[k]}render()};
}).catch(e=>{document.getElementById('charts').textContent='Failed to load data: '+e;console.error(e)});
