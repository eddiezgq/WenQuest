---
id: install
title: 安装
lead: 下载一个压缩包，复制一个文件夹，重启 FreeCAD。
---
<ol class="steps">
<li>安装 FreeCAD 1.1（官网 freecad.org）。</li>
<li>网页版“制造”或“三维与制造”页点“下载 → FreeCAD 工作台 .zip”。</li>
<li>把压缩包里的 <code>Mod/WenQuest</code> 文件夹复制到 FreeCAD 的用户 Mod 目录。目录在哪：在 FreeCAD 的 Python 控制台输入 <code>App.getUserAppDataDir()</code> 回车，显示的文件夹里的 <code>Mod</code>（没有就新建）。FreeCAD 1.1 一般是 Windows <code>%APPDATA%\FreeCAD\v1-1\Mod</code>，macOS <code>~/Library/Application Support/FreeCAD/v1-1/Mod</code>，Linux <code>~/.local/share/FreeCAD/v1-1/Mod</code>，以控制台显示的为准。已经装过问渠轴承或数字工厂的，解压到同一个 WenQuest 文件夹，各自的按钮都在。</li>
<li>重启 FreeCAD，工作台列表里选 <b>问渠</b>，点 <b>凸轮</b>。</li>
</ol>

缺 Python 包（scipy、shapely）时点“凸轮”会提示一条安装命令，整行粘贴到 FreeCAD 的 Python 控制台里运行（命令会自动找到 FreeCAD 自带的 Python，没有 pip 先补上，再装缺的包），装完重启 FreeCAD。压缩包里有示例项目（`examples`）和本帮助的离线一份（`Mod/WenQuest/cam-help/index.html`，不联网也能看）。

::video{src=fc-01-cam title="录像：安装工作台，打开槽凸轮示例"}
