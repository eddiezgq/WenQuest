from en_svgkit import *
ply=lambda:'<rect x="65" y="266" width="261" height="22" rx="3" fill="#f3eee0" stroke="#d2c69f"/><rect x="65" y="292" width="261" height="22" rx="3" fill="#efe1c2" stroke="#d2c69f"/>'
ill=[ply()+''.join(f'<line x1="{85+27*i}" y1="258" x2="{85+27*i}" y2="320" stroke="#2a6fdb" stroke-width="2.4"/>' for i in range(9)),
 '<text x="195" y="178" text-anchor="middle" style="font-size:13px">Ultrasonic horn</text><rect x="175" y="190" width="40" height="69" rx="3" fill="#5a6570"/>'+ply()+'<rect x="165" y="286" width="60" height="9" rx="1" fill="#e0662f"/>',
 ply()+'<rect x="65" y="286" width="261" height="7" fill="#b8761a"/><text x="195" y="350" text-anchor="middle" style="fill:#b8761a;font-size:13.5px">Adhesive film</text>',
 '<rect x="65" y="266" width="261" height="22" rx="3" fill="#f3eee0" stroke="#d2c69f"/><rect x="65" y="292" width="261" height="22" rx="3" fill="#efe1c2" stroke="#d2c69f"/>'+''.join(f'<circle cx="{80+21*i}" cy="298" r="8.5" fill="none" stroke="#8a44b4" stroke-width="1.8"/>' for i in range(12))]
cards=[("Sewing (for comparison)","#2a6fdb","#2a5fb8",["Needle and thread join the two plies;","stitches stretch, can be unpicked and","suit almost anything; needle holes may leak"]),
("Ultrasonic welding","#e0662f","#c4531d",["High-frequency vibration locally melts","synthetic fibres; flat, sealed seams with no","needle holes; only for thermoplastic-rich cloth"]),
("Hot-melt tape bonding","#b8761a","#a8740c",["Heat and pressure melt an adhesive film between","the plies; seamless underwear, sportswear,","waterproof seams; cotton works if heat is controlled"]),
("Whole-garment knitting","#8a5cc7","#7444b4",["The garment is joined while it is knitted;","no cutting or seaming;","knitwear only (Ch. 17, 29)"])]
s=''
for k,((n,c,tc,lines),g) in enumerate(zip(cards,ill)):
    x=[40,450,859,1270][k]
    s+=f'<g transform="translate({x},120)"><rect width="390" height="470" rx="8" fill="#fff" stroke="{c}" stroke-width="2"/><text x="195" y="31" text-anchor="middle" style="fill:{tc};font-weight:700;font-size:15.5px">{n}</text><g transform="translate(0,-120)">{g}</g>'
    s+=''.join(f'<text x="195" y="{345+i*24}" text-anchor="middle" style="fill:#1b2430;font-size:14px">{l}</text>' for i,l in enumerate(lines))+'</g>'
render('fig_23_join',page(1700,640,'Joining without sewing: which sewing operations they replace','Illustrative',f'<svg width="1700" height="640">{s}</svg>'))
