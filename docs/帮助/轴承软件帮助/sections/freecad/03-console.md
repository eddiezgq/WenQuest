---
id: console
title: 不开界面：控制台命令
lead: 在 FreeCAD 的 Python 控制台里一行跑完：计算、建模、出图、工序简图。
---
```python
import wq_bearing
wq_bearing.run_headless("项目.wqbearing.json", "输出文件夹", "工艺模板.wqprocess.json")
```

不要工序简图时去掉第三个参数。输出文件夹里有校核结果、各零件的 STEP 和 A3 工作图（SVG），有工艺模板时还有工序简图。批量处理一个系列：

```python
import glob, os, wq_bearing
for f in glob.glob("系列/*.wqbearing.json"):
    wq_bearing.run_headless(f, os.path.join("输出", os.path.basename(f)[:-15]))
```
