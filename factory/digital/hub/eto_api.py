# -*- coding: utf-8 -*-
"""按单设计（ETO，第 139 轮）的网页接口：作业、估算、AI 起草、发报价（提议 → 人确认 → 桥接写入 ERPNext）。"""
import logging

from fastapi import Body, Depends, HTTPException

from hub import ai as _ai
from hub import eto as E
from hub import eto_design as ED
from hub import eto_mrp as EM
from hub import eto_plan as EP

log = logging.getLogger("eto")
ROLES = ("sales", "planner", "engineer", "manager", "approver")


def mount(app, H, user_of, who, ai_quota=None):
    for fn in (E.on_proposal_done, ED.on_proposal_done):
        if fn not in _ai.ON_PROPOSAL_DONE:
            _ai.ON_PROPOSAL_DONE.append(fn)

    def can(u):
        if u.get("role") not in ROLES and not u.get("teacher"):
            raise HTTPException(403, "估算和报价由销售、计划、设计或厂长做")

    def found(d, jn):
        if d is None:
            raise HTTPException(404, "没有作业 {}".format(jn))
        return d

    @app.get("/api/eto/config")
    def eto_config(u=Depends(user_of)):
        """配置，以及估算表要选的工序、原材料和外购件"""
        from factory import data as F
        return dict(E.config(), operations=list(F.OPERATIONS),
                    items=[{"code": c, "name": v[0], "kind": v[1], "uom": v[2]} for c, v in F.ITEMS.items() if v[1] in ("raw", "buy")],
                    all_items=[{"code": c, "name": v[0], "kind": v[1], "uom": v[2], "bom": c in F.BOMS} for c, v in F.ITEMS.items()
                               if not str(v[6] or "").startswith("按单设计")],
                    suppliers={k: v["name"] for k, v in F.SUPPLIERS.items()})

    @app.get("/api/eto/jobs")
    def eto_jobs(u=Depends(user_of)):
        return E.jobs(H.db, u["mode"])

    @app.post("/api/eto/jobs")
    def eto_new(body: dict = Body(...), u=Depends(user_of)):
        can(u)
        try:
            return E.new_job(H.db, u["mode"], who(u), body.get("customer"), body.get("title"), body.get("requirement"),
                             body.get("qty"), body.get("qty_breaks"), body.get("due_date"))
        except E.EtoError as e:
            raise HTTPException(400, str(e))

    def with_feas(d):
        """第 139d 段：报价时能否按期（按估算粗算）"""
        if d:
            d["feasibility"] = EP.feasibility(d["job"], (d.get("estimate") or {}).get("lines") or [])
        return d

    @app.get("/api/eto/jobs/{job_no}")
    def eto_detail(job_no: str, u=Depends(user_of)):
        try:
            return with_feas(found(E.detail(H.db, u["mode"], job_no), job_no))
        except E.EtoError as e:
            raise HTTPException(400, str(e))

    @app.put("/api/eto/jobs/{job_no}/estimate")
    def eto_save(job_no: str, body: dict = Body(...), u=Depends(user_of)):
        can(u)
        try:
            E.save_estimate(H.db, u["mode"], job_no, body.get("lines"), body.get("note"), who(u), body.get("source") or "human")
        except KeyError:
            raise HTTPException(404, "没有作业 {}".format(job_no))
        except E.EtoError as e:
            raise HTTPException(409, str(e))
        return with_feas(E.detail(H.db, u["mode"], job_no))

    @app.post("/api/eto/jobs/{job_no}/draft")
    def eto_draft(job_no: str, u=Depends(user_of)):
        """起草估算行（AI；没有模型照现有产品）。只返回草稿，估算员看过再存。"""
        can(u)
        j = found(E.job(H.db, u["mode"], job_no), job_no)
        llm = getattr(getattr(H, "ai", None), "llm", None)
        if llm is not None and llm.available() and ai_quota:
            ai_quota(u)
        try:
            return E.draft(llm, j)
        except Exception as ex:  # noqa: BLE001 —— 模型出错：退回规则起草
            log.warning("AI 起草估算出错，改用规则：%s", ex)
            d = E.draft(None, j)
            d["note"] = "AI 起草出错（{}），".format(str(ex)[:120]) + d["note"]
            return d

    @app.post("/api/eto/jobs/{job_no}/quote")
    def eto_quote(job_no: str, u=Depends(user_of)):
        """发报价：生成提议（预览），人确认后桥接在 ERPNext 建 Project、物料、报价单"""
        can(u)
        try:
            pv = E.quote_preview(H.db, u["mode"], job_no)
        except KeyError:
            raise HTTPException(404, "没有作业 {}".format(job_no))
        except E.EtoError as e:
            raise HTTPException(409, str(e))
        title = "报价 {}：{} {} 件，{:.2f}".format(job_no, pv["job"]["customer"], pv["quotation"]["qty"], pv["quotation"]["amount"])
        pid = H.ai.propose("eto_quote", pv, u["mode"], u["name"], title, source="workbench/" + who(u), role=u["role"])
        return {"proposal_id": pid, "preview": pv, "title": title}

    # ------------------------------------------------------------ 139b：接单、设计、设计发布
    def propose(u, action, pv, title):
        pid = H.ai.propose(action, pv, u["mode"], u["name"], title, source="workbench/" + who(u), role=u["role"])
        return {"proposal_id": pid, "preview": pv, "title": title}

    def guard(fn):
        try:
            return fn()
        except KeyError as e:
            raise HTTPException(404, "没有作业 {}".format(e.args[0] if e.args else ""))
        except E.EtoError as e:
            raise HTTPException(409, str(e))

    @app.post("/api/eto/jobs/{job_no}/order")
    def eto_order(job_no: str, body: dict = Body(default={}), u=Depends(user_of)):
        """客户接受报价：销售订单提议（单价按报出去的那一版，付款计划按里程碑）"""
        can(u)
        pv = guard(lambda: ED.order_preview(H.db, u["mode"], job_no, body.get("delivery_date")))
        so = pv["sales_order"]
        return propose(u, "eto_order", pv, "接单 {}：{} {} 件，{:.2f}".format(job_no, so["customer"], so["qty"], so["amount"]))

    @app.get("/api/eto/jobs/{job_no}/design")
    def eto_design_get(job_no: str, u=Depends(user_of)):
        return found(ED.detail(H.db, u["mode"], job_no), job_no)

    @app.put("/api/eto/jobs/{job_no}/design")
    def eto_design_save(job_no: str, body: dict = Body(...), u=Depends(user_of)):
        can(u)
        guard(lambda: ED.save(H.db, u["mode"], job_no, body.get("spec"), who(u)))
        return ED.detail(H.db, u["mode"], job_no)

    @app.post("/api/eto/jobs/{job_no}/design/draft")
    def eto_design_draft(job_no: str, u=Depends(user_of)):
        """照报出去的那一版估算起草设计（只返回草稿，设计员看过再存）"""
        can(u)
        j = found(E.job(H.db, u["mode"], job_no), job_no)
        rev = j.get("quoted_rev")
        est = H.db.one("select lines from eto_estimate where mode=%s and job_no=%s " + ("and rev=%s" if rev else "order by rev desc limit 1"),
                       (u["mode"], job_no, rev) if rev else (u["mode"], job_no))
        return ED.from_estimate(j, (est or {}).get("lines") or [])

    @app.post("/api/eto/jobs/{job_no}/design/copy")
    def eto_design_copy(job_no: str, body: dict = Body(...), u=Depends(user_of)):
        """把父件里的一个现有自制件复制为本单新件（只改草稿，不存）"""
        can(u)
        return guard(lambda: ED.copy_as_new(body["spec"], job_no, body.get("parent") or job_no, body.get("code"),
                                            str(body.get("suffix") or "").strip() or "X"))

    @app.post("/api/eto/jobs/{job_no}/design/release")
    def eto_design_release(job_no: str, u=Depends(user_of)):
        """设计发布：校验通过、已接单 → 提议；人确认后桥接在 ERPNext 建新物料和物料清单"""
        can(u)
        pv = guard(lambda: ED.release_preview(H.db, u["mode"], job_no))
        return propose(u, "eto_release", pv, "设计发布 {} 第 {} 版（{} 个新物料、{} 组物料清单）".format(
            job_no, pv["job"]["rev"], len(pv["items"]), len(pv["boms"])))

    # ------------------------------------------------------------ 139c：作业算料、长周期件提前采购
    @app.get("/api/eto/jobs/{job_no}/materials")
    def eto_materials(job_no: str, u=Depends(user_of)):
        """算料预览（不下单）"""
        return guard(lambda: EM.plan(H.db, u["mode"], job_no))

    @app.post("/api/eto/jobs/{job_no}/materials")
    def eto_materials_propose(job_no: str, u=Depends(user_of)):
        """算料 → 提议：工单、请购单都挂作业号；人确认后桥接写入 ERPNext"""
        can(u)
        if ED.pending(H.db, u["mode"], "eto_materials", job_no):
            raise HTTPException(409, "已经有一份算料提议在等确认")
        pv = guard(lambda: EM.plan(H.db, u["mode"], job_no))
        if not pv["work_orders"] and not pv["material_requests"]:
            raise HTTPException(409, "都够用了：没有要下的工单和请购")
        return propose(u, "eto_materials", pv, "作业算料 {}：工单 {} 张、请购 {} 项".format(
            job_no, len(pv["work_orders"]), len(pv["material_requests"])))

    @app.get("/api/eto/jobs/{job_no}/early-buy")
    def eto_early_candidates(job_no: str, u=Depends(user_of)):
        return EM.early_candidates(H.db, u["mode"], job_no)

    @app.post("/api/eto/jobs/{job_no}/early-buy")
    def eto_early_buy(job_no: str, body: dict = Body(...), u=Depends(user_of)):
        """长周期件提前采购（设计发布前）：单独的提议，人确认"""
        can(u)
        pv = guard(lambda: EM.early_buy_preview(H.db, u["mode"], job_no, list(body.get("items") or [])))
        return propose(u, "eto_early_buy", pv, "提前采购 {}：{}".format(job_no, "、".join(r["item_code"] for r in pv["material_requests"])))

    # ------------------------------------------------------------ 139d：倒排与负荷
    @app.get("/api/eto/jobs/{job_no}/schedule")
    def eto_schedule(job_no: str, u=Depends(user_of)):
        def run():
            t = EP.schedule(H.db, u["mode"], job_no)
            t["load"] = EP.load(H.db, u["mode"], job_no)
            return t
        return guard(run)
