# 招标信息抓取（tender-crawler）

> 本仓库中的部署方式：国内服务器上以 deploy 用户运行（`server-install.sh` + `cron.sh`，不用 sudo），由 `.github/workflows/tender-crawler.yml` 安装和取回结果，说明见 `docs/帮助/招标抓取.md`。下面的 systemd 安装方式供有 root 的机器使用。

每天自动从公开的政府采购 / 公共资源交易网站抓取招标公告，按关键词筛选，用规则提取预算、截止时间、采购人和地区，
生成一份 JSON 和一份 Markdown 摘要，供每日判断"哪些能投"使用。

- 只访问公开页面；不登录、不绕过验证码、不报名、不发邮件、不联系任何人。
- 每个网站两次请求之间至少间隔 4 秒（另加随机 0~2 秒），并遵守 robots.txt。
- 某个网站返回 403 / 412 / 429 或出现验证码页面，当天立即停止访问这个网站，不重试；其他网站照常。
- 信息提取只用规则，不调用任何大模型（配置里有开关，默认关闭；以后若开启，只能用国内已备案的模型服务）。
- 所有数据保存在本机 `/opt/tender-crawler/data`。OSS 上传、邮件推送都是开关，默认关闭。

## 一、安装（国内阿里云 ECS，Ubuntu 20.04 / 22.04 / 24.04）

```bash
# 1. 把程序包传到服务器后解压
tar xzf tender-crawler-1.0.1.tar.gz && cd tender-crawler

# 2. 一条命令安装（需要 root）
sudo bash install.sh
```

安装脚本会：安装 Python 依赖（走阿里云 PyPI 镜像）→ 建立专用的 `tender` 系统用户 → 程序装到 `/opt/tender-crawler`
→ 注册 systemd 定时任务，**每天北京时间 06:30 左右自动运行**（服务器关机错过的，开机后会补跑）。

装完立刻试跑一次，看日志：

```bash
sudo systemctl start tender-crawler.service
journalctl -u tender-crawler -n 50 --no-pager
cat /opt/tender-crawler/data/latest.md
```

重复运行 `install.sh` 就是升级：程序更新，已有的 `config.yaml` 和历史数据保留。

## 二、日常查看

| 文件 | 内容 |
| --- | --- |
| `/opt/tender-crawler/data/latest.json` | 最新一次结果（给每日判断任务读取） |
| `/opt/tender-crawler/data/latest.md` | 最新一次的可读摘要 |
| `/opt/tender-crawler/data/YYYY-MM-DD.json / .md` | 按天存档，默认保留 90 天 |
| `/opt/tender-crawler/data/seen.sqlite3` | 去重库（记录每条公告第一次发现的日期） |

常用命令：

```bash
tender-crawler check                    # 检查配置文件
tender-crawler test-source 中国政府采购网  # 只试抓一个来源
systemctl list-timers tender-crawler.timer
```

## 三、改配置（`/opt/tender-crawler/config.yaml`）

- **关键词**：`keywords` 下分工程 / 教育 / 管理三组，加减词即可。标题或采购人里命中才收录。
- **排除词**：`exclude`，标题命中直接丢弃（物业、施工、保洁等）。
- **重点地区和高校**：`focus`，命中的排在前面并打上标记。
- **来源**：`sources`。
  - `ccgp_list`：中国政府采购网公告列表页（地方 / 中央的公开招标、磋商、谈判、询价、单一来源栏目），按日期往回翻，本地按关键词过滤。
  - `ggzy_deal`：全国公共资源交易平台（2026 年新版接口 www.ggzy.gov.cn；接口要求验证码时当天停止）。
  - `ccgp_search`：中国政府采购网全文检索。从国内云服务器访问会被拦截（“频繁访问”），默认关闭。
  - `html_list`：**通用列表页抓取器**。任何高校采购网、地方采购网的"公告列表页"，填网址和 CSS 选择器就能加，不用改代码。填好后用 `tender-crawler test-source 名称` 验证，再把 `enabled` 改成 `true`。
  - 上海政府采购网已预置为 `html_list`，但默认关闭：它的页面结构需要在服务器上打开确认后再启用。
- 改完不用重启，下次运行自动生效。

## 四、推送开关（以后再填）

- **OSS**：`publish.oss.enabled: true`，填 bucket；密钥写在 `/etc/tender-crawler.env`（权限 600）：
  ```
  OSS_ACCESS_KEY_ID=...
  OSS_ACCESS_KEY_SECRET=...
  ```
  然后 `sudo /opt/tender-crawler/venv/bin/pip install -i https://mirrors.aliyun.com/pypi/simple/ oss2`。
  每天会上传 `latest.json / latest.md` 和当天存档。
- **邮件**：`publish.email.enabled: true`，填 SMTP 和收件人，账号密码同样放在 `/etc/tender-crawler.env`。

## 五、结果格式（`latest.json`，schema `tender-feed/1`）

```jsonc
{
  "schema": "tender-feed/1",
  "date": "2026-11-08",                     // 北京时间运行日期
  "window": {"from": "2026-11-06", "to": "2026-11-08"},
  "sources": [                               // 每个来源当天的状态
    {"name": "中国政府采购网", "status": "ok|partial|blocked|error|disabled", "items": 42, "requests": 120, "message": ""}
  ],
  "summary": {"total": 18, "new": 7, "open_calls_new": 5, "by_group": {"education": 12, "engineering": 6}},
  "items": [{
    "id": "3f2a…",                            // 去重键
    "title": "…虚拟仿真实验教学平台建设项目公开招标公告",
    "url": "http://www.ccgp.gov.cn/…",
    "sources": ["中国政府采购网"],
    "publish_date": "2026-11-07",
    "first_seen": "2026-11-08", "is_new": true,
    "notice_type": "tender|intention|inquiry|negotiation|single_source|correction|result|other",
    "is_result": false,                      // 中标、成交等结果公告，只供参考
    "region": "上海", "buyer": "上海理工大学",
    "budget_cny": 3865000.0,                 // 元；识别不到为 null
    "deadline": "2026-11-28 09:30",          // 投标 / 响应截止；识别不到为 null
    "groups": ["education"], "keywords": ["虚拟仿真实验", "教学评价"],
    "focus": ["上海", "上海理工大学"],
    "detail_fetched": true,                  // 是否打开过详情页
    "detail_excluded_by": []                 // 详情页里出现的排除词（只提示，不丢弃）
  }]
}
```

排序规则：招标 / 采购类在前，结果公告在后；重点地区 / 高校在前；新增在前；同类按发布日期从新到旧。

## 六、注意

- 网站改版后，解析可能失效。表现是某个来源 `status` 为 `ok` 但 `items` 长期为 0，或者变成 `error`。
  这时改 `tender_crawler/sources.py` 中对应的解析函数，或者在配置里改用 `html_list`。
- 预算、截止时间都是规则识别，可能识别不到或识别错。投标前以公告原文为准。
- 卸载：`sudo bash uninstall.sh`（保留历史数据）。
