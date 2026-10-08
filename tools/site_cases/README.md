# 官网“典型应用”案例页

生成 `site/cases/`：`index.html`（总览）、`cobot-joint.html`、`scara.html`、`lockstitch.html`，中英一页切换（与首页共用语言设置 `wq-site-lang`）。第 27 轮细则“三之三”。

```bash
python3 tools/site_cases/build.py                      # 改了 cases.py / style.css / page.js 后重新生成
python3 tools/site_cases/build.py --preview <目录>     # 另出一份去掉 <head> 外壳的总览预览稿
```

- `cases.py`：全部文字与数字（中英成对）。数字只能取自 freecad-ai-parts 仓库 `examples/apps/out/<应用>/README.md` 和 `factory_flow/README.md`；改数前先核对。
- `assets/<slug>.mesh.json`：页面三维模型，由演练产出的 STEP 用 build123d 三角化（`tessellate`，公差 0.08–0.3 mm）得到；`assets/<slug>.layout.png`：FreeCAD 布局截图；`assets/three.min.js`：three.js r128（本站自带，国内访问不依赖外部 CDN）。
- 演练重跑、数字有变时：更新 `cases.py`，必要时重新三角化 STEP，再运行 `build.py`，提交 `site/cases/`。

还没做：每个案例 60–90 秒录屏短片（要在工厂里真实走一遍再录）；减速器厂的专题案例页。
