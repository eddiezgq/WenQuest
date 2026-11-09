# 阶段 C2：问渠ERP 附件在线编辑——交接草稿（给 wenquest-ops 仓库）

日期：2026-11-09（第 128 轮写，Eddie 已定范围：只做质量 ERP，每家试点企业；教学用的数字工厂 ERPNext 只读打开）
状态：草稿。在 `eddiezgq/wenquest-ops` 仓库开一轮细则，按那边的规矩确认后施工；本仓库只改 Caddy / 部署接口（见第四节）。

## 一、要做成什么

问渠ERP（WenQuest Ops + ERPNext v16）里，附件是 docx / xlsx / pptx 时多一个 **“在线编辑”**：用本服务器的 OnlyOffice（`learn.<域名>/docs/`，第 121 轮已上线）在浏览器里打开，多人同时改，关掉后新文件存回这个附件（ERPNext 留旧版本）。其余格式照旧下载。

## 二、现状（本仓库能看到的）

- 质量 ERP：国内 `/opt/wenquest/qms`（演示 `qms-demo-edge`）、美国 `/opt/wenquest/qms`；试点企业每家一套 `qms-<id>-edge`（独立数据库和 ERPNext），由 `pilot-runner.sh` / `tenant.sh` 开。
- 网络：质量 ERP 的 edge 容器只在外部网络 `qms-edge` 上；OnlyOffice 的 `docs` 容器只在学习平台的 `default` 网络上——**两边现在互相找不到**。Caddy 两个网络都在。
- OnlyOffice：`JWT_ENABLED=true`，密钥是学习平台 `.env` 的 `DOCS_JWT_SECRET`；`ALLOW_PRIVATE_IP_ADDRESS=true`；插件关闭。
- 本仓库没有任何 Frappe 应用；ERPNext 本身没有 OnlyOffice 接口。

## 三、建议做法（wenquest-ops 那边）

1. **一个小 Frappe 应用**（例如 `wq_onlyoffice`）：
   - 附件（File 文档）旁边加“在线编辑”按钮（只给 docx / xlsx / pptx，且当前用户对所属单据有写权限）。
   - 服务端方法：生成 OnlyOffice 编辑器配置（`document.url` = 本 ERP 的内部下载地址，带一次性签名；`key` = 文件哈希 + 修改时间；`callbackUrl` = 本 ERP 的回调方法），用 JWT 签名。
   - 回调：状态 2 / 6（已保存）时从 OnlyOffice 下载新文件，新建一个 File 版本挂回原单据（旧文件保留，记谁改的），校验回调的 JWT。
   - 页面：一个全屏编辑页，嵌 `https://learn.<域名>/docs/web-apps/apps/api/documents/api.js`。
2. **每家 ERP 一把自己的 JWT？** OnlyOffice 只认一个密钥（社区版）。建议共用学习平台的 `DOCS_JWT_SECRET`，由部署脚本写进每家 ERP 的站点配置（不进数据库导出）；回调里再核对文件属于本站点。
3. **网络**：让 OnlyOffice 能取文件、能回调——二选一：
   - 把 `docs` 容器也接到 `qms-edge` 网络（本仓库 `docker-compose.prod.yml` 一行），ERP 用内部地址 `http://qms-<id>-edge` 互通；或
   - 都走 Caddy 的公网地址（`qms-erp.<域名>`），简单但绕一圈。
   建议前者。
4. **安装**：演示站和每家试点企业都装这个应用（`tenant.sh` 新开企业时装；已有的补装一次）；国内镜像放 `qms/` 前缀，遵守《国内服务器加模块（质量ERP等）》的内存与锁规矩。
5. **验收**：演示 ERP 里给一个零件挂 docx，点“在线编辑”，两个账号同时改，保存后附件出现新版本、旧版本可下载；国内、美国各测一次；无权限的账号看不到按钮。

## 四、本仓库要配合的改动（做 C2 时一起提）

- `docker-compose.prod.yml`：`docs` 服务加 `qms-edge` 网络（如选内部互通）。
- `deploy/update.sh`：把 `DOCS_JWT_SECRET` 交给质量 ERP 的部署（文件或环境变量，两边约定）。
- `deploy/check-docs.sh`：加一项“从 qms-edge 能连到 docs”。
- 帮助：`docs/帮助/在线编辑Word和Excel.md` 加“问渠ERP 附件”一节。
