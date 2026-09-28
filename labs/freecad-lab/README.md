# WenQuest FreeCAD Lab：用 Python 驱动 FreeCAD

边写代码边熟悉 FreeCAD。每个宏都是一个参数化零件：改几个数，运行一次，就得到新零件，同时导出 STEP（给其他 CAD 用）和 STL（给 3D 打印用）。这也是以后平台上机械类虚拟实验的后台做法。

| 文件 | 内容 |
| --- | --- |
| `macros/wq_gear.py` | 渐开线直齿圆柱齿轮：按模数、齿数、压力角生成真实渐开线齿廓，报告分度圆、基圆、齿顶厚，并提示根切 |
| `macros/wq_shaft.py` | 阶梯轴：任意段数，两端倒角，一个平键槽，带键槽尺寸校核 |
| `tests/test_geometry.py` | 几何计算的自动测试（不需要 FreeCAD），数值与教科书公式对照 |

## 一、安装（Windows，约 20 分钟）

1. **FreeCAD 1.1.3**：从 [freecad.org](https://www.freecad.org/downloads.php) 下载 Windows 安装包，默认安装。首次打开时在首选项里可把语言改成简体中文。
2. **Python 3.12**：从 [python.org](https://www.python.org/downloads/windows/) 下载安装，**勾选 “Add python.exe to PATH”**。它用来跑测试和给 VS Code 提供 FreeCAD 的代码补全；宏本身在 FreeCAD 自带的 Python 里运行。
3. 把本文件夹解压到比如 `D:\code\freecad-lab`，在 PowerShell 里执行：

   ```powershell
   cd D:\code\freecad-lab
   py -m pip install -r requirements-dev.txt
   code .
   ```

   VS Code 右下角提示安装推荐扩展时，点“安装”。装了 `freecad-stubs` 后，写 `Part.` 就会弹出函数提示。

## 二、在 FreeCAD 里运行宏

1. FreeCAD 菜单 **宏 → 宏…**，在对话框下方把“用户宏位置”改成 `D:\code\freecad-lab\macros`。
2. 列表里出现 `wq_gear.py` 和 `wq_shaft.py`，选中一个，点 **执行**。
3. 打开 **视图 → 面板 → 报告视图**，可以看到齿轮尺寸、体积和导出文件的位置（在 `C:\Users\<你>\freecad-lab-output\`）。

**边改边看的循环**：在 VS Code 里改 `PARAMS`（比如齿数 24 改成 12），保存 → 回到 FreeCAD 再执行一次宏。新零件会加进当前文档；想重新开始就先关掉旧文档。

## 三、不开界面批量运行

以后在服务器上生成模型就是这样跑的：

```powershell
& "C:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe" macros\wq_gear.py
```

安装路径不同的话，把引号里的路径换成你电脑上 FreeCAD 的 `bin` 文件夹。

## 四、跑测试

```powershell
py -m pytest tests
```

也可以在 VS Code 左侧的“测试”（烧杯图标）里点运行。改了几何计算后先跑测试，全部通过再到 FreeCAD 里建模。

## 五、练习（由浅入深）

1. **根切**：把齿数改成 12，看报告视图里的根切提示，想一想正变位要改哪个尺寸。
2. **齿轮副**：给 `wq_gear.py` 加一个从动轮，齿数 36，中心距 a = m(z₁ + z₂)/2，放在正确位置，并转半个齿距让两轮啮合不干涉。
3. **键槽查表**：按 GB/T 1095 把阶梯轴第 4 段（d = 35）的键槽也加上，并在 `check_keyway` 里加一条“槽长不小于 1.5 倍键宽”的检查，再写一个测试。
4. **对照手工建模**：在 Part Design 工作台里用草图 + 凸台手工画同一根阶梯轴，比较体积是否一致，体会“脚本建模”和“界面建模”各自的长处。
5. **有限元初体验**：在 FEM 工作台里对一根 20×20×200 mm 的钢制悬臂梁端部加 1000 N，求端部挠度，与公式 δ = PL³/(3EI) 对照。这就是以后“材料力学”虚拟实验的原型。

## 说明

- 本工具包里的纯几何计算已通过测试；调用 FreeCAD 的部分按 FreeCAD 1.1 的接口编写，但尚未在 FreeCAD 里实际运行过。第一次运行如果报错，把报告视图里的红色信息发给 Claude 修正。
- 齿轮宏按标准齿轮建模，不包含根切过渡曲线和齿根圆角，适合学习和展示，不作为加工图纸。
