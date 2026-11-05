---
id: console
title: 不开界面：控制台命令
lead: 在 FreeCAD 的 Python 控制台里一行跑完：校核、建模、导出。
---
```python
import wq_cam
wq_cam.run_headless("项目.json", "输出文件夹")
```

批量处理一批凸轮：

```python
import glob, os, wq_cam
for f in glob.glob("凸轮/*.json"):
    wq_cam.run_headless(f, os.path.join("输出", os.path.basename(f)[:-5]))
```
