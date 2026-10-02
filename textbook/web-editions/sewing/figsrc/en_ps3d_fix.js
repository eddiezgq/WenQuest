// Post-render label nudges for the English captures (CSS px). Usage: window.__nudge('Title', dx, dy)
window.__nudge=(t,dx,dy)=>{const svg=document.getElementById('lab');const ts=[...svg.querySelectorAll('text')];const i=ts.findIndex(e=>e.textContent===t);if(i<0)return 'miss '+t;
 const tt=ts[i];const path=tt.previousElementSibling;const sub=tt.nextElementSibling&&tt.nextElementSibling.tagName==='text'&&tt.nextElementSibling.getAttribute('font-weight')!=='700'?tt.nextElementSibling:null;
 for(const e of [tt,sub]) if(e){e.setAttribute('x',+e.getAttribute('x')+dx);e.setAttribute('y',+e.getAttribute('y')+dy);}
 const m=path.getAttribute('d').match(/M([\d.\-]+) ([\d.\-]+)L([\d.\-]+) ([\d.\-]+)/);path.setAttribute('d',`M${m[1]} ${m[2]}L${+m[3]+dx} ${+m[4]+dy}`);return 'ok';};
window.__rename=(a,b)=>{for(const e of document.querySelectorAll('#lab text')) if(e.textContent===a){e.textContent=b;return 'ok';} return 'miss '+a;};
