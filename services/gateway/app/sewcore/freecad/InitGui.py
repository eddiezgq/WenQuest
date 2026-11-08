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
        # 第 109 轮：装了“问渠 PLM”插件（WenQuestPLM，在质量 ERP 仓库 freecad/ 下），就多“推送到 PLM”“问渠 PLM 设置”两个按钮
        try:
            import wqplm_net  # noqa: F401
            plm = [c for c in ("WQPLM_Push", "WQPLM_Settings") if c in FreeCADGui.listCommands()]
            if plm:
                self.appendToolbar("问渠 PLM", plm)
                self.appendMenu("问渠 PLM", plm)
        except ImportError:
            pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(WenQuestSewingWorkbench())
