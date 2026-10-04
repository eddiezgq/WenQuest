# GPU 平台接入说明（管理员）

云端 GPU 实验（《实施细则 · 第 14 轮附》）需要在 GPU 平台开账号、生成密钥，再把密钥交给问渠。**密钥只填在 GitHub 的加密变量里，不要发在聊天、邮件或代码中。**问渠每次部署时把它们写进服务器的 `.env`。

平台的选择（Eddie 2026-10-03 定）：国内部署用 **AutoDL**；美国部署用 **Lambda**；第 7 章前再接阿里云。

## 一、AutoDL（国内）

1. 打开 https://www.autodl.com 注册。在“账号 → 实名认证”完成个人或企业认证（用接口开机必须认证）。
2. “费用 → 充值”：先充 50—100 元试用。
3. “控制台 → 设置 → 开发者 Token”：生成一个 Token，复制下来（只显示一次）。
4. 机器规格：
   - 按 AutoDL《容器实例 Pro API》文档中的“GPU 规格与基础镜像”表，挑选 RTX 4090 一档的 GPU 规格 ID 和镜像 ID（选带 CUDA 12 与 PyTorch 的镜像）；
   - 写成 `basic=GPU规格ID:镜像ID`。
   - 例：`basic=v-48g:base-image-mbr2n4urrc`（以文档当时列出的为准）。
5. 在 GitHub 填加密变量（下面第三节），`WQ_GPU_PROVIDER` 填 `autodl`。

## 二、Lambda（美国）

1. 打开 https://lambda.ai 注册，绑定付款方式。
2. “Cloud → API keys”：生成一个 API key。
3. “Cloud → SSH keys”：
   - 添加一把 SSH 公钥，记下它的名字。没有的话，在自己电脑的终端运行 `ssh-keygen -t ed25519 -f wq_gpu`，会生成 `wq_gpu`（私钥）和 `wq_gpu.pub`（公钥）两个文件；
   - 把 `wq_gpu.pub` 的内容粘贴到 Lambda。
4. 在 GitHub 填加密变量。在美国部署时，`WQ_GPU_PROVIDER` 填 `lambda`。

## 三、在 GitHub 填加密变量

1. 打开仓库 → Settings → Secrets and variables → Actions → New repository secret，逐个添加：

| 名称 | 填什么 | 用途 |
|---|---|---|
| `WQ_GPU_PROVIDER` | `autodl` 或 `lambda` | 打开学生 GPU 实验 |
| `WQ_GPU_AUTODL_TOKEN` | AutoDL 开发者 Token | 学生实验（国内） |
| `WQ_GPU_AUTODL_SPECS` | 如 `basic=v-48g:base-image-mbr2n4urrc` | 学生实验（国内） |
| `WQ_GPU_LAMBDA_KEY` | Lambda API key | 学生实验（美国） |
| `WQ_GPU_LAMBDA_SSH_KEY` | Lambda 上登记的 SSH 公钥名字 | 学生实验（美国） |
| `LAMBDA_KEY` | 同 `WQ_GPU_LAMBDA_KEY` | 书中数字的实测 |
| `LAMBDA_SSH_KEY_NAME` | 同上，SSH 公钥名字 | 书中数字的实测 |
| `LAMBDA_SSH_PRIVATE_KEY` | `wq_gpu` 私钥文件的全部内容 | 书中数字的实测 |

2. 填好后，在 Actions → “Build and deploy” → Run workflow 重新部署一次，或等下一次推送。部署日志里出现“GPU 实验设置已写入服务器”即成功。

## 四、书中数字的实测

Actions → “GPU measurements” → Run workflow，填书（`ai`）和章号。它会在 Lambda 上开一台机器，运行这一章 `code/runs/` 下的程序，把实测记录提交回仓库，最后关机。一次通常十几分钟、几美元。

## 五、检查与费用

- 用量与费用：老师在课程“实验”页看本课程学生的用量。全站的台账接口 `/api/v1/gpulab/admin/ledger` 只对站点管理员开放。
- 每台机器最长 3 小时、空闲 30 分钟自动关机。即使问渠出故障，也请每周到平台控制台看一眼有没有遗留的机器。
