# Renders the 1200x675 X/Twitter chart from nz/data (run from repo root after nz/build.py).
import json,matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
L=lambda f:json.load(open('nz/data/'+f+'.json'))
t=lambda p:int(p[:4])+(int(p[5:7])-0.5)/12
mig=L('migration')['series']['Net migration (12 months)'];un=L('unemployment')['series']['Unemployment rate'];rw=L('wages')['series']['Real wage growth (QES - CPI)']
fig,ax=plt.subplots(figsize=(12,6.75),dpi=100);fig.patch.set_facecolor('white')
ax2=ax.twinx()
ax2.fill_between([t(p[0]) for p in mig],[p[1]/1000 for p in mig],color='#2f6fb5',alpha=.18,lw=0)
ax2.plot([t(p[0]) for p in mig],[p[1]/1000 for p in mig],color='#2f6fb5',lw=2,label='Net migration, 12-mo total (k, right)')
ax.plot([t(p[0]) for p in un],[p[1] for p in un],color='#c0392b',lw=2.6,label='Unemployment rate (%)')
ax.plot([t(p[0]) for p in rw],[p[1] for p in rw],color='#111',lw=2.6,label='Real wage growth: QES − CPI (pp)')
ax.axhline(0,color='#999',lw=.8)
ax.set_zorder(ax2.get_zorder()+1);ax.patch.set_visible(False)
ax.set_xlim(2015,2026.9);ax.set_ylim(-3,7);ax2.set_ylim(-60,140)
ax.set_ylabel('% / percentage points',fontsize=12);ax2.set_ylabel('Net migration (thousands)',fontsize=12,color='#2f6fb5')
for a in(ax,ax2):a.tick_params(labelsize=12);[a.spines[s].set_visible(False) for s in('top',)]
h1,l1=ax.get_legend_handles_labels();h2,l2=ax2.get_legend_handles_labels();ax.legend(h1+h2,l1+l2,loc='upper left',fontsize=12,frameon=False)
fig.suptitle('New Zealand: migration boom, then jobs and real wages turn',fontsize=20,fontweight='bold',x=.06,ha='left',y=.965)
ax.set_title(f"Latest: net migration +{mig[-1][1]:,.0f} (yr to {mig[-1][0]}), unemployment {un[-1][1]}% ({un[-1][0]} qtr), real wages {rw[-1][1]:+.1f} pp",fontsize=13,loc='left',color='#555')
fig.text(.06,.025,'Source: Stats NZ: international migration (rel. 14 Oct 2026); HLFS & QES, Jun qtr (rel. 5 Aug 2026); CPI, Sep qtr (rel. 22 Oct 2026). simon-manning.github.io/nz',fontsize=9.5,color='#777')
ax.grid(axis='y',color='#eee')
fig.subplots_adjust(left=.07,right=.93,top=.84,bottom=.1)
fig.savefig('/workspace/nz_x_chart.png',dpi=100)
