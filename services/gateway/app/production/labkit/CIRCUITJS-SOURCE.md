# circuitjs-embed.html 的来源

`circuitjs-embed.html` 是电路仿真器 CircuitJS1 的单文件嵌入版，供“电路”虚拟实验（`view: "circuit"`）使用。

- 原作者：Paul Falstad、Iain Sharp。许可证：GNU GPL 第 2 版（见上游仓库的 COPYING.txt）。
- 上游源码：https://github.com/pfalstad/circuitjs1 ，提交号见 `tools/circuitjs/COMMIT`。
- 我们的改动只为嵌入：启动参数和起始电路由外层页面给出；内嵌中文界面文字；不联网取示例电路、语言文件和侧栏页面；编译成一个文件。具体改动见 `tools/circuitjs/patch.py`，打包见 `tools/circuitjs/bundle.py`。
- 编译：GitHub 任务 `.github/workflows/circuitjs.yml` 运行 `tools/circuitjs/build.sh`，结果发布为 `circuitjs-<提交>-<补丁指纹>` 附件。更新时下载该附件替换本文件。
