# 问渠数字工厂 · 本地版（给学校机房管理员）

学校机房没有外网、上不了线上的问渠数字工厂时，用本地版：在机房的**一台电脑**（下面叫“教师机”）上用 Docker
启动整座数字工厂，学生的电脑用浏览器连教师机就能上《数字工厂实训》。

本地版缺省是**教学模式、演示工厂“问渠减速器厂”、模拟 ERPNext**：仿真车间一直在生产，看板有数据；
实验 7、15–23，两周情景，情景导演都能用。数据只存在教师机的 Docker 里，不往外发。

## 一、要什么电脑

| | 教师机（运行工厂） | 学生机 |
| --- | --- | --- |
| 系统 | Windows 10 / 11（64 位）、macOS 12 以上、或 Linux（如 Ubuntu 22.04 以上） | 任意，有新版 Chrome 或 Edge 就行 |
| 处理器 | 4 核以上，支持虚拟化（Windows 要在 BIOS 里打开 VT-x / AMD-V） | — |
| 内存 | 至少 8 GB；一个班同时用，建议 16 GB | 4 GB 以上 |
| 硬盘 | 至少 40 GB 空余（镜像里有有限元、流体计算软件，比较大） | — |
| 网络 | 和学生机在同一个局域网；第一次安装要能上外网（或用 U 盘导入，见第七节） | 能访问教师机 |

学生机不用装任何软件。教师机最好设成**固定 IP**（在路由器里给它分配固定地址），不然每次开机地址可能变。

## 二、在教师机上装 Docker

- **Windows / macOS**：下载安装 Docker Desktop（<https://www.docker.com/products/docker-desktop/>）。
  Windows 安装时选用 WSL 2；装完重启，打开 Docker Desktop，等左下角显示 “Engine running”。
  在 Docker Desktop 的 Settings → Resources 里把内存调到 6 GB 以上。
- **Linux**：装 Docker Engine 和 compose 插件（Ubuntu：按 Docker 官网“Install Docker Engine on Ubuntu”做，装 `docker-ce` 和 `docker-compose-plugin`）。

装好后在终端（Windows 用 PowerShell）里运行 `docker info`，不报错就可以了。

## 三、取得问渠的代码

两种办法任选一种，放在一个好找的文件夹里（例如 `D:\wenquest` 或 `~/wenquest`）：

- 有 git：`git clone <问渠给你的仓库地址> wenquest`
- 没有 git：向问渠要代码压缩包（ZIP），解压出来。

下面的命令都在这个文件夹（仓库根目录）里运行。

## 四、启动

Windows（PowerShell）：

```powershell
cd D:\wenquest
.\factory\local\start.ps1
```

PowerShell 提示“禁止运行脚本”时，先运行一次 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`（选 Y）。

macOS / Linux（终端）：

```bash
cd ~/wenquest
factory/local/start.sh
```

**第一次启动**要下载、构建镜像，约 10–30 分钟（看网速）；以后每次几十秒。脚本会：

1. 生成配置文件 `factory/digital/.env`（登录签名密钥随机生成）；
2. 生成**老师密码**并显示一次，例如 `老师密码：k7Qm2xPa9T`——请记下来；忘了就打开 `factory/digital/.env` 找 `WQ_TEACHER_PASSWORD=` 那一行；
3. 启动整座工厂，最多等 4 分钟，看到“已启动（本地版）”就好了，并显示学生该打开的地址。

教师机自己打开 <http://localhost:8100>，登录页标题旁边显示“本地版”。

## 五、学生怎么连

1. 查教师机的 IP：Windows 运行 `ipconfig`，看“IPv4 地址”；macOS 运行 `ipconfig getifaddr en0`；Linux 运行 `hostname -I`。
   启动脚本最后也会显示，例如 `机房里学生的电脑打开：http://192.168.1.20:8100`。
2. 学生在浏览器打开 `http://<教师机 IP>:8100`，例如 <http://192.168.1.20:8100>。
3. 打不开时多半是防火墙：教师机要允许 **8100**（工作台）、**9001**（实时数据）、**8091**（模拟 ERPNext）三个端口进来。
   Windows 第一次启动时如果弹出防火墙提示，选“允许”；或者用管理员身份的 PowerShell 运行：

   ```powershell
   New-NetFirewallRule -DisplayName "WenQuest Digital Factory" -Direction Inbound -Protocol TCP -LocalPort 8100,9001,8091 -Action Allow
   ```

**登录**：

- **学生**：填自己的名字（名字就是成绩账号，每次用同一个名字），选一个岗位（计划员、工艺员、操作工、质检员、售后、安全员、维修工、班组长），
  进入教学模式。学生不能当厂长、不能用生产模式和教师控制台。
