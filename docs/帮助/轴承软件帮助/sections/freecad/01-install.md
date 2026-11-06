---
id: install
title: 安装
lead: 下载一个压缩包，复制一个文件夹，重启 FreeCAD。
---
<ol class="steps">
<li>安装 FreeCAD 1.1（官网 freecad.org）。它自带 numpy 和 scipy（1.9 以上），工作台不用另装别的。</li>
<li>网页版“零件图与三维”里点 <b>下载 FreeCAD 工作台</b>，或直接打开 <code>https://learn.wenquestrobotics.com/bearing/api/freecad.zip</code>。</li>
<li>把压缩包里的 <code>Mod/WenQuest</code> 文件夹复制到 FreeCAD 的用户 Mod 目录。目录在哪：在 FreeCAD 的 Python 控制台输入 <code>App.getUserAppDataDir()</code> 回车，显示的文件夹里的 <code>Mod</code>（没有就新建）。FreeCAD 1.1 一般是 Windows <code>%APPDATA%\FreeCAD\v1-1\Mod</code>，macOS <code>~/Library/Application Support/FreeCAD/v1-1/Mod</code>，Linux <code>~/.local/share/FreeCAD/v1-1/Mod</code>，以控制台显示的为准。已经装过问渠凸轮或数字工厂的，解压到同一个 WenQuest 文件夹，各自的按钮都在。</li>
<li>重启 FreeCAD，工作台列表里选 <b>问渠</b>，工具栏上点 <b>轴承</b>。</li>
</ol>

压缩包里还有示例项目（`examples/*.wqbearing.json`）和本帮助的离线一份。缺依赖时点“轴承”会提示安装命令。

::video{src=fc-01-bearing title="录像：安装工作台，打开示例、计算、建模"}
