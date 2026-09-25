# 问渠 WenQuest v0.1 部署包

问渠 WenQuest 的教学引擎部署包：开源教学引擎 Moodle 5.2 + Claude / DeepSeek 模型接入。一条命令启动，AI 功能开箱可用。问渠前端与 AI 服务层将在后续版本加入本包。

## 包里有什么

| 内容 | 说明 |
| --- | --- |
| `plugins/aiprovider_claude/` | 自研 Moodle 插件：把 Anthropic Claude 接入 Moodle AI 子系统 |
| `moodle/Dockerfile` | Moodle 5.2 镜像（PHP 8.3 + Apache），已内置 Claude 插件和中文语言包 |
| `docker-compose.yml` | Moodle、PostgreSQL 16、Redis、定时任务四个服务 |
| `moodle/setup_ai.php` | 启动时按 `.env` 自动配置 AI 模型、启用 AI 功能、设置中文和时区 |
| `.env.example` | 配置模板 |
| `docker-compose.prod.yml`、`deploy/` | 云服务器生产部署：Caddy 自动 HTTPS、更新、回滚、备份与恢复脚本 |
| `.github/workflows/deploy.yml` | 推送即自动构建镜像并部署到服务器 |
| `site/` | 学院官网（静态页面，中英双语） |
| `docs/上线手册.md` | 从零上线到 DigitalOcean 的分步手册 |

启用后，Moodle 里立即可用的 AI 功能：

- **课程助手**：学生和教师在课程页面一键“总结本页”“解释这段内容”。
- **编辑器 AI**：在任何富文本编辑器里让 AI 起草文字（教案、作业说明、公告等）。

## 上线到云服务器

按 [docs/上线手册.md](docs/上线手册.md) 操作：官网在主域名，学习平台在 `learn.` 子域名，推送代码即自动部署，每天自动备份。

## 本地快速试用

需要一台 Linux 服务器（建议 4 核 8 GB 内存以上）并安装 Docker 24+。

```bash
cp .env.example .env
nano .env                      # 至少填：MOODLE_WWWROOT、两个密码、一个 AI 密钥
docker compose up -d --build   # 首次构建约 10–20 分钟
docker compose logs -f moodle  # 看到 "Created AI provider" 即完成
```

浏览器打开 `MOODLE_WWWROOT`，用 `.env` 里的管理员账号登录。

## 模型选择

| 场景 | 设置 |
| --- | --- |
| 在美国开发、演示 | 填 `ANTHROPIC_API_KEY`（在 console.anthropic.com 申请；claude.ai 订阅不含 API） |
| 中国大陆部署 | 填 `DEEPSEEK_API_KEY`。DeepSeek 已完成生成式 AI 服务备案，Moodle 5.2 已内置其插件 |
| 两个都填 | 两个模型都启用，在“网站管理 → AI → AI 提供方”里调整优先顺序 |

可选 Claude 模型：`claude-sonnet-5`（默认，质量与速度均衡）、`claude-opus-5-5`（最强，适合复杂批改）、`claude-haiku-4-5-20251001`（最快、成本最低）。
改 `.env` 后执行 `docker compose up -d`，重启时自动更新配置。

## 在中国大陆部署的注意事项

- **合规**：Anthropic 不对中国大陆提供服务；面向国内学校提供生成式 AI 服务须使用已备案模型，并在属地网信办登记。国内部署请只填 `DEEPSEEK_API_KEY`。
- **网络**：Docker Hub 和 GitHub 在国内可能很慢或无法访问。
  - 给 Docker 配置国内镜像加速器（阿里云、腾讯云控制台均提供）。
  - 构建时换成可访问的 Moodle 仓库镜像：
    `docker compose build --build-arg MOODLE_GIT=<镜像地址>`
- **HTTPS**：`docker-compose.prod.yml` 里的 Caddy 会自动申请证书；也可以改用 Nginx 或云负载均衡，并设 `MOODLE_SSLPROXY=true`。

## 只安装插件（已有 Moodle 5.1 及以上）

用 `aiprovider_claude.zip`（GitHub Actions 每次构建都会生成，在该次运行的 Artifacts 里下载）：网站管理 → 插件 → 安装插件 → 上传 zip。
然后在“网站管理 → AI → AI 提供方”新建 Claude 实例并填入 API 密钥，再到“AI 调用位置”启用课程助手和编辑器。

## 日常运维

生产服务器上用 `deploy/` 里的脚本（见上线手册“日常维护”）。本地试用时：

```bash
docker compose ps                                   # 查看状态
docker compose exec db pg_dump -U moodle moodle > backup.sql   # 备份数据库
docker compose up -d --build                        # 更新插件或 Moodle 后重新构建，自动升级数据库
```

`moodledata`（上传的文件）和 `dbdata`（数据库）存放在 Docker 卷中，重建容器不会丢失，但请定期备份。

## 测试情况（v0.1）

- 插件单元测试 23 项全部通过（Moodle 5.2.3，PHP 8.4，PostgreSQL 16）。
- 端到端：通过 Moodle AI 管理器调用生成、摘要、解释三种动作均成功；对真实 Anthropic API 的请求格式和认证已验证（用无效密钥得到预期的 401）。
- 安装流程（生成配置 → 安装数据库 → 配置 AI → 升级）已在全新数据库上验证。
- Docker 镜像本身尚未在服务器上实际构建过，首次构建如有报错请把日志发回。

## 许可

插件与部署脚本以 GNU GPL v3 或更高版本发布，与 Moodle 一致。
