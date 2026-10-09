# 运维：状态、备份、恢复、重启

> 数字工厂装在服务器的 `/opt/wenquest/factory`；下面的命令都在这个目录里运行。

## 日常命令

| 命令 | 作用 |
| --- | --- |
| `deploy/status.sh` | 各容器状态、内存、历史库大小、工作台和 ERPNext 两个网址的响应 |
| `deploy/backup.sh` | 备份历史库、ERPNext（数据库加附件）和 `.env`；每天 03:30 随学习平台的备份自动执行 |
| `deploy/restore.sh backups/<时间>` | 从备份恢复历史库与 ERPNext；恢复前先自动再备份一次当前数据 |
| `deploy/update.sh` | 不带参数：用现有版本重启（改了 `.env`，例如换工厂清单、换 AI 密钥之后） |

新版本由推送自动部署（测试 → 构建镜像 → 服务器上运行 `deploy/update.sh 新镜像`），不用手动升级。

## 要注意的

- `.env` 里有全部密码，只在服务器上；自己另存一份；
- 换工厂清单前先在自己电脑上 `python -m factory.plant check 清单.yaml`；
- 恢复演练：在另一台机器上用 `deploy/restore.sh` 恢复一次，确认备份能用。

更详细的说明在帮助首页“资料”里的《数字工厂上线与维护》。

```ask
q: 怎么确认昨晚的备份做成了？
```
