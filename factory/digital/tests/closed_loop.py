# -*- coding: utf-8 -*-
"""完整闭环测试（对运行中的服务）：总线 + 历史库/枢纽 + 仿真车间 + Node-RED 桥接 + 模拟 ERPNext。

按实验 7 走一遍：教师重置情景 → 学生读看板答题 → 计划员接单算料并确认 → 工艺员发布新版设计与 G 代码 →
下达车间、操作工逐道开工 → 10 根轴做完 → 质检处置 → 成本分析；
然后在模拟 ERPNext 里核对：订单、工单、7 张作业卡（工时不重叠）、每件一张质量检验单、完工入库扣料加成品；
最后核对总线消息全部合规、看板指标更新、AI 能回答成本问题并注明来源。

用法：python3 tests/closed_loop.py [--hub http://localhost:8100] [--erp http://localhost:8091]
真 ERPNext（第 3 轮服务器演练）：加 --erp-kind real --erp-key <API Key> --erp-secret <API Secret>
"""
import argparse
import datetime as dt
import json
import sys
import time
import urllib.parse
import urllib.request

P = argparse.ArgumentParser()
P.add_argument("--hub", default="http://localhost:8100")
P.add_argument("--erp", default="http://localhost:8091")
P.add_argument("--speed", type=float, default=300)
P.add_argument("--timeout", type=float, default=600)
P.add_argument("--erp-kind", choices=("mock", "real"), default="mock")
P.add_argument("--erp-key", default="")
P.add_argument("--erp-secret", default="")
A = P.parse_args()

FAILS = []