- **老师**：填名字，勾“我是老师”，输老师密码。老师可以当厂长、用生产模式、教师控制台、情景导演，看全班得分。

老师密码只给任课老师。要换密码：改 `factory/digital/.env` 里的 `WQ_TEACHER_PASSWORD=`，再运行一次启动脚本。

## 六、停止、清空、换一座工厂

| 要做的 | Windows | macOS / Linux |
| --- | --- | --- |
| 停止（数据保留，下次接着用） | `.\factory\local\stop.ps1` | `factory/local/stop.sh` |
| 清空重来（成绩、订单、车间历史全部删掉） | `.\factory\local\stop.ps1 -Reset` | `factory/local/stop.sh --reset` |
| 再启动 | `.\factory\local\start.ps1` | `factory/local/start.sh` |
| 按一份工厂清单建车间 | `.\factory\local\start.ps1 -Plant 清单.yaml` | `factory/local/start.sh --plant 清单.yaml` |

教师机关机、重启后，打开 Docker Desktop，工厂会自己起来；起不来就再运行一次启动脚本。

不加 `--plant` 就是演示工厂。用别的清单（例如 `factory/plants/example-sewing.yaml` 示例缝纫机厂）时，
车间、看板、订单照常，但实验、情景、七个领域的教学页面只在演示工厂有。下次不加 `--plant` 启动就回到演示工厂。

## 七、没有外网的机房

第一次构建要从网上下载。机房完全没有外网时，在一台能上网、装了 Docker 的电脑上先准备好，再用 U 盘拷过去：

1. 在能上网的电脑上，照第三、四节取代码、启动一次（会构建好镜像），然后导出镜像：

   ```bash
   docker save -o wq-factory-images.tar wq-digital-factory:1.0 wq-digital-factory-bridge:1.0 \
     wq-digital-factory-openplc:1.0 eclipse-mosquitto:2.0.20 postgres:16-alpine
   ```

2. 把 `wq-factory-images.tar` 和整个代码文件夹拷到教师机（不要拷 `factory/digital/.env`，教师机会自己生成）。
3. 在教师机上导入并用 `--offline` 启动（不构建、不下载）：

   ```bash
   docker load -i wq-factory-images.tar
   factory/local/start.sh --offline          # Windows：.\factory\local\start.ps1 -Offline
   ```

## 八、AI 工厂助手（可选）

不联网时 AI 工厂助手用规则回答，简报、提醒照常。机房能上外网、想用大模型时，在 `factory/digital/.env` 里填
`WQ_DEEPSEEK_KEY=`（国内用已备案的 DeepSeek）或 `WQ_CLAUDE_KEY=`，再运行一次启动脚本。

## 九、更新到新版本

1. 先停止（数据保留）：`factory/local/stop.sh`。
2. 换新代码：有 git 就在仓库根目录运行 `git pull`；用压缩包的，把新压缩包解压**覆盖**到原文件夹，
   **保留原来的 `factory/digital/.env`**（老师密码、密钥都在里面）。
3. 再运行启动脚本：会重新构建，几分钟到十几分钟。没有外网的机房，按第七节在能上网的电脑上准备新镜像，
   导入后用 `--offline` 启动。

数据（成绩、订单、车间历史）在 Docker 卷里，更新不会丢；只有 `--reset` 才会清空。

## 十、地址一览

| 地址 | 内容 |
| --- | --- |
| `http://<教师机 IP>:8100` | 工作台（学生、老师都从这里进） |
| `http://<教师机 IP>:8091` | 模拟 ERPNext（演示用的 ERP，工作台里的 ERPNext 链接指向它） |
| `http://localhost:1880` | Node-RED 数据流（只在教师机上看） |
| `<教师机 IP>:1883`、`:9001` | 数据总线（MQTT；9001 给浏览器用） |

## 十一、出了问题

| 现象 | 处理 |
| --- | --- |
| “没有找到 docker”“Docker 没有在运行” | 装好并打开 Docker Desktop，等显示 Engine running 再运行脚本 |
| “枢纽 4 分钟内没有就绪” | 在 `factory/digital` 里运行 `docker compose logs hub` 看原因；内存不够时把 Docker 的内存调大 |
| 学生打不开 | 查教师机 IP 是否变了；防火墙放行 8100、9001、8091；学生机和教师机在同一个网段 |
| 学生能打开但看板不动 | 防火墙没放行 9001（实时数据走这个端口） |
| 老师密码不对 | 看 `factory/digital/.env` 的 `WQ_TEACHER_PASSWORD`；连续输错 5 次要等 10 分钟 |

服务器部署（域名、HTTPS、备份）用的是 `factory/deploy/`，本地版用不到。
