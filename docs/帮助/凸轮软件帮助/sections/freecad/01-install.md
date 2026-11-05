---
id: install
title: 安装
lead: 下载一个压缩包，复制一个文件夹，重启 FreeCAD。
---
<ol class="steps">
<li>安装 FreeCAD 1.1（官网 freecad.org）。</li>
<li>网页版“制造”或“三维与制造”页点“下载 → FreeCAD 工作台 .zip”。</li>
<li>把压缩包里的 <code>Mod/WenQuest</code> 文件夹复制到 FreeCAD 的用户 Mod 目录：Windows <code>%APPDATA%\FreeCAD\Mod</code>，macOS <code>~/Library/Application Support/FreeCAD/Mod</code>，Linux <code>~/.local/share/FreeCAD/Mod</code>。已经装过问渠轴承或数字工厂的，解压到同一个 WenQuest 文件夹，各自的按钮都在。</li>
<li>重启 FreeCAD，工作台列表里选 <b>问渠</b>，点 <b>凸轮</b>。</li>
</ol>

缺 Python 包（scipy、shapely）时点“凸轮”会提示一条安装命令，照着在 FreeCAD 的 Python 控制台里运行即可。压缩包里有示例项目（`examples`）和本帮助的离线一份（`Mod/WenQuest/cam-help/index.html`，不联网也能看）。
