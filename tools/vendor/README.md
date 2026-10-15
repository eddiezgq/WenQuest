# 字体与外部库本地化（第 34 轮）

国内访问不了 Google Fonts、cdnjs 慢，所以上线页面的字体和 three.js、KaTeX、Verilog 实验的仿真器都由自己的服务器在 `/vendor/` 提供：

- `package.json` / `package-lock.json`：锁定版本的字体（@fontsource）和库。
- `build.py`：生成 `site/vendor/`（不进仓库，约 29 MB）。部署时由 `deploy.sh` 生成并复制到服务器，版本没变不复制。
- `localize.py`：把页面里的 Google Fonts、cdnjs 链接改成 `/vendor/...`（脚本带回退：本机打开存下来的页面时再试原 CDN）。
- `check_external.py`：CI 测试里跑，上线页面再出现 Google Fonts / 公共 CDN 地址就报错。

新页面要用字体：写 `<link rel="stylesheet" href="/vendor/fonts/noto-sans-sc.css">`（可用的字体见 `build.py` 的 `FONTS`）；或照旧写 Google Fonts 链接后运行 `python3 tools/vendor/localize.py <文件>`。

本地预览：`cd tools/vendor && npm ci --ignore-scripts && python3 build.py`，再用任何静态服务器从仓库的 `site/` 打开。
