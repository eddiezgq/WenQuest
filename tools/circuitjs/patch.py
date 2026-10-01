"""给 CircuitJS1 源码打嵌入用的小补丁（第 7 轮第 6 步）。只改“从哪里取启动参数、取不取网络文件、怎样编译”，不改仿真。

    python3 tools/circuitjs/patch.py <circuitjs1 源码目录>

1. QueryParameters：外层页面可以用 window.CircuitJSQuery（形如 "?hideMenu=true&lang=zh"）给出启动参数，不必放在网址里；
2. 语言：window.CircuitJSLocaleText 有内容时直接用它，不联网取 locale_xx.txt；
3. 示例电路列表 setuplist.txt、右侧面板 iframe.html：window.CircuitJSEmbedded 为真时不取；
4. GWT 模块：单文件输出（sso 链接器、单一排列），样式不由 GWT 注入（由嵌入页内联）；
5. 编译选项：OBFUSCATED，减小体积。
每处改动都先确认原文存在，找不到就报错，避免上游改版后悄悄失效。
"""
import sys
from pathlib import Path

root = Path(sys.argv[1])
C = root / "src" / "com" / "lushprojects" / "circuitjs1"


def edit(path: Path, old: str, new: str) -> None:
    s = path.read_text(encoding="utf-8")
    if old not in s:
        sys.exit(f"patch: 在 {path} 中找不到要改的原文：{old[:80]!r}")
    path.write_text(s.replace(old, new, 1), encoding="utf-8")


edit(C / "client" / "QueryParameters.java",
     "          return $wnd.location.search;",
     "          return $wnd.CircuitJSQuery || $wnd.location.search;")

edit(C / "client" / "circuitjs1.java",
     "        url = GWT.getModuleBaseURL() + \"locale_\" + lang + \".txt\";",
     "        String inline = embeddedLocale();\n"
     "        if (inline != null) {\n"
     "            loadSimulator(processLocale(inline));\n"
     "            return;\n"
     "        }\n"
     "        url = GWT.getModuleBaseURL() + \"locale_\" + lang + \".txt\";")
edit(C / "client" / "circuitjs1.java",
     "    void loadLocale() {",
     "    static native String embeddedLocale() /*-{ return $wnd.CircuitJSLocaleText || null; }-*/;\n\n"
     "    static native boolean embedded() /*-{ return !!$wnd.CircuitJSEmbedded; }-*/;\n\n"
     "    void loadLocale() {")

edit(C / "client" / "Menus.java",
     "    void getSetupList(final boolean openDefault) {\n",
     "    void getSetupList(final boolean openDefault) {\n\tif (circuitjs1.embedded()) return;\n")

edit(C / "client" / "UIManager.java",
     "verticalPanel.add(iFrame = new Frame(\"iframe.html\"));",
     "verticalPanel.add(iFrame = new Frame(circuitjs1.embedded() ? \"about:blank\" : \"iframe.html\"));")

gwt = C / "circuitjs1.gwt.xml"
edit(gwt, "<inherits name='com.google.gwt.user.theme.clean.Clean'/>",
     "<inherits name='com.google.gwt.user.theme.clean.CleanResources'/>")
edit(gwt, "<stylesheet src='style.css' />", "<!-- style.css 由嵌入页内联 -->")
edit(gwt, "</module>",
     "    <add-linker name=\"sso\" />\n    <collapse-all-properties />\n</module>")

edit(root / "build.gradle", "style = \"PRETTY\"", "style = \"OBFUSCATED\"")
print("patch: 完成")
