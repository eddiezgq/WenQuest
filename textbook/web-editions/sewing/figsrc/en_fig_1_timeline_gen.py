# generates figsrc/en_fig_1_timeline.en.html (SVG drawn in the original's 2000x968 display frame)
X1=lambda y:117+(y-1825)*(1935-117)/65
X2=lambda y:116+(y-1840)*(1935-116)/190
o=[]
T=lambda x,y,s,sz=14.5,w=400,c='#4a5560',a='middle':o.append(f'<text x="{x:.1f}" y="{y}" font-size="{sz}" font-weight="{w}" fill="{c}" text-anchor="{a}">{s}</text>')
L=lambda x1,y1,x2,y2,c='#7a848e',w=1.1,d='':o.append(f'<line x1="{x1:.1f}" y1="{y1}" x2="{x2:.1f}" y2="{y2}" stroke="{c}" stroke-width="{w}" {d}/>')
T(42,54,'From invention to intelligence: two hundred years of the sewing machine',27,700,'#1b2430','start')
T(42,88,'Top: key patents of the age of invention and the problems they solved. Bottom: the five stages of the industrial sewing machine (dates approximate; stages overlap)',16.5,400,'#5a6570','start')
# top axis
L(117,347,1935,347,'#1b2430',2)
for y in range(1830,1891,10):
    L(X1(y),341,X1(y),353,'#1b2430',1.5); T(X1(y),379,str(y),14,400,'#5a6570')
T(1935,404,'Top axis is the age of invention (1825–1890), enlarged',13.5,400,'#5a6570','end')
ev=[ # year, label x, row, title, l1, l2
 (1830,158,0,'1830 Thimonnier','single-thread chainstitch','hooked needle · French patent'),
 (1834,374,1,'c. 1833–34 Hunt','eye-pointed needle + shuttle','lockstitch; no patent applied for'),
 (1846,589,0,'1846 Howe · US 4,750','curved needle swinging sideways + shuttle','fabric hung on a pin plate; straight seams only'),
 (1851,805,1,'1851 Singer · US 8,294','straight needle up and down, overhanging arm','spring presser, continuous feed'),
 (1851.6,1020,0,'1851–52 Wilson','rotating hook (forerunner of the rotary hook)','US 8,296 / 9,041'),
 (1854,1236,1,'1854 Wilson · US 12,116','four-motion feed','rise, advance, drop, return'),
 (1856,1452,0,'1856 patent pool','nine patents licensed jointly','sewing machines spread widely'),
 (1857,1667,1,'1857 Gibbs · US 17,427','single-thread chainstitch machine','rotating hook forms the loop'),
 (1884,1883,0,'1884 electric motor','sewing machines begin to be','driven by electric motors')]
for yr,lx,row,t,a,b in ev:
    y0=130 if row==0 else 214
    L(lx,y0+62,X1(yr),340)
for yr,lx,row,t,a,b in ev:
    y0=130 if row==0 else 214
    anc='end' if lx>1850 else 'middle'; xx=1935 if lx>1850 else lx
    T(xx,y0+6,t,17,700,'#1b2430',anc); T(xx,y0+30,a,14,400,'#4a5560',anc); T(xx,y0+49,b,14,400,'#4a5560',anc)
    c='#e0662f' if yr==1884 else '#2a6fdb'
    o.append(f'<circle cx="{X1(yr):.1f}" cy="347" r="7" fill="{c}"/>')
# bottom gantt
T(42,431,'Five stages of the industrial sewing machine',20,700,'#1b2430','start')
for y in range(1840,2021,20):
    L(X2(y),455,X2(y),890,'#c9ced3',1,'stroke-dasharray="4 5"'); T(X2(y),920,str(y),14,400,'#5a6570')
st=[(1850,1950,480,'#8aaee9','1  Mechanisation','r',['Treadle, electric motor, mechanisms settled','shuttles, four-motion feed (Chapters 2–8)']),
    (1945,1985,573,'#3f7fdb','2  High speed','r',['Speeds of several thousand stitches per minute','balancing, lubrication, lighter parts (Chapters 3, 8)']),
    (1970,2015,666,'#237f80','3  Electronic control','l',['Servo motors, needle positioning, automatic trimming','electronic stitch length and tension (Chapters 13–22)']),
    (1980,2030,758,'#e5793f','4  Automation','l',['Pattern sewers, template machines, automatic units, hangers','(Chapters 11, 12, 15)']),
    (2010,2030,851,'#9a6bcf','5  Intelligence','l',['Networking, data, vision and AI','(Chapters 14, 26, 30, 31)'])]
for a,b,y,c,name,side,txt in st:
    o.append(f'<rect x="{X2(a):.1f}" y="{y-17}" width="{X2(b)-X2(a):.1f}" height="35" rx="5" fill="{c}"/>')
    T(X2(a)+14,y+6.5,name,17.5,700,'#ffffff','start')
    if side=='r': xx=X2(b)+18; anc='start'
    else: xx=X2(a)-16; anc='end'
    T(xx,y-3,txt[0],14.5,400,'#1b2430',anc); T(xx,y+17,txt[1],14.5,400,'#1b2430',anc)
# redraw grid over bars faintly (as in original)
for y in range(1840,2021,20):
    L(X2(y),455,X2(y),890,'rgba(255,255,255,.55)',1,'stroke-dasharray="4 5"')
html=('<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">'
 '<div class="fig" style="--w:1900px;padding:0"><svg width="1900" height="920" viewBox="0 0 2000 968" xmlns="http://www.w3.org/2000/svg" style="display:block">'
 +''.join(o)+'</svg></div>')
open('figsrc/en_fig_1_timeline.en.html','w').write(html)
