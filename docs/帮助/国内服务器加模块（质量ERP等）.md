# 国内服务器上加一个模块（以问渠质量 ERP 为例）

写给：在别的仓库、别的会话里开发的模块（问渠质量 ERP 等），要部署到问渠的国内服务器上。
依据：第 53 轮（服务器自带镜像仓库）。2026-10-29 起草。

## 一、国内服务器的现状

| 项目 | 情况 |
|---|---|
| 服务器 | 阿里云 华东2（上海），Ubuntu 24.04，4 核 8 GB，100 GB 云盘，公网 IP `139.224.32.125` |
| 已装 | Docker（Ubuntu 软件源装的，Compose 2.40）、`bootstrap.sh` 初始化完成：`deploy` 用户（在 docker 组）、只允许密钥登录、防火墙只开 22 / 80 / 443 |
| 备案 | ICP 备案审核中。**备案号下来之前网站不对外开放**，域名先不解析到这台服务器 |
| 网络 | **服务器连不上 GitHub，也拉不动 Docker Hub**。凡是要放到服务器上的东西，都由 GitHub Actions 通过 SSH 推过去，不让服务器自己下载 |
| 镜像仓库 | 服务器自带一个仓库 `wq-registry`，只监听 `127.0.0.1:5000`，不对外开端口（第 53 轮，问渠主仓库的部署第一次运行时建好） |
| 问渠平台 | 装在 `/opt/wenquest`；它的 Caddy 占用 80 / 443，管所有网址和证书 |
| AI | 国内只能用已备案模型（DeepSeek 等），不能调 Claude |

## 二、模块要遵守的约定

1. **镜像**：模块自己的 GitHub Actions 照常构建，推到 ghcr.io；再通过 SSH 通道复制进服务器的仓库，**名字一律加前缀** `qms/`（例：`127.0.0.1:5000/qms/app:<版本>`），不和问渠自己的 `engine`、`gateway` 等重名。
2. **复制方法**（与问渠主仓库的 `mirror-cn` 相同，可以直接抄 `.github/workflows/deploy.yml` 里那几步）：
   ```bash
   # 在 GitHub Actions 里，已写好 ~/.ssh/id_ed25519 和 known_hosts
   ssh -fN -o ExitOnForwardFailure=yes -L 5000:127.0.0.1:5000 deploy@$HOST
   skopeo copy --retry-times 3 --dest-tls-verify=false --src-creds "$GITHUB_ACTOR:$GITHUB_TOKEN" \
     docker://ghcr.io/<owner>/<repo>/app:$TAG docker://localhost:5000/qms/app:$TAG
   ```
   Docker Hub 上的基础镜像（如 postgres）也这样复制进来，例如 `docker://docker.io/library/postgres:16-alpine` → `localhost:5000/qms/postgres:16-alpine`。只传缺少的层，第一次慢，以后快。
   - 问渠主仓库的部署会定期清理**它自己的**镜像，并回收仓库空间。回收时正好在传的那一层可能被删掉，复制命令会报错，重试一次就好（上面的 `--retry-times` 加外层重试）。模块不要自己运行 `garbage-collect`。
   - 模块自己的旧版本请自己清理（只留最近 3 个），方法同 `deploy.yml` 里的 “Keep the last 3 versions” 那一步。
3. **目录**：装在 `/opt/qms`（`deploy` 用户有写权限的话直接建；没有就请 Eddie 用 root 运行 `install -d -o deploy -g deploy /opt/qms`）。服务器上的 `docker compose` 从 `127.0.0.1:5000/qms/...` 拉镜像，不用登录（Docker 默认允许本机仓库走 http）。
4. **网址**：模块**不要**占 80 / 443。在 compose 里把对外的那个容器接到外部网络 `qms-edge`（问渠平台已建好），容器名叫 `qms-demo-edge`，监听 80 端口（和美国服务器上的约定相同）。问渠这边在 `deploy/caddy-extra/cn/` 加一个 `qms.caddy`，把 `qms.<主域名>` 转给它，证书由问渠的 Caddy 自动办。**模块就绪后告诉问渠主仓库这边加这个文件。**
5. **SSH 密钥**：给模块的仓库单独一把钥匙，不和问渠主仓库共用。Eddie 在服务器上（root）运行：
   ```bash
   ssh-keygen -t ed25519 -N "" -C github-deploy-qms -f /root/qms_deploy
   cat /root/qms_deploy.pub >> /home/deploy/.ssh/authorized_keys
   cat /root/qms_deploy
   ```
   把显示的私钥（整段，连头尾两行）填进**模块仓库**的 Secrets（例如 `CN_DEPLOY_SSH_KEY`），`CN_DEPLOY_HOST` 填 `139.224.32.125`；然后 `rm /root/qms_deploy`。
6. **一次只部署一个**：服务器上启动、更新容器前先拿锁 `flock -w 1500 /tmp/wenquest-deploy.lock …`（问渠主仓库也用这把锁），免得两边同时重启把 8 GB 内存挤满。
7. **资源**：服务器只有 4 核 8 GB，问渠平台已经占去大半。模块的每个容器都设内存上限（`mem_limit`），合计建议不超过 **2.5 GB**；数据库尽量小配置。真不够时再说升级（8 核 16 GB）或给客户单独部署。
8. **数据和备份**：数据放 docker 卷或 `/opt/qms/data`，只存在国内服务器上，不传回美国。问渠的每日备份（03:30）不包括模块，模块自己做备份。
9. **AI**：国内版只接 DeepSeek（或别的已备案模型），钥匙由 Eddie 自己填进服务器上的 `.env`，不经过聊天。
10. **备案期间**：可以部署、在服务器内部测；不要让外人能打开。

## 三、建议的顺序

1. 模块那边：按上面写好它的国内部署步骤（复制镜像 → 传 compose 文件到 `/opt/qms` → `docker compose up -d`）。
2. Eddie：生成模块专用的 SSH 钥匙，填进模块仓库的 Secrets。
3. 问渠主仓库这边：加 `deploy/caddy-extra/cn/qms.caddy`（`qms.<主域名>` → `qms-demo-edge:80`）。
   - **已加（2026-10-30）**：质量 ERP 第一次部署成功后（wenquest-ops 的 ADR-0024，装在 `/opt/wenquest/qms`，因为 deploy 用户不能建 `/opt/qms`），`qms.caddy` 转两个名字：`qms.<主域名>`（WenQuest Ops）和 `qms-erp.<主域名>`（ERPNext），都给 `qms-demo-edge:80`。
4. 备案号下来、域名解析后，`https://qms.<主域名>` 就能访问。
