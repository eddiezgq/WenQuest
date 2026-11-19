# 问渠 CAD 培训课程录屏（fcrec）

真软件录屏：云端 Linux 上的 FreeCAD 1.1.4（官方 AppImage 解开）+ 问渠 CAD 品牌（`wenquest-cad/branding.xml` 拷到 `usr/bin/`）+ AI 工作台（freecad-ai-parts 固定提交，`--standalone` 装进 `~/.local/share/WenQuest CAD/v1-1/Mod`），界面中文。Xvfb 1600×900，ffmpeg x11grab 25 帧实录；剧本里按时间表操作，鼠标平滑移动，点击处事后叠黄圈（`rings.py`）。

```bash
export WQ_REC=/某个工作目录 FC=/解开的/squashfs-root WQLS_TE=/整机STEP目录
Xvfb :77 -screen 0 1600x900x24 &
$FC/usr/bin/freecadcmd build_model.py              # 110 个 STEP + 机壳 STL → model/WQ-LS.FCStd（按八个部件分组）
HOME=$WQ_REC/home DISPLAY=:77 $FC/AppRun color.py  # 上色、机壳半透明
./rec.sh l01.py 输出.mp4                            # 第 1 课试录
```
- 第一次启动要先在 `$WQ_REC/home/.config/WenQuest CAD/v1-1/user.cfg` 里把 `Language` 设成 `Chinese (Simplified)`，并关掉“首次启动设置”（`Mod/Start` 的 `FirstStart2024=0`）。
- 只差 27 个内核补丁（补丁不改界面）；“检查几何”“展开面”两处结果不同，不录屏（细则 D-5）。
