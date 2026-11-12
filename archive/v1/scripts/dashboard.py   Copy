"""Visual trade dashboard using synthetic demonstration data."""
import csv
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
rows = []
with (ROOT / 'trade_data.csv').open(newline='', encoding='utf-8') as handle:
    for row in csv.DictReader(handle):
        rows.append({
            'year': int(row['year']), 'country': row['country'],
            'exports': float(row['exports_usd_millions']),
            'imports': float(row['imports_usd_millions'])
        })

countries = sorted({r['country'] for r in rows})
years = sorted({r['year'] for r in rows})
by_country = defaultdict(lambda: {'exports': 0.0, 'imports': 0.0})
by_year = defaultdict(lambda: {'exports': 0.0, 'imports': 0.0})
for r in rows:
    for field in ('exports', 'imports'):
        by_country[r['country']][field] += r[field]
        by_year[r['year']][field] += r[field]

plt.style.use('seaborn-v0_8-whitegrid')
fig, axs = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
fig.suptitle('Global Trade Analysis | 2022–2024', fontsize=20, fontweight='bold')
fig.text(0.5, 0.945, 'SYNTHETIC DEMONSTRATION DATA • USD millions', ha='center', fontsize=10)

x = range(len(countries))
axs[0,0].bar([i-0.18 for i in x], [by_country[c]['exports'] for c in countries], width=.36, label='Exports', color='#168a83')
axs[0,0].bar([i+0.18 for i in x], [by_country[c]['imports'] for c in countries], width=.36, label='Imports', color='#f19b57')
axs[0,0].set_xticks(list(x), countries)
axs[0,0].set_title('Trade by Country (3-year totals)')
axs[0,0].set_ylabel('USD millions')
axs[0,0].legend(frameon=False)

axs[0,1].plot(years, [by_year[y]['exports'] for y in years], marker='o', linewidth=3, label='Exports', color='#168a83')
axs[0,1].plot(years, [by_year[y]['imports'] for y in years], marker='o', linewidth=3, label='Imports', color='#f19b57')
axs[0,1].set_xticks(years)
axs[0,1].set_title('Annual Import / Export Trends')
axs[0,1].set_ylabel('USD millions')
axs[0,1].legend(frameon=False)

balances = [by_country[c]['exports'] - by_country[c]['imports'] for c in countries]
axs[1,0].barh(countries, balances, color=['#c65b67' if b < 0 else '#168a83' for b in balances])
axs[1,0].axvline(0, color='#333333', linewidth=1)
axs[1,0].set_title('Trade Balance by Country (3-year totals)')
axs[1,0].set_xlabel('USD millions | Negative = deficit')

imports = [by_country[c]['imports'] for c in countries]
axs[1,1].pie(imports, labels=countries, autopct='%1.1f%%', startangle=90, colors=['#168a83','#f19b57','#6079a9','#9a86c4'])
axs[1,1].set_title('Share of Total Imports (2022–2024)')

output = ROOT / 'trade_dashboard.png'
fig.savefig(output, dpi=170, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'Dashboard saved: {output}')
print('NOTE: All figures are synthetic demonstration data, not real trade statistics.')