def call(method, url, body=None, token=None, headers=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json", **({"x-wq-token": token} if token else {}),
                                          **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        raise RuntimeError("{} {} → {} {}".format(method, url, e.code, e.read().decode()[:400])) from None


def hub(method, path, body=None, token=None):
    return call(method, A.hub + path, body, token)


def erp(path):
    return call("GET", A.erp + urllib.parse.quote(path))


REAL = A.erp_kind == "real"


def erp_docs(doctype):
    """某类单据的全部记录（只含主表字段）：模拟 ERPNext 用它的调试接口，真 ERPNext 用 REST 接口。"""
    if not REAL:
        return erp("/api/mock/db/" + doctype)
    q = urllib.parse.urlencode({"fields": '["*"]', "limit_page_length": 0})
    return call("GET", "{}/api/resource/{}?{}".format(A.erp, urllib.parse.quote(doctype), q),
                headers={"Authorization": "token {}:{}".format(A.erp_key, A.erp_secret)})["data"]


def delivery_date():
    d = dt.date.today() + dt.timedelta(days=16)
    return (d + dt.timedelta(days=(7 - d.weekday()) % 7 if d.weekday() >= 5 else 0)).isoformat()


def check(cond, what):
    print(("  ✓ " if cond else "  ✗ ") + what)
    if not cond:
        FAILS.append(what)


def login(name, role):
    return hub("POST", "/api/login", {"name": name, "role": role, "mode": "teach"})["token"]


def wait(fn, what, timeout=None, every=2):
    t0 = time.time()
    while time.time() - t0 < (timeout or A.timeout):
        v = fn()
        if v:
            return v
        time.sleep(every)
    check(False, "等待超时：" + what)
    return None


def main():
    student = "测试学生" + time.strftime("%H%M%S")
    teacher = login("测试教师", "manager")
    print("1. 教师重置实验 7 情景")
    if not REAL:
        call("POST", A.erp + "/api/mock/reset")
    steel0 = None if not REAL else sum(b["actual_qty"] for b in erp_docs("Bin") if b["item_code"] == "RM-45-D50")
    hub("POST", "/api/scenario/reset", {"speed": 1, "scores": True}, teacher)
    ov = wait(lambda: (lambda o: o if o["demo"] and any(m["state"] == "down" for m in o["machines"]) else None)(
        hub("GET", "/api/overview", token=teacher)), "情景载入", 60)
    check(ov is not None, "情景载入：看板有演示数据，GRD-01 停机")

    mgr = login(student, "manager")
    print("2. 任务 1：读懂看板")
    r = hub("POST", "/api/teach/t1", {"machine": "grd-01", "order": "SAL-ORD-2026-00019", "material": "BRG-6207"}, mgr)
    check(r["score"] == 15, "任务 1 满分（{}）".format(r))

    print("3. 任务 2：接单与算料（计划员表单 → 提议 → 确认 → 桥接写入 ERPNext）")
    planner = login(student, "planner")
    pv = hub("POST", "/api/plan/order", {"customer": "示例·绿谷输送设备 GreenValley Conveyor (Demo)",
                                         "item": "WQR-105", "qty": 10, "delivery_date": delivery_date()}, planner)
    steel = next(r for r in pv["mrp"] if r["item_code"] == "RM-45-D50")
    check(pv["work_orders"][0]["qty"] == 10 and pv["work_orders"][0]["production_item"] == "SH-301", "算料：SH-301 工单 10 件")
    check(any(m["item_code"] == "RM-45-D50" for m in pv["material_requests"]),
          "算料：45 钢要请购（毛需求 {} kg，库存 {} kg，占用 {} kg）".format(steel["gross"], steel["stock"], steel["committed"]))
    check(any(m["item_code"] == "BRG-6207" for m in pv["material_requests"]), "算料：BRG-6207 要请购")
    p = hub("POST", "/api/proposals", {"customer": "示例·绿谷输送设备 GreenValley Conveyor (Demo)", "item": "WQR-105",
                                       "qty": 10, "delivery_date": delivery_date()}, planner)
    pid = p["proposal_id"]
    hub("POST", "/api/proposals/{}/confirm".format(pid), token=planner)
    prop = wait(lambda: (lambda x: x if x["status"] in ("executed", "failed") else None)(
        hub("GET", "/api/proposals/" + pid, token=planner)), "桥接执行提议", 60, 1)
    check(prop and prop["status"] == "executed", "提议已执行：{}".format(prop and prop.get("result")))
    wo = next(d["name"] for d in prop["results"] if d["doctype"] == "Work Order")
    so = next(d["name"] for d in prop["results"] if d["doctype"] == "Sales Order")
    print("   订单 {}，工单 {}".format(so, wo))
    st = hub("GET", "/api/teach", token=planner)
    check(st["tasks"][1]["score"] == 20, "任务 2 满分（{}）".format(st["tasks"][1]["score"]))

    print("4. 任务 3：工艺员发布新版设计（模拟 FreeCAD 宏）")
    sys.path[:0] = [__file__.rsplit("/tests/", 1)[0] + "/freecad"]
    import wq_publish  # noqa: E402
    eng = login(student, "engineer")
    res = wq_publish.publish(hub_url=A.hub, token=eng, author=student,
                             params={"segments": [[30, 40], [35, 12], [40, 60], [35, 25], [30, 30]],
                                     "chamfer": 1.5, "keyway": {"segment": 2, "b": 12.0, "t": 5.0, "L": 42.0}},
                             change_note="键槽长 45 → 42 mm", step_bytes=b"ISO-10303-21; (test)")
    check(res["revision"] >= 2, "发布 rev {}，G 代码 {} 行".format(res["revision"], res["gcode_lines"]))
    wait(lambda: any(d["name"] == "SH-301" and d.get("wq_revision") == res["revision"]
                     for d in erp_docs("Item")), "ERPNext 物料版本更新", 30, 1)
    item = next(d for d in erp_docs("Item") if d["name"] == "SH-301")
    check(item.get("wq_revision") == res["revision"], "ERPNext 里 SH-301 版本 = {}".format(item.get("wq_revision")))
    files = [f for f in erp_docs("File") if f["attached_to_name"] == "SH-301"]
    check(len(files) >= 2, "SH-301 附件 {} 个（STEP、G 代码…）".format(len(files)))
    st = hub("GET", "/api/teach", token=eng)
    check(st["tasks"][2]["score"] == 15, "任务 3 满分")
    alerts = hub("GET", "/api/overview", token=eng)["alerts"]
    check(any("设计改版" in a["title"] for a in alerts), "AI 提醒了设计改版的影响")

    print("5. 任务 4：下达车间，操作工逐道开工（仿真倍速 {:g}）".format(A.speed))
    hub("POST", "/api/mes/cmd", {"unit": "sim", "command": "set_speed", "speed": A.speed}, teacher)
    op = login(student, "operator")
    rel = hub("POST", "/api/mes/release", {"work_order": wo}, op)["dispatched"]
    check(len(rel) == 7, "下达 7 道工序")
    time.sleep(1)
    for d in rel:
        hub("POST", "/api/mes/cmd", {"unit": d["unit"], "command": "start", "work_order": wo, "operation": d["operation"]}, op)
    t0 = time.time()
    def finished():
        evs = [e for e in hub("GET", "/api/history?type=machine.event&corr={}&limit=500".format(wo), token=op)
               if e["data"]["event"] == "op_complete"]
        return evs if any(e["data"].get("last_op") for e in evs) else None
    done = wait(finished, "10 根轴全部完工", A.timeout, 3)
    print("   用时 {:.0f} 秒".format(time.time() - t0))
    check(done and len(done) == 7, "7 道工序全部完工")
    time.sleep(6)       # 等桥接把最后的入库写完
    st = hub("GET", "/api/teach", token=op)
    check(st["tasks"][3]["score"] == 20, "任务 4 满分")

    print("6. 核对{} ERPNext".format("真实" if REAL else "模拟"))
    jcs = [j for j in erp_docs("Job Card") if j["work_order"] == wo]
    check(len(jcs) == 7 and all(j["docstatus"] == 1 for j in jcs), "7 张作业卡全部提交")
    check(all(j["total_completed_qty"] == 10 for j in jcs), "每张作业卡完成 10 件")
    qis = [q for q in erp_docs("Quality Inspection") if any(q["reference_name"] == j["name"] for j in jcs)]
    check(len(qis) == 10, "每件一张质量检验单（{} 张）".format(len(qis)))
    good = sum(1 for q in qis if q["status"] == "Accepted")
    ses = [s for s in erp_docs("Stock Entry") if s.get("work_order") == wo and s["docstatus"] == 1]
    check(len(ses) == 1 and ses[0]["docstatus"] == 1 and ses[0]["fg_completed_qty"] == good,
          "完工入库 {} 件（合格数）".format(ses[0]["fg_completed_qty"] if ses else 0))
    wod = next(w for w in erp_docs("Work Order") if w["name"] == wo)
    check(wod["produced_qty"] == good, "工单完工数 {}".format(wod["produced_qty"]))
    bins = {b["item_code"]: b for b in erp_docs("Bin") if "原材料" in b["warehouse"] or "半成品" in b["warehouse"]}
    start = steel0 if REAL else 60
    check(abs(bins["RM-45-D50"]["actual_qty"] - (start - 2.8 * good)) < 1e-6,
          "45 钢扣料：{} → {} kg".format(start, bins["RM-45-D50"]["actual_qty"]))
    check(bins["SH-301"]["actual_qty"] == good, "SH-301 入库 {} 件".format(bins["SH-301"]["actual_qty"]))
    if not REAL:
        errs = erp("/api/mock/errors")["errors"]
        check(not errs, "ERPNext 字段校验无错误" + ("：" + "；".join(errs[:5]) if errs else ""))

    print("7. 任务 5、6：质检处置与成本分析")
    q = login(student, "quality")
    for n in hub("GET", "/api/ncr", token=q):
        if n["work_order"] == wo and n["status"] == "open":
            hub("POST", "/api/ncr/" + n["ncr_id"], {"disposition": "rework", "note": "返修：重新磨削"}, q)
    r = hub("POST", "/api/teach/t5", {"reason": "磨床砂轮逐渐磨损"}, q)
    check(r["score"] == 15, "任务 5 满分（{}）".format(r["feedback"]))
    cost = hub("GET", "/api/work_orders/{}/cost".format(wo), token=mgr)
    check(cost["actual_cost"] > cost["std_cost"] > 0, "成本：标准 ${} 实际 ${}（{:+}%）".format(
        cost["std_cost"], cost["actual_cost"], cost["variance_pct"]))
    r = hub("POST", "/api/teach/t6", {"variance_pct": cost["variance_pct"], "reason": "主要是调整和换刀时间"}, mgr)
    check(r["score"] == 15, "任务 6 满分")
    st = hub("GET", "/api/teach", token=mgr)
    check(st["score"] == 100, "实验 7 总分 {} / 100".format(st["score"]))

    print("8. 看板、AI 与总线")
    ov = hub("GET", "/api/overview", token=mgr)
    check(any(o["name"] == so for o in ov["orders"]), "看板“订单与交期”出现新订单 " + so)
    out = next(k for k in ov["kpis"] if k["key"] == "output")
    check(out["value"] >= good, "本周完工 {} 件（含本批 {}）".format(out["value"], good))
    ans = hub("POST", "/api/ai/chat", {"messages": [{"role": "user", "content": "{} 的实际成本比标准高多少？为什么？".format(wo)}]},
              mgr)
    check("提示" in ans["answer"] or "来源" in ans["answer"], "AI 回答（教学模式给提示）：" + ans["answer"][:60])
    bad = hub("GET", "/api/health")
    check(bad["ok"] and bad["bus"], "枢纽健康，历史库 {} 条消息".format(bad["messages"]))
    print()
    if FAILS:
        print("失败 {} 项：".format(len(FAILS)))
        for f in FAILS:
            print("  - " + f)
        sys.exit(1)
    print("完整闭环全部通过。")


if __name__ == "__main__":
    main()
