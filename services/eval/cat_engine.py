"""自适应闭卷考试引擎（施工第3步，第一版）。
模型：每个知识点一个能力值 θ_k，单参数（Rasch）作答模型；以全章总体能力作先验中心（经验贝叶斯），
知识点之间互相借力。题目难度先用模板的估计值 b，积累作答后可换成校准值（接口不变）。"""
import json, math, random
import numpy as np

GRID=np.linspace(-4,4,161)
CUTS=(-0.5,0.5,1.5)                      # 未掌握 | 基本掌握 | 熟练 | 精通
TIERS=["未掌握","基本掌握","熟练","精通"]
TAU=0.8                                  # 知识点能力围绕总体能力的离散程度

def p_correct(theta,b): return 1/(1+np.exp(-(theta-b)))
def tier_of(theta): return sum(theta>c for c in CUTS)

class AdaptiveExam:
    def __init__(self,items,kps,max_items=30,max_per_kp=4,tier_conf=0.8):
        self.items=items; self.kps=kps
        self.max_items,self.max_per_kp,self.tier_conf=max_items,max_per_kp,tier_conf
        self.resp=[]                      # (item, correct)
        self._cache={}
        self._tiermask=[np.array([tier_of(g)==t for g in GRID]) for t in range(4)]
    # —— 估计 ——
    def _global(self):
        lp=-0.5*GRID**2
        for it,c in self.resp:
            p=p_correct(GRID,it["b"]); lp+=np.log(p if c else 1-p)
        w=np.exp(lp-lp.max()); w/=w.sum(); return float((w*GRID).sum())
    def posterior(self,kp):
        if "_g" not in self._cache: self._cache["_g"]=self._global()
        mu=self._cache["_g"]; lp=-0.5*((GRID-mu)/TAU)**2
        for it,c in self.resp:
            if it["kp"]==kp: p=p_correct(GRID,it["b"]); lp+=np.log(p if c else 1-p)
        w=np.exp(lp-lp.max()); w/=w.sum(); return w
    def estimate(self,kp):
        if kp in self._cache: return self._cache[kp]
        r=self._estimate(kp); self._cache[kp]=r; return r
    def _estimate(self,kp):
        w=self.posterior(kp); m=float((w*GRID).sum()); sd=float(np.sqrt((w*(GRID-m)**2).sum()))
        tp=[float(w[m].sum()) for m in self._tiermask]
        return {"theta":m,"sd":sd,"tier":int(np.argmax(tp)),"tier_prob":max(tp),"n":sum(1 for it,_ in self.resp if it["kp"]==kp)}
    # —— 出题 ——
    def _done(self,kp):
        e=self.estimate(kp); return e["n"]>=self.max_per_kp or (e["n"]>=1 and e["tier_prob"]>=self.tier_conf)
    def next_item(self):
        if len(self.resp)>=self.max_items: return None
        used={it["id"] for it,_ in self.resp}; used_tpl={it["template"] for it,_ in self.resp}
        open_kps=[k for k in self.kps if not self._done(k)]
        if not open_kps: return None
        kp=max(open_kps,key=lambda k:self.estimate(k)["sd"])
        th=self.estimate(kp)["theta"]
        cand=[it for it in self.items if it["kp"]==kp and it["id"] not in used]
        # 信息量最大（难度最接近当前估计）；同等情况下优先没出过的模板，避免连续同一类题
        cand.sort(key=lambda it:(abs(it["b"]-th)+(0.3 if it["template"] in used_tpl else 0), it["id"]))
        return cand[0] if cand else None
    def answer(self,item,correct): self.resp.append((item,bool(correct))); self._cache={}
    def report(self):
        return {k:{**self.estimate(k),"tier_name":TIERS[self.estimate(k)["tier"]]} for k in self.kps}

# —— 用虚拟考生检验 ——
def simulate(n=200,seed=7):
    d=json.load(open("ch1_bank.json")); items=d["items"]; kps=[k["id"] for k in d["knowledge_points"]]
    rng=np.random.default_rng(seed); random.seed(seed)
    res={"adaptive":[], "fixed30":[]}
    for s in range(n):
        g=rng.normal(); true={k:g+rng.normal(0,0.7) for k in kps}
        ans=lambda it: rng.random()<p_correct(true[it["kp"]],it["b"])
        # 自适应
        ex=AdaptiveExam(items,kps)
        while (it:=ex.next_item()) is not None: ex.answer(it,ans(it))
        rep=ex.report(); res["adaptive"].append((len(ex.resp),true,rep))
        # 固定 30 题（每个知识点随机 3 题）
        fx=AdaptiveExam(items,kps,max_items=999)
        for k in kps:
            for it in random.sample([i for i in items if i["kp"]==k],3): fx.answer(it,ans(it))
        res["fixed30"].append((30,true,fx.report()))
    out={}
    for name,rows in res.items():
        err=[];hit=[];near=[];L=[]
        for L_,true,rep in rows:
            L.append(L_)
            for k in kps:
                err.append(rep[k]["theta"]-true[k]); t=tier_of(true[k])
                hit.append(rep[k]["tier"]==t); near.append(abs(rep[k]["tier"]-t)<=1)
        out[name]={"平均题数":round(float(np.mean(L)),1),"能力估计误差RMSE":round(float(np.sqrt(np.mean(np.square(err)))),3),
                   "档位完全判对":f"{100*np.mean(hit):.1f}%","档位误差不超过一档":f"{100*np.mean(near):.1f}%"}
    return out

if __name__=="__main__":
    print(json.dumps(simulate(),ensure_ascii=False,indent=1))
