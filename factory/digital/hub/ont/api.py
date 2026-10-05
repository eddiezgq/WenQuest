# -*- coding: utf-8 -*-
"""本体 API（第 17 轮 A 期 A9）：本体定义、搜索、对象、关系图、时间线、对象集查询、血缘、同步状态。

权限（A14）：敏感级别 0 公开、1 内部、2 部门、3 受限。老师（教学）可看 3；生产模式的厂长、审批人可看 2；其他人看到 1。
超过级别的对象类型整个看不到，超过级别的属性不返回。"""
from fastapi import Body, Depends, HTTPException

from hub.ont import schema as S

MAX_NODES = 150


def level(u):
    if u.get("teacher") and u.get("mode") == "teach":
        return 3
    if u.get("teacher") or u.get("role") in ("manager", "approver"):
        return 2
    return 1


def mount(app, H, user_of):
    onto = S.get()

    def sens_type(t):
        return int(onto.types[t].get("sensitivity", 0) or 0)

    def visible(u, t):
        return t in onto.types and sens_type(t) <= level(u)

    def clean_props(u, t, props):
        lv, spec = level(u), onto.types[t]
        out = {}
        for p, v in (props or {}).items():
            ps = spec["props"].get(p)
            if ps is None or int(ps.get("s", spec.get("sensitivity", 0)) or 0) > lv:
                continue
            out[p] = v
        return out

    def node(u, r):
        t = r["type"]
        sp = onto.types[t]
        return {"id": t + "|" + r["key"], "type": t, "key": r["key"], "display": r["display"], "domain": sp["domain"],
                "label": sp["label"]}

    @app.get("/api/ont/types")
    def ont_types(u=Depends(user_of)):
        counts = {r["type"]: r["n"] for r in H.db.q("select type, count(*) as n from ont_object where mode=%s group by type", (u["mode"],))}
        recent = {r["type"]: r["n"] for r in H.db.q(
            "select type, count(*) as n from ont_event where mode=%s and ts > now() - interval '1 day' group by type", (u["mode"],))}
        doms = onto.public()
        for d in doms:
            d["types"] = [dict(t, count=counts.get(t["name"], 0), changes_24h=recent.get(t["name"], 0), hidden=not visible(u, t["name"]))
                          for t in d["types"]]
            d["count"] = sum(t["count"] for t in d["types"] if not t["hidden"])
            d["with_data"] = sum(1 for t in d["types"] if t["count"])
        return {"domains": doms, "maturity": S.MATURITY, "level": level(u)}

    @app.get("/api/ont/search")
    def ont_search(q: str = "", type: str = "", limit: int = 30, u=Depends(user_of)):
        q = q.strip()
        if not q:
            return {"results": []}
        limit = max(1, min(int(limit), 100))
        types = [t for t in onto.types if visible(u, t) and (not type or t == type)]
        hits, seen = [], set()

        def add(rows, how):
            for r in rows:
                k = (r["type"], r["key"])
                if k in seen or r["type"] not in types:
                    continue
                seen.add(k)
                hits.append(dict(node(u, r), how=how))
        add(H.db.q("select o.type, o.key, o.display from ont_alias a join ont_object o on o.mode=a.mode and o.type=a.type and o.key=a.key "
                   "where a.mode=%s and lower(a.alias)=lower(%s) limit 10", (u["mode"], q)), "别名")
        add(H.db.q("select type, key, display from ont_object where mode=%s and lower(key)=lower(%s) and type = any(%s) limit 10",
                   (u["mode"], q, types)), "编号")
        like = "%" + q.replace("%", r"\%").replace("_", r"\_") + "%"
        add(H.db.q("select type, key, display from ont_object where mode=%s and type = any(%s) and search ilike %s "
                   "order by length(key), key limit %s", (u["mode"], types, like, limit)), "包含")
        # 前面都没找到才做“相近”匹配（容错拼写），它在几十万对象时要零点几秒
        if not hits and H.ont is not None and getattr(H.ont.store, "trgm", False) and len(q) >= 3:
            add(H.db.q("select type, key, display from ont_object where mode=%s and type = any(%s) and search %% %s "
                       "order by similarity(search, %s) desc limit %s", (u["mode"], types, q, q, limit)), "相近")
        return {"results": hits[:limit]}

    def get_obj(u, t, key):
        if not visible(u, t):
            raise HTTPException(404, "没有这类对象，或你没有权限查看")
        r = H.db.one("select * from ont_object where mode=%s and type=%s and key=%s", (u["mode"], t, key))
        if r is None:
            raise HTTPException(404, "没有这个对象：{} {}".format(onto.types[t]["label"], key))
        return r

    @app.get("/api/ont/obj/{t}/{key:path}/graph")
    def ont_graph(t: str, key: str, depth: int = 1, u=Depends(user_of)):
        get_obj(u, t, key)
        depth = max(1, min(int(depth), 3))
        nodes, edges = {}, {}
        frontier = [(t, key)]
        start = H.db.one("select type, key, display from ont_object where mode=%s and type=%s and key=%s", (u["mode"], t, key))
        nodes[t + "|" + key] = dict(node(u, start), root=True, hop=0)
        for hop in range(1, depth + 1):
            nxt = []
            for ft, fk in frontier:
                rows = H.db.q("select * from ont_link where mode=%s and ((src_type=%s and src_key=%s) or (dst_type=%s and dst_key=%s)) limit 400",
                              (u["mode"], ft, fk, ft, fk))
                for lr in rows:
                    other = (lr["dst_type"], lr["dst_key"]) if (lr["src_type"], lr["src_key"]) == (ft, fk) else (lr["src_type"], lr["src_key"])
                    if not visible(u, other[0]):
                        continue
                    oid = other[0] + "|" + other[1]
                    if oid not in nodes:
                        if len(nodes) >= MAX_NODES:
                            continue
                        o = H.db.one("select type, key, display from ont_object where mode=%s and type=%s and key=%s",
                                     (u["mode"], other[0], other[1]))
                        nodes[oid] = dict(node(u, o) if o else {"id": oid, "type": other[0], "key": other[1], "display": other[1],
                                                                 "domain": onto.types[other[0]]["domain"], "label": onto.types[other[0]]["label"],
                                                                 "missing": True}, hop=hop)
                        nxt.append(other)
                    ls = onto.links[(lr["src_type"], lr["type"].split(".", 1)[1])]
                    eid = "{}>{}>{}".format(lr["type"], lr["src_type"] + "|" + lr["src_key"], lr["dst_type"] + "|" + lr["dst_key"])
                    edges[eid] = {"id": eid, "from": lr["src_type"] + "|" + lr["src_key"], "to": lr["dst_type"] + "|" + lr["dst_key"],
                                  "type": lr["type"], "label": ls["l"], "inverse": ls.get("inv", ""), "props": lr["props"], "seq": lr["src_seq"]}
            frontier = nxt
        return {"nodes": list(nodes.values()), "edges": [e for e in edges.values() if e["from"] in nodes and e["to"] in nodes],
                "truncated": len(nodes) >= MAX_NODES}

    @app.get("/api/ont/obj/{t}/{key:path}/timeline")
    def ont_timeline(t: str, key: str, limit: int = 300, u=Depends(user_of)):
        get_obj(u, t, key)
        rows = H.db.q("select ts, kind, text, changes, src_seq from ont_event where mode=%s and type=%s and key=%s order by ts desc, id desc limit %s",
                      (u["mode"], t, key, max(1, min(int(limit), 1000))))
        props = onto.types[t]["props"]
        out = []
        for r in rows:
            ch = clean_props(u, t, {k: v for k, v in (r["changes"] or {}).items()})
            out.append({"ts": r["ts"].isoformat(), "kind": r["kind"], "text": r["text"],
                        "changes": [{"prop": k, "label": props[k]["l"], "unit": props[k].get("u", ""), "old": v[0], "new": v[1]}
                                    for k, v in ch.items() if k in props],
                        "seq": r["src_seq"]})
        return {"events": out}

    @app.get("/api/ont/obj/{t}/{key:path}")
    def ont_obj(t: str, key: str, u=Depends(user_of)):
        r = get_obj(u, t, key)
        spec = onto.types[t]
        props = clean_props(u, t, r["props"])
        attrs = [{"name": p, "label": ps["l"], "type": ps["t"], "unit": ps.get("u", ""), "value": props.get(p),
                  "source": r["prop_src"].get(p)} for p, ps in spec["props"].items() if p in props]
        groups = []
        for (ft, ln), ls in onto.links.items():
            out_ = ft == t
            in_ = ls["to"] == t
            for direction in (["out"] if out_ else []) + (["in"] if in_ else []):
                other = ls["to"] if direction == "out" else ft
                if not visible(u, other):
                    continue
                if direction == "out":
                    rows = H.db.q("select l.dst_key as k, l.props, l.src_seq, o.display from ont_link l left join ont_object o on "
                                  "o.mode=l.mode and o.type=l.dst_type and o.key=l.dst_key where l.mode=%s and l.type=%s and l.src_key=%s "
                                  "order by l.ts desc nulls last limit 51", (u["mode"], ft + "." + ln, key))
                    label = ls["l"]
                else:
                    rows = H.db.q("select l.src_key as k, l.props, l.src_seq, o.display from ont_link l left join ont_object o on "
                                  "o.mode=l.mode and o.type=l.src_type and o.key=l.src_key where l.mode=%s and l.type=%s and l.dst_key=%s "
                                  "order by l.ts desc nulls last limit 51", (u["mode"], ft + "." + ln, key))
                    label = ls.get("inv") or ls["l"]
                if rows:
                    groups.append({"link": ft + "." + ln, "direction": direction, "label": label, "type": other,
                                   "type_label": onto.types[other]["label"], "more": len(rows) > 50,
                                   "items": [{"key": x["k"], "display": x["display"] or x["k"], "props": x["props"], "seq": x["src_seq"]}
                                             for x in rows[:50]]})
        aliases = [a["alias"] for a in H.db.q("select alias from ont_alias where mode=%s and type=%s and key=%s", (u["mode"], t, key))]
        return {"type": t, "key": key, "display": r["display"], "label": spec["label"], "label_en": spec.get("label_en", ""),
                "domain": spec["domain"], "maturity": spec["maturity"], "attrs": attrs, "links": groups, "aliases": aliases,
                "first_seq": r["first_seq"], "first_ts": r["first_ts"].isoformat() if r["first_ts"] else None,
                "updated_at": r["updated_at"].isoformat(), "sources": spec.get("sources", [])}

    @app.post("/api/ont/query")
    def ont_query(body: dict = Body(...), u=Depends(user_of)):
        """对象集：{type, where: [{prop, op(= != > < >= <= contains), value}], link: {name, key, direction}, limit}"""
        t = body.get("type")
        if not visible(u, t):
            raise HTTPException(404, "没有这类对象，或你没有权限查看")
        spec = onto.types[t]
        where, args = ["o.mode=%s", "o.type=%s"], [u["mode"], t]
        ops = {"=": "=", "!=": "<>", ">": ">", "<": "<", ">=": ">=", "<=": "<="}
        for w in body.get("where") or []:
            p, op, v = w.get("prop"), w.get("op", "="), w.get("value")
            if p not in spec["props"]:
                raise HTTPException(400, "{} 没有属性 {}".format(spec["label"], p))
            num = spec["props"][p]["t"] in ("num", "int")
            if op == "contains":
                where.append("o.props->>%s ilike %s")
                args += [p, "%" + str(v) + "%"]
            elif op in ops:
                where.append("({} {} %s)".format("(o.props->>%s)::float" if num else "o.props->>%s", ops[op]))
                args += [p, float(v) if num else str(v)]
            else:
                raise HTTPException(400, "不支持的条件 " + str(op))
        lk = body.get("link")
        if lk:
            ft, ln = (lk["name"].split(".", 1) + [""])[:2]
            if (ft, ln) not in onto.links:
                raise HTTPException(400, "没有链接 " + lk["name"])
            if lk.get("direction", "out") == "out":
                where.append("exists (select 1 from ont_link l where l.mode=o.mode and l.type=%s and l.src_key=o.key and l.dst_key=%s)")
            else:
                where.append("exists (select 1 from ont_link l where l.mode=o.mode and l.type=%s and l.dst_key=o.key and l.src_key=%s)")
            args += [lk["name"], lk["key"]]
        limit = max(1, min(int(body.get("limit", 500)), 5000))
        rows = H.db.q("select o.type, o.key, o.display, o.props from ont_object o where {} order by o.key limit %s".format(" and ".join(where)),
                      args + [limit])
        return {"type": t, "count": len(rows), "objects": [dict(node(u, r), props=clean_props(u, t, r["props"])) for r in rows]}

    @app.get("/api/ont/lineage/{seq}")
    def ont_lineage(seq: int, u=Depends(user_of)):
        r = H.db.one("select seq, ts, topic, type, mode, corr, payload from bus_message where seq=%s", (seq,))
        if r is None:
            raise HTTPException(404, "这条原始消息已经不在历史库里（可能已按保留天数清理）")
        if (r["mode"] or "teach") != u["mode"]:
            raise HTTPException(404, "不是当前模式的消息")
        return {"seq": r["seq"], "ts": r["ts"].isoformat(), "topic": r["topic"], "type": r["type"], "corr": r["corr"],
                "source": r["payload"].get("source"), "data": r["payload"].get("data")}

    @app.get("/api/ont/health")
    def ont_health(u=Depends(user_of)):
        return H.ont.health()

    @app.post("/api/ont/replay")
    def ont_replay(u=Depends(user_of)):
        if not (u.get("teacher") and u.get("role") == "manager"):
            raise HTTPException(403, "只有厂长（教师）可以重建本体")
        n = H.ont.replay(u["mode"])
        return dict(H.ont.health(), replayed=n)
