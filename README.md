# 智训引擎赛事提交源码

2026-11-24 合并版使用官方 SDK 1.0.2 和 `contest.harness.workspace.v2` 协议。A 按 Step 7 从官方父 MLP 续训，以 Macro-F1 选择候选。B 保留父模型。C 为官方 MLP 增加稳定域输出头和低 RUL 残差模块，以 RMSE 选择候选。A 和 C 的候选均须通过独立未来标签门控。

下载后解压源码快照，从解压目录使用 `scripts/Dockerfile.platform` 构建。该定义依赖固定的本地父镜像 `ite-ac-policy:20261115-v1`。源码快照沿用上一版已公开源码，更新了赛事运行入口所需的模块和提交协议测试。[源码快照](source-snapshot.zip)

- 镜像对应的本地源码提交为 `dd9011a45ddcc1b89ddc5d11375c52b7e9aac4c0`。
- 原交付镜像标签为 `ite-contest-sdk:20261124-merged-v1`，镜像 ID 为 `sha256:8f0da5f8aebd2297e2e2b09574566c9e88858751721d223228b15754e731baf4`。
- 原交付镜像在断网 Linux 上通过 940 项测试，1 项因缺少主机专用运行时而跳过。Docker tar 重载后镜像 ID 一致。
- 公开源码快照已在断网 Linux 容器中通过 18 项 SDK 提交协议测试。
- 源码清单记录了公开快照和原镜像各自的摘要。重建公开快照时用清单顶层的 `ite_sha256` 作为 `ITE_SOURCE_SHA256`。[源码清单](SOURCE_MANIFEST.json)

仓库根目录的 `harness.py`、`contest_submission.py`、`Dockerfile.platform` 和 `contest-contract.json` 提供入口预览。平台运行命令为 `python3 /app/harness.py describe`、`train` 或 `predict`。历史 SDK 接入记录见 [SDK 修复报告](SDK_FIX_RESULTS.md)。
