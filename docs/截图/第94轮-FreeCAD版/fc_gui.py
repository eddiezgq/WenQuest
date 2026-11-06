import sys, os
MOD = os.environ["WQMOD"]; OUT = os.environ["WQOUT"]
sys.path.insert(0, MOD)
import FreeCAD as App, FreeCADGui as Gui
import wqsew_feature as F
import wqsew_gui as G
try:
    G.register()
except Exception as e:
    App.Console.PrintError(str(e))
BAD = {"lockstitch": {"n": 6000}, "overlock": {"n": 9000}, "cover": {"dphi": 40}, "pattern": {"n": 3000},
       "embroid": {"n": 1400}, "flatknit": {"sys": 2, "xfer": 4, "rack": 4, "dwell": 0.01}}
log = open(os.path.join(OUT, "gui_log.txt"), "w")
for m, p in BAD.items():
    try:
        doc = App.newDocument("G_" + m)
        o = F.add_design(doc, params=p, machine=m)
        Gui.activeDocument().activeView().viewIsometric()
        Gui.activeDocument().activeView().fitAll()
        Gui.updateGui()
        hs = F.hotspots(o)
        h = next((h for h in hs if h["phi"] is not None), hs[0] if hs else None)
        msg = G.goto(o, h["key"]) if h else ""
        Gui.Selection.clearSelection()          # 截图看涂色，不要选中的绿色
        Gui.updateGui()
        v = Gui.activeDocument().activeView()
        v.saveImage(os.path.join(OUT, "fc-94-%s.png" % m), 1400, 900, "White")
        log.write("%s ok %s\n" % (m, ascii(msg)))
    except Exception as e:
        import traceback
        log.write("%s FAIL %s\n" % (m, traceback.format_exc()))
    log.flush()
try:
    d = G.VideoDialog(o)
    d.show(); Gui.updateGui()
    d.grab().save(os.path.join(OUT, "fc-94-video-dialog.png"))
    QtW = G.QtW
    # 校核结果：不弹模态，照 show_checks 的样子截一张（替换 exec 为不阻塞）
    orig = QtW.QDialog.exec_ if hasattr(QtW.QDialog, "exec_") else None
    shots = []
    def fake_exec(self):
        Gui.updateGui(); shots.append(self.grab()); return 0
    QtW.QDialog.exec_ = fake_exec; QtW.QDialog.exec = fake_exec
    doc = App.newDocument("G_checks"); o2 = F.add_design(doc, params={"n": 3000}, machine="pattern")
    G.show_checks(o2)
    shots[0].save(os.path.join(OUT, "fc-94-checks.png"))
    log.write("dialogs ok\n")
except Exception:
    import traceback; log.write(traceback.format_exc())
log.write("DONE\n"); log.close()
os._exit(0)
