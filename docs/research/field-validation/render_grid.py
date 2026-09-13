"""Plot verified, individual-wavelength RMS spot radii; no optical engine calls."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
data = json.loads((HERE/'verified-evidence.json').read_text())
fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.6), layout='constrained')
records = []
for ax, engine, label in zip(axes, ['zos', 'optiland'], ['OpticStudio 2024 R1', 'Optiland 0.6.2']):
    rows = data['runs'][engine+'-validation']['measurements']
    spot = {(r['field'], r['wavelength']): r['value'] for r in rows if r['metric'] == 'rms_spot_um'}
    values = np.array([[spot[f, w] for w in (1, 2, 3)] for f in (1, 2, 3)])
    heat = ax.imshow(values, vmin=0, vmax=90, cmap='YlOrRd', aspect='auto')
    for f in (1, 2, 3):
        for w in (1, 2, 3):
            value = spot[f, w]
            fail = value > 30
            ax.text(w-1, f-1, f'{value:.2f}'+('\n>30' if fail else ''),
                    ha='center', va='center', color='white' if value > 55 else '#222222', fontsize=12)
            records.append(dict(engine=engine, field=f, angle_y_deg=[0, 3, 6][f-1],
                                wavelength=w, wavelength_um=[.4861327, .55, .6562725][w-1],
                                rms_spot_um=value, rms_requirement_passes=not fail))
    ax.set(xticks=[0, 1, 2], xticklabels=['486.13', '550.00\nsearch wavelength', '656.27'],
           yticks=[0, 1, 2], yticklabels=['0°', '3°', '6°'], xlabel='Wavelength (nm)',
           ylabel='Field Y angle', title=label)
fig.colorbar(heat, ax=axes, label='Centroid RMS spot radius (µm)', shrink=.82)
fig.suptitle('Search condition passes; the wider field/spectral grid fails\n'
             'Saved candidates · RMS limit 30 µm · individual wavelengths · sampling 64', fontsize=13)
fig.savefig(HERE/'rms-grid.png', dpi=170)
fig.savefig(HERE/'rms-grid.svg')
svg = HERE/'rms-grid.svg'
svg.write_bytes(('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n').encode('utf-8'))
plt.close(fig)
with (HERE/'rms-grid.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
print('Wrote RMS grid PNG, SVG and CSV from verified results.')
