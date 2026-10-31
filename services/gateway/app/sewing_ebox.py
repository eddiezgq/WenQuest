"""缝纫机设计软件 · 电控箱的热与流体（第 62 轮）：参数表和公式计算（来宾也能算，同设计计算）。CAE 复核（流体 → 温度场）在 sewing_cae.py。

  GET  /api/v1/sewing/ebox/schema?machine=      参数分组、选项、这台机型的默认值
  POST /api/v1/sewing/ebox/analyze             {machine, params（设计参数）, ebox（电控箱参数）, rbox?（CAE 算出的箱子热阻）}
"""
from typing import Any

from pydantic import BaseModel, Field

from . import sewcore
from .moodle import EngineError
from .sewcore import ebox as EB


class EboxIn(BaseModel):
    machine: str = Field(default="lockstitch", max_length=20)
    params: dict[str, Any] = Field(default_factory=dict)
    ebox: dict[str, Any] = Field(default_factory=dict)
    rbox: float | None = Field(default=None, ge=0.01, le=20)


def schema(machine: str) -> dict:
    d = EB.defaults_for(machine)
    return {"version": EB.VERSION, "lectures": EB.LECTURES, "defaults": d,
            "groups": [{"key": k, "zh": zh, "en": en, "params": [
                dict(key=p[0], zh=p[1], en=p[2], unit=p[3], default=d[p[0]], min=p[5], max=p[6], step=p[7],
                     choices=[dict(key=c[0], zh=c[1], en=c[2]) for c in EB.CHOICES.get(p[0], [])]) for p in ps]}
                for k, zh, en, ps in EB.GROUPS]}


def compute(body: EboxIn) -> dict:
    if body.machine not in sewcore.MACHINES:
        raise EngineError("bad_request", "unknown machine", 400)
    p = sewcore.get(body.machine).clean(body.params)
    return EB.analyze(body.ebox, body.machine, p, Rbox=body.rbox)


def register(app, m) -> None:
    @app.get("/api/v1/sewing/ebox/schema")
    async def ebox_schema(machine: str = "lockstitch"):
        if machine not in sewcore.MACHINES:
            raise EngineError("bad_request", "unknown machine", 400)
        return schema(machine)

    @app.post("/api/v1/sewing/ebox/analyze")
    async def ebox_analyze(body: EboxIn):
        return compute(body)
