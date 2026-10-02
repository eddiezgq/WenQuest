# -*- coding: utf-8 -*-
"""MES（车间执行）：把工单下达到车间（逐工序派工）、转发车间终端的开工 / 暂停 / 复位。
工作台通过这里发 machine.cmd，不直接碰设备（附录 A.4 第 1 条）。"""
from sim.engine import OP_UNITS, routing_for
from wqbus import UNITS
from wqbus.topics import topic, unit_topic


class MES:
    def __init__(self, db, publish):
        self.db, self.publish = db, publish

    def work_order(self, name, mode):
        for w in self.db.erp_docs("Work Order", mode):
            if w["data"]["name"] == name:
                return w["data"]
        return None

    def release(self, name, mode, user, units=None):
        """下达：按工艺路线把每道工序派给默认设备（units 可指定 {工序: 设备}）。"""
        wo = self.work_order(name, mode)
        if wo is None:
            raise KeyError("找不到工单 " + name)
        if wo.get("docstatus", 1) != 1:
            raise ValueError("工单 {} 还没提交，不能下达".format(name))
        item = wo.get("production_item")
        from hub import process
        ops = process.active_routing(self.db, item=item, mode=mode) or routing_for(item)   # 生效的工艺规程优先（第 13 轮）
        sent = []
        for op, mins in ops:
            unit = (units or {}).get(op) or OP_UNITS[op][0]
            self.publish(unit_topic(unit, "cmd"), "machine.cmd", "mes/" + user,
                         {"command": "dispatch", "work_order": name, "operation": op, "qty": int(float(wo["qty"])),
                          "item": item, "routing": [list(x) for x in ops], "std_min": mins,
                          "gcode_ref": self.gcode_ref(item, op)}, name, mode)
            sent.append({"operation": op, "unit": unit, "name": UNITS[unit][1]})
        return sent

    def gcode_ref(self, item, op):
        if not op.startswith("铣键槽"):
            return None
        r = self.db.one("select payload from bus_message where type='design.gcode' and payload->'data'->>'item'=%s "
                        "order by ts desc limit 1", (item,))
        return r["payload"]["data"]["gcode_ref"] if r else None

    def command(self, unit, command, mode, user, work_order=None, operation=None, **extra):
        if unit == "sim":
            self.publish(topic("machining", "sim", "cmd"), "machine.cmd", "workbench/" + user,
                         dict({"command": command}, **extra), None, mode)
            return
        if unit not in UNITS:
            raise KeyError("没有这台设备：" + unit)
        data = {"command": command}
        if work_order:
            data["work_order"] = work_order
        if operation:
            data["operation"] = operation
        data.update(extra)
        self.publish(unit_topic(unit, "cmd"), "machine.cmd", "mes/" + user, data, work_order, mode)
