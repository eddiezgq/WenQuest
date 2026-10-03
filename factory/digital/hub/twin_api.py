# -*- coding: utf-8 -*-
"""数字孪生的网页接口（第 15 轮）"""
from fastapi import Body, Depends, HTTPException

from hub import twin as TW


def mount(app, H, user_of, who, uid_of, is_teacher, ai_quota=None):

    @app.get("/api/twin/fleet")
    def twin_fleet(u=Depends(user_of)):
        mode = u["mode"]
        if mode in TW.FIELD_MODES:
            H.twin.touch(mode)
        c = H.twin._clock(mode)
        return TW.json_safe({"units": TW.fleet(H.db, mode), "field_today": H.twin.field_today(mode).isoformat(),
                             "clock": {"days_per_min": c["days_per_min"], "paused": c["paused"], "simulated": mode in TW.FIELD_MODES},
                             "sites": {k: {"label": v["label"], "customer": v["customer"], "note": v["note"]} for k, v in TW.F.SITES.items()}})

    @app.get("/api/twin/units/{serial}")
    def twin_unit(serial: str, u=Depends(user_of)):
        r = TW.detail(H.db, u["mode"], serial)
        if r is None:
            raise HTTPException(404, "没有这台设备的孪生")
        return TW.json_safe(r)

    @app.post("/api/twin/clock")
    def twin_clock(body: dict = Body(...), u=Depends(user_of)):
        """老师：现场时钟快慢（每分钟多少个现场日，0 = 暂停）"""
        if not is_teacher(u):
            raise HTTPException(403, "只有老师能调现场时钟")
        mode = u["mode"]
        if mode not in TW.FIELD_MODES:
            raise HTTPException(409, "这个模式下没有客户现场模拟器（等真设备的数据）")
        v = float(body.get("days_per_min", 1))
        if not 0 <= v <= 30:
            raise HTTPException(400, "每分钟 0–30 个现场日")
        if v == 0:
            today = H.twin.field_today(mode)
            H.db.x("update field_clock set paused=true, days_per_min=0, anchor_day=%s where mode=%s", (today, mode))
        else:
            H.twin.set_rate(mode, v)
        return {"ok": True, "field_today": H.twin.field_today(mode).isoformat()}
