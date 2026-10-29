---
id: console
title: 联网与控制台
lead: 钥匙怎么填；在 Python 控制台里批量算、批量导出。
---
### 联网：钥匙 {#key}

AI 助手和插入本单位零件要知道“你是谁、哪个单位”。网页版登录后：“缝纫机设计 → 零件库 → FreeCAD 钥匙 → 生成钥匙”，复制。FreeCAD 里第一次点“AI 助手”或“插入本单位零件”会弹出“设置钥匙”，粘贴进去，确定。钥匙只存在本机的 FreeCAD 设置里。

- 服务器地址默认 `https://learn.wenquestrobotics.com`；国内部署或单位自建服务器时，在同一个对话框里改。
- 钥匙每人一把，只显示一次；丢了就在网页版重新生成（旧的作废），再填一次。
- 钥匙只能读本单位零件库、下载零件 STEP、用 AI 助手。

### 在控制台里用

菜单“视图 → 面板 → Python 控制台”。工作台装好后，下面这些命令可以直接用（都在 FreeCAD 1.0.2 里实际跑过）：

```python
import wqsew_feature as F
d = F.add_design(machine="lockstitch")        # 新建平缝机设计（overlock / cover / pattern / embroid）
d.P_n = 6000                                  # 改转速；参数名都是 P_ 加网页版的参数键
App.ActiveDocument.recompute()
print(d.Status)                               # 不合格 {{n_bad6}} 项，注意 {{n_warn6}} 项
print([c["name"]["zh"] for c in F.result(d)["checks"] if c["state"] == "bad"])
```

一次改几个参数并重算（AI 助手的“采用”用的就是它）：

```python
F.apply_params(d, {"mr": 0.10, "fn": 240})    # 针杆组件减到 0.10 kg，机壳一阶固有频率提到 240 Hz
print(d.Status)                               # 全部合格
```

导出 STEP、参数文件：

```python
F.export_step(d, "D:/work/平缝机-6000.step")
F.export_params(d, "D:/work/平缝机-6000.wqsew.json")
```

批量比较几组转速：

```python
for n in (4500, 5000, 5500, 6000):
    d.P_n = n
    App.ActiveDocument.recompute()
    print(n, d.Status)
```

本机有限元（Gmsh + CalculiX）见“复杂 CAE 快速上手”最后一小节：`import wqsew_fem; wqsew_fem.run()`。
