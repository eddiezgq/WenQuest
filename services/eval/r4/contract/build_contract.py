"""问渠数据契约 v1：JSON Schema、样例数据包、校验程序。"""
import json, hashlib, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import attainment as A
from jsonschema import Draft202012Validator

num01 = {"type": "number", "minimum": 0, "maximum": 1}
evidence = {"type": "object", "required": ["url", "scope"], "additionalProperties": False, "properties": {
    "url": {"type": "string", "pattern": "^https://"},
    "scope": {"enum": ["课程负责人", "任课教师", "评估办", "辅导员", "教师本人"]}}}
offering = {"type": "object", "required": ["course_code", "term", "offering_id"], "additionalProperties": False, "properties": {
    "course_code": {"type": "string", "description": "教务系统课程代码，用于与培养方案对接"},
    "term": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{4}-[12]$"},
    "offering_id": {"type": "string"}, "course_name": {"type": "string"}}}
provenance = {"type": "object", "required": ["method", "method_version", "snapshot_id"], "additionalProperties": False, "properties": {
    "method": {"type": "string"}, "method_version": {"type": "string"}, "snapshot_id": {"type": "string"}}}

def rec(kind, props, req, privacy="汇总"):
    base = {"kind": {"const": kind}, "privacy": {"const": privacy}, "offering": offering, "provenance": provenance}
    return {"type": "object", "additionalProperties": False, "required": ["kind", "privacy", "offering", "provenance"] + req,
            "properties": {**base, **props}}

attain = rec("course_objective_attainment", {
    "n_students": {"type": "integer", "minimum": 1},
    "threshold": num01, "student_pass_line": num01,
    "objectives": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": False,
        "required": ["co_id", "name", "direct", "achieved", "student_pass_rate", "indirect", "components", "evidence"],
        "properties": {"co_id": {"type": "string"}, "name": {"type": "string"}, "direct": num01, "achieved": {"type": "boolean"},
            "student_pass_rate": num01, "indirect": {"oneOf": [num01, {"type": "null"}]},
            "components": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                "required": ["name", "weight", "rate"], "properties": {"name": {"type": "string"}, "weight": num01, "rate": num01}}},
            "weak_items": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                "required": ["item_id", "label", "rate"], "properties": {"item_id": {"type": "string"}, "label": {"type": "string"}, "rate": num01}}},
            "evidence": evidence}}}}, ["n_students", "threshold", "student_pass_line", "objectives"])
gain = rec("learning_gain", {
    "n_students": {"type": "integer", "minimum": 15, "description": "少于 15 人不推送（上篇 3.3）"},
    "pre_mean": {"type": "number"}, "post_mean": {"type": "number"}, "gain": {"type": "number"},
    "by_kp": {"type": "array", "items": {"type": "object", "required": ["kp_id", "gain"], "additionalProperties": False,
        "properties": {"kp_id": {"type": "string"}, "label": {"type": "string"}, "gain": {"type": "number"}}}}},
    ["n_students", "pre_mean", "post_mean", "gain"])
feedback = rec("feedback_themes", {
    "n_responses": {"type": "integer", "minimum": 5, "description": "少于 5 份不推送（上篇 3.4）"},
    "round": {"enum": ["期末"], "description": "期中评教只给教师本人，不推送（H3）"},
    "themes": {"type": "array", "items": {"type": "object", "required": ["theme", "count", "tone"], "additionalProperties": False,
        "properties": {"theme": {"type": "string"}, "count": {"type": "integer", "minimum": 1}, "tone": {"enum": ["正面", "负面", "建议"]}}}}},
    ["n_responses", "round", "themes"])
risk = rec("student_risk", {
    "student_ref": {"type": "string", "description": "学号，仅在有权限的预警视图中解析"},
    "purpose": {"const": "学业预警与辅导"},
    "visible_to": {"type": "array", "items": {"enum": ["任课教师", "辅导员"]}, "minItems": 1},
    "signals": {"type": "array", "minItems": 1, "items": {"type": "object", "required": ["type", "detail"], "additionalProperties": False,
        "properties": {"type": {"enum": ["知识点未掌握", "作业缺交", "实验未完成", "答辩未通过", "长期未登录"]}, "detail": {"type": "string"}}}},
    "expires": {"type": "string", "format": "date"}}, ["student_ref", "purpose", "visible_to", "signals", "expires"], privacy="个人")
receipt = rec("task_receipt", {
    "task_id": {"type": "string"}, "status": {"enum": ["已接收", "进行中", "已完成", "退回说明"]},
    "note": {"type": "string"}, "evidence": evidence}, ["task_id", "status"])
task = {"type": "object", "additionalProperties": False, "required": ["kind", "task_id", "offering", "target", "reason", "due"],
    "properties": {"kind": {"const": "improvement_task"}, "task_id": {"type": "string"}, "offering": offering,
        "target": {"type": "string", "description": "课程目标或指标点"}, "reason": {"type": "string"},
        "suggested_actions": {"type": "array", "items": {"type": "string"}}, "due": {"type": "string", "format": "date"}}}

schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "wenquest-contract-v1",
  "title": "问渠数据契约 v1（问渠 ⇄ 校情中枢）", "type": "object", "additionalProperties": False,
  "required": ["contract_version", "direction", "school_id", "source", "generated_at", "batch_id", "records"],
  "properties": {"contract_version": {"const": "1.0"}, "direction": {"enum": ["问渠→校情中枢", "校情中枢→问渠"]},
    "school_id": {"type": "string"}, "source": {"type": "string"}, "generated_at": {"type": "string", "format": "date-time"},
    "batch_id": {"type": "string", "description": "幂等键：同一批次重复推送只处理一次"},
    "records": {"type": "array", "items": {"oneOf": [attain, gain, feedback, risk, receipt, task]}}}}

R = A.result; off = {"course_code": "PHY1101", "term": "2026-2027-1", "offering_id": "PHY1101-01", "course_name": "大学物理（上）"}
prov = {"method": "课程目标达成度：环节加权（第4轮第1步）", "method_version": "1.0", "snapshot_id": "snap-2026-2027-1-final"}
base_url = "https://wenquest.example.cn/evidence/PHY1101-01"
objs = []
for co, it in R["课程目标"].items():
    weak = it.get("追溯：得分率最低的考核项", [])
    o = {"co_id": co, "name": it["名称"], "direct": it["直接评价达成度"], "achieved": it["是否达成"],
         "student_pass_rate": it["学生个人达成比例"], "indirect": it["间接评价（学生自评）"],
         "components": [{"name": p["环节"], "weight": p["权重"], "rate": p["得分率"]} for p in it["环节"]],
         "evidence": {"url": f"{base_url}/{co}", "scope": "课程负责人"}}
    if weak: o["weak_items"] = [{"item_id": w["考核项"], "label": w["说明"], "rate": w["得分率"]} for w in weak]
    objs.append(o)
payload = {"contract_version": "1.0", "direction": "问渠→校情中枢", "school_id": "SCH-DEMO", "source": "wenquest",
  "generated_at": "2027-01-20T10:00:00+08:00", "batch_id": "", "records": [
   {"kind": "course_objective_attainment", "privacy": "汇总", "offering": off, "provenance": prov,
    "n_students": len(A.students), "threshold": A.THRESHOLD, "student_pass_line": A.STU_PASS, "objectives": objs},
   {"kind": "learning_gain", "privacy": "汇总", "offering": off, "provenance": {**prov, "method": "掌握度增值：期初诊断 vs 期末"},
    "n_students": 40, "pre_mean": 0.21, "post_mean": 0.88, "gain": 0.67,
    "by_kp": [{"kp_id": "P1-1.3-c", "label": "出手误差的灵敏度", "gain": 0.18}, {"kp_id": "P1-1.3-b", "label": "按目标求初速度", "gain": 0.92}]},
   {"kind": "feedback_themes", "privacy": "汇总", "offering": off, "provenance": {**prov, "method": "期末评教留言主题归类"},
    "n_responses": 33, "round": "期末", "themes": [{"theme": "虚拟实验有助于理解", "count": 14, "tone": "正面"},
       {"theme": "灵敏度分析讲得太快", "count": 9, "tone": "负面"}, {"theme": "希望多给建模练习", "count": 6, "tone": "建议"}]},
   {"kind": "student_risk", "privacy": "个人", "offering": off, "provenance": {**prov, "method": "学业预警规则 v0"},
    "student_ref": "S017", "purpose": "学业预警与辅导", "visible_to": ["任课教师", "辅导员"],
    "signals": [{"type": "知识点未掌握", "detail": "P1-1.3-c、P1-1.2-b 两次小测均为未掌握"}], "expires": "2027-03-01"}]}
body = json.dumps(payload["records"], ensure_ascii=False, sort_keys=True)
payload["batch_id"] = "WQ-" + hashlib.sha256(body.encode()).hexdigest()[:16]
back = {"contract_version": "1.0", "direction": "校情中枢→问渠", "school_id": "SCH-DEMO", "source": "xiaoqing",
  "generated_at": "2027-01-25T09:00:00+08:00", "batch_id": "XQ-0001", "records": [
   {"kind": "improvement_task", "task_id": "T-2027-001", "offering": off, "target": "CO2 / 指标点 2.1 问题分析",
    "reason": "CO2 直接评价 0.698，低于阈值 0.70；追溯到 P1-1.3-c（0.428）、LAB-1.2 建模（0.482）、P1-1.2-b（0.527）",
    "suggested_actions": ["1.3 节增加灵敏度分析练习", "实验 1.2 加强运行前预测的指导"], "due": "2027-06-30"}]}

json.dump(schema, open("contract/wenquest_contract_v1.schema.json", "w"), ensure_ascii=False, indent=1)
json.dump(payload, open("contract/sample_push.json", "w"), ensure_ascii=False, indent=1)
json.dump(back, open("contract/sample_task.json", "w"), ensure_ascii=False, indent=1)

V = Draft202012Validator(schema)
def check(name, d):
    errs = sorted(V.iter_errors(d), key=lambda e: list(e.path))
    print(name, "通过" if not errs else f"不通过：{len(errs)} 处")
    return errs
check("问渠推送样例", payload); check("改进任务样例", back)
# 反例：边界规则必须被拦下
bad = json.loads(json.dumps(payload))
bad["records"][1]["n_students"] = 9                      # 少于 15 人
bad["records"][2]["round"] = "期中"                       # 期中评教不得推送
bad["records"][3]["visible_to"] = ["评估办"]              # 个人数据给了评估办
bad["records"].append({"kind": "teacher_report", "privacy": "个人"})   # 教师个人报告
errs = check("反例（应不通过）", bad)
print("拦下的规则：", len(errs) >= 4)
