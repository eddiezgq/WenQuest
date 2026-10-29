---
id: install
title: 安装
lead: 只做一次：把工作台文件夹复制进 FreeCAD 的 Mod 文件夹，重启。
---
要求：FreeCAD 1.0 及以上（Windows、macOS、Linux）。安装包在网页版“缝纫机设计 → 导出 → 下载 FreeCAD 工作台”（已开通的企业账号），文件名“问渠缝纫机-FreeCAD工作台.zip”。

<ol class="steps">
<li>打开 FreeCAD，菜单“视图 → 面板 → Python 控制台”，输入下面一行回车，显示的就是用户数据文件夹。</li>
</ol>

```python
App.getUserAppDataDir()
```

<ol class="steps" start="2">
<li>在这个文件夹里找到（没有就新建）<code>Mod</code> 文件夹。</li>
<li>把压缩包里的 <code>Mod\WenQuestSewing</code> 整个文件夹复制进去，结果应是 <code>…\Mod\WenQuestSewing\InitGui.py</code>。</li>
<li>重启 FreeCAD，在工作台下拉列表里选“问渠缝纫机”。工具栏出现 17 个中文按钮。</li>
</ol>

::video{src=fc-01-install title="安装：找到用户数据文件夹，复制工作台，重启后选“问渠缝纫机”"}

**更新**：下载新的安装包，把旧的 `WenQuestSewing` 文件夹整个换掉，重启。
