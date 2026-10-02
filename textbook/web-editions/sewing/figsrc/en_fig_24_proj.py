# English fig_24_proj (refs updated: Ch. 21 -> 28, 22 -> 29; labs 21-1, 22-1 -> 28-1, 29-1)
from en_svgkit import *
B=[("1 Preparation","#1b2430","#1b2430",["Complete Lab 7 in the WenQuest","Digital Factory; learn to read dashboards,","ask the AI, check the sources"],"Digital factory · Lab 7"),
("2 Build the data","#2a6fdb","#2a5fb8",["Pick a style; write down operations,","work content, staff groups","and output records"],"Ch. 28 · Labs 28-1, 29-1"),
("3 Ask the AI","#8a5cc7","#7444b4",["Have the AI assistant find the bottleneck","and propose improvements; require it to","show its calculations and data sources"],"AI assistant"),
("4 Calculate yourself","#e0662f","#c4531d",["Use balance efficiency, cycle time and","Little’s law to check the AI’s","conclusions point by point"],"Ch. 28, 29 · Lab 29-1"),
("5 Report","#2e9e5b","#1f8a4c",["Where the AI was right, where it was","wrong, and why; improvement plan","and its expected effect"],"Oral defence")]
s='<defs><marker id="m" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10z" fill="#5a6570"/></marker></defs>'
for i,(n,c,tc,ls,ft) in enumerate(B):
    x=40+330*i
    s+=f'<rect x="{x}" y="130" width="300" height="170" rx="8" fill="#fff" stroke="{c}" stroke-width="2"/><text x="{x+150}" y="159" text-anchor="middle" style="fill:{tc};font-weight:700;font-size:16px">{n}</text>'
    s+=''.join(f'<text x="{x+150}" y="{185+i2*19}" text-anchor="middle" style="fill:#1b2430;font-size:12.5px">{l}</text>' for i2,l in enumerate(ls))
    s+=f'<text x="{x+150}" y="281" text-anchor="middle" style="fill:{tc};font-weight:700;font-size:12.5px">{ft}</text>'
    if i<4: s+=f'<line x1="{x+303}" y1="215" x2="{x+327}" y2="215" stroke="#5a6570" stroke-width="2.6" marker-end="url(#m)"/>'
s+='<text x="40" y="370" style="fill:#1b2430;font-size:15px">Grading does not focus on the answer the AI gives but on whether the student can judge it: are the numbers calculated from the given data,</text>'
s+='<text x="40" y="398" style="fill:#1b2430;font-size:15px">has takt time been confused with cycle time, and do the proposed improvements violate operation precedence, machine types or head count?</text>'
render('fig_24_proj',page(1700,480,'Student project: find a sewing line’s bottleneck with the digital factory and an AI assistant, and verify the AI’s answers',
 'Illustrative; below each box: the book chapters or virtual labs used',f'<svg width="1700" height="480">{s}</svg>'))
