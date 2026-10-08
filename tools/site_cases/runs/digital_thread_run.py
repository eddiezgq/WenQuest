# 在 factory/digital 目录下运行：python3 ../../tools/site_cases/runs/digital_thread_run.py（需要本地 PostgreSQL：postgresql://postgres@localhost:5433/wq_test）
import sys, json, datetime as dt
sys.path[:0]=['.','..','tests']
from tests.test_agent import NoLLM
from hub.ont import evals as EV
from hub import lab16, service as SV
H,eng=EV.sandbox("postgresql://postgres@localhost:5433/wq_test", name="wq_story5", llm=NoLLM())
db=H.db
TEA={"name":"王老师","role":"manager","teacher":True,"mode":"teach"}
r=lab16.inject(H,TEA,{"n":3}); print("INJECT",json.dumps(r,ensure_ascii=False,default=str))
db.x("update field_clock set anchor_day=anchor_day + 3, paused=true where mode='teach'")
got=SV.tick(H,"teach")["complaints"]; c=db.one("select * from complaint where id=%s",(got[0],))
print("COMPLAINT",json.dumps({k:c[k] for k in c},ensure_ascii=False,default=str))
t=lab16.trace(db,c["serial"]); print("TRACE",json.dumps(t,ensure_ascii=False,default=str))
us=SV.units(db,"teach")
for s in t["units"]+[c["serial"]]:
    u=us.get(s); print("UNIT",s,json.dumps(u,ensure_ascii=False,default=str)[:400], "HIGH",SV.is_high(u) if u else None)
H.ai.detector().run("teach", dt.datetime.now(dt.timezone.utc))
a=lab16._anomaly_for(db,c); print("ANOM",json.dumps({k:a[k] for k in ('rule','title','detail') if k in a},ensure_ascii=False,default=str)[:2500])
ev=SV.anomaly_options(db,"teach",a)
print("REC",ev["recommended"])
for o in ev["options"]:
    oo={k:v for k,v in o.items() if k!='changes'}
    print("OPT",json.dumps(oo,ensure_ascii=False,default=str)[:1500])
from hub.ont import anomaly as A, chain as CH
out=CH.chain_field(A.Ctx(db,"teach"),[c["serial"]],label="投诉").out()
print("CHAIN",json.dumps(out,ensure_ascii=False,default=str)[:6000])
