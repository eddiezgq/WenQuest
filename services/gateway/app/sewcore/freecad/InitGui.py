# -*- coding: utf-8 -*-
# 问渠缝纫机工作台（第 39 轮）：在 FreeCAD 里做平缝机机构设计。计算核心与问渠网页版是同一份（sewcore），结果一致。
import FreeCADGui


class WenQuestSewingWorkbench(FreeCADGui.Workbench):
    MenuText = "问渠缝纫机"
    ToolTip = "问渠缝纫机设计：平缝机机构参数化设计、校核、时序、导出 STEP"

    def __init__(self):
        import os
        import FreeCAD
        for base in (FreeCAD.getUserAppDataDir(), FreeCAD.getHomePath()):
            p = os.path.join(base, "Mod", "WenQuestSewing", "wqsew.svg")
            if os.path.exists(p):
                self.__class__.Icon = p
                break

    def Initialize(self):
        import wqsew_gui
        cmds = wqsew_gui.register()
        self.appendToolbar("问渠缝纫机", cmds)
        self.appendMenu("问渠缝纫机", cmds)

    def GetClassName(self):
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(WenQuestSewingWorkbench())
