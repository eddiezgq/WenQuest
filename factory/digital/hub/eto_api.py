# -*- coding: utf-8 -*-
"""按单设计（ETO，第 139 轮）的网页接口：作业、估算、AI 起草、发报价（提议 → 人确认 → 桥接写入 ERPNext）。"""
import logging

from fastapi import Body, Depends, HTTPException

from hub import ai as _ai
from hub import eto as E

log = logging.getLogger("eto")
ROLES = ("sales", "planner", "engineer", "manager", "approver")


def mount(app, H, user_of, who, ai_quota=None):
    if E.on_proposal_done not in _ai.ON_PROPOSAL_DONE:
        _ai.ON_PROPOSAL_DONE.append(E.on_proposal_done)

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
                    items=[{"code": c, "name": v[0], "kind": v[1], "uom": v[2]} for c, v in F.ITEMS.items() if v[1] in ("raw", "buy")])

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

    @app.get("/api/eto/jobs/{job_no}")
    def eto_detail(job_no: str, u=Depends(user_of)):
        try:
            return found(E.detail(H.db, u["mode"], job_no), job_no)
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
        return E.detail(H.db, u["mode"], job_no)

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
