from en_svgkit import *
s='<rect x="40" y="120" width="640" height="620" rx="8" fill="#fff" stroke="#e2e5e8" stroke-width="1.5"/>'
T=lambda x,y,t,st='': f'<text x="{x}" y="{y}" style="fill:#1b2430;font-size:15px;{st}">{t}</text>'
s+=T(70,180,'Shirt poplin (c = 20 mm, B ≈ 9.4 μN·m)')+T(70,206,'clamped vertically: the greatest height it can stand')+T(70,232,'l = (7.84 B/w)^(1/3) ≈ 2c ≈ 4.0 cm')
s+='<rect x="110" y="470" width="140" height="16" rx="2" fill="#5a6570"/><line x1="180" y1="470" x2="180" y2="397" stroke="#2e9e5b" stroke-width="4"/>'
s+='<rect x="350" y="470" width="140" height="16" rx="2" fill="#5a6570"/><path d="M420,470 C416,420 440,364 486,361" fill="none" stroke="#e0662f" stroke-width="4"/>'
s+='<text x="180" y="514" text-anchor="middle" style="fill:#1f8a4c;font-weight:700;font-size:15px">3 cm: stands</text><text x="420" y="514" text-anchor="middle" style="fill:#c4531d;font-weight:700;font-size:15px">8 cm: bends over</text>'
s+=T(70,570,'Pushing a 5 cm × 30 cm strip from one end (other end free to move sideways,')+T(70,594,'self-weight ignored): critical force F = π²Bb/(4L²) ≈ 2.8 mN; the strip weighs ≈ 17.7 mN.')+T(70,618,'So a sewing machine drags the cloth instead: the feed dog pulls from below,')+T(70,642,'and the presser foot presses from above.')
cloth=lambda y:f'<rect x="50" y="{y}" width="200" height="10" rx="2" fill="#f3eee0" stroke="#d8cfb4"/>'
ill={
'needle':'<rect x="71" y="71" width="159" height="21" rx="3" fill="#5a6570"/>'+cloth(139)+''.join(f'<line x1="{x}" y1="92" x2="{x+7}" y2="145" stroke="#1b2430" stroke-width="1.8"/>' for x in [91,121,151,181,211]),
'vac':'<rect x="90" y="91" width="120" height="49" rx="4" fill="#5a6570"/>'+cloth(139)+'<line x1="150" y1="125" x2="150" y2="68" stroke="#2e9e5b" stroke-width="2"/><path d="M143,72 L150,57 L157,72z" fill="#5a6570"/>',
'el':'<rect x="71" y="99" width="159" height="36" rx="4" fill="#fbf0d4" stroke="#c48a17" stroke-width="1.6"/>'+''.join(f'<text x="{86+i*26}" y="122" text-anchor="middle" style="fill:#a8740c;font-size:15px">{"−" if i%2==0 else "+"}</text>' for i in range(6))+cloth(141),
'cryo':'<rect x="70" y="100" width="160" height="35" rx="4" fill="#e9eefc" stroke="#8a5cc7" stroke-width="1.6"/><text x="150" y="123" text-anchor="middle" style="fill:#7444b4;font-size:15px">−20 °C</text>'+cloth(141),
'stiff':'<path d="M110,59 L110,110 L190,110 L190,59" fill="none" stroke="#1b2430" stroke-width="2.2"/><rect x="50" y="131" width="200" height="10" fill="#f0b49b"/><rect x="50" y="140" width="200" height="10" fill="#e8a483"/>',
'vis':'<circle cx="99" cy="80" r="16" fill="#fff" stroke="#1b2430" stroke-width="2"/><line x1="105" y1="96" x2="129" y2="135" stroke="#c8352b" stroke-width="1.4" stroke-dasharray="4 3"/>'+cloth(139)+''.join(f'<circle cx="{90+i*26}" cy="158" r="7" fill="#c8352b"/>' for i in range(6)),
}
cards=[("Needle gripper","#2a6fdb","#2a5fb8","needle",["Fine needles driven obliquely into","the cloth hook it; suits thicker,","looser cloth; may leave needle holes"]),
("Vacuum","#2e9e5b","#1f8a4c","vac",["Vacuum through the table or cups;","air-permeable cloth leaks, needs high","flow; single plies hard to separate"]),
("Electroadhesion","#c48a17","#a8740c","el",["Electrode plates hold the cloth;","works well on thin cloth, single plies;","affected by humidity"]),
("Cryo-grip","#8a5cc7","#7444b4","cryo",["Sprayed with water and frozen onto","a cold plate; firm grip, can pick a","single ply; must wait for it to thaw"]),
("Stiffen the cloth","#e0662f","#c4531d","stiff",["Soaked in water-soluble resin, the cloth","handles like sheet, moved by ordinary","robot arms; washed out after sewing"]),
("Vision + real-time correction","#c8352b","#c8352b","vis",["Cameras and sensors recognise the","panel and keep adjusting its path","as it passes the sewing head"])]
for k,(n,c,tc,key,lines) in enumerate(cards):
    x=720+320*(k%3); y=120+310*(k//3)
    s+=f'<g transform="translate({x},{y})"><rect width="300" height="290" rx="7" fill="#fff" stroke="{c}" stroke-width="2"/><text x="150" y="29" text-anchor="middle" style="fill:{tc};font-weight:700;font-size:15.5px">{n}</text>{ill[key]}'
    s+=''.join(f'<text x="150" y="{218+i*20}" text-anchor="middle" style="fill:#1b2430;font-size:13.5px">{l}</text>' for i,l in enumerate(lines))+'</g>'
render('fig_23_grip',page(1700,780,'Cloth cannot be pushed, only pulled, supported or gripped: ways of feeding and grasping fabric',
 'Left: a strip of cloth clamped vertically stands under its own weight only up to about 2c; right: several common fabric-gripping methods (illustrative)',f'<svg width="1700" height="780">{s}</svg>'))
