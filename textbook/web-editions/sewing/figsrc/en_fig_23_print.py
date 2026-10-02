from en_svgkit import *
rows=[("Water",1680.7,1082.7,"L","36%"),("Electricity",537.9,347.6,"kWh","35%"),("Chemicals",67.6,48.7,"kg","28%"),("Gas",133.6,99.2,"m³","26%"),
("Waste water",580,340,"L","41%"),("Fabric waste",10,3,"m","70%"),("Chemical waste",96,0.4,"kg",">99%")]
s='';W=1039
fmt=lambda v:(f'{v:g}')
for i,(n,a,b,u,p) in enumerate(rows):
    y=134+64*i
    s+=f'<text x="240" y="{y+30}" text-anchor="end" style="fill:#1b2430;font-weight:700;font-size:16px">{n}</text>'
    s+=f'<rect x="260" y="{y}" width="{W}" height="20" rx="4" fill="#e6b6ae"/><rect x="260" y="{y+24}" width="{max(W*b/a,4)}" height="20" rx="4" fill="#4cad70"/>'
    s+=f'<text x="1313" y="{y+15}" style="font-size:13.5px">Rotary screen {fmt(a)} {u}</text><text x="1313" y="{y+39}" style="fill:#1f8a4c;font-weight:700;font-size:13.5px">Digital {fmt(b)} {u} ({p} ↓)</text>'
inner=f'<svg width="1700" height="620">{s}</svg><p class="foot" style="top:578px">Digital printing needs no screens and prints on demand, so changing designs in small batches wastes almost nothing in set-up; it points the same way as on-demand production and small-batch quick response (Ch. 29).</p>'
render('fig_23_print',page(1700,620,'Resource use of digital versus rotary-screen printing (the same 16-colour design, 1000 m of cotton fabric)',
 'Data from a comparative study at a factory in Peru (Hoque et al., 2024); rotary screen = 100%',inner))
