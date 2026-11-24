# 智训引擎官方 SDK 1.0.2 修复源码

本仓库发布 2026-11-17 赛事提交镜像对应的冻结源码。

下载并解压完整的冻结源码包，其中包含 416 份文件。[source-snapshot.zip](source-snapshot.zip)

根目录的`harness.py`、`contest_submission.py`、`Dockerfile.platform`和`contest-contract.json`仅作预览；不要仅下载薄入口运行。`SOURCE_MANIFEST.json`包含原始源码提交及逐文件摘要。

- 原始运行提交：`3186ccd214d271f69228b4c6d5b9e494859188b2`；公开仓库的提交号会不同。
- ITE源码SHA-256：`2f051f284963f43328676980c2b0b26fdfc77c1e09ff4a36dd89c8e2d7e282d3`。
- 源码ZIP：14,926,408字节；SHA-256 `8d8d14fc8ea6f6551f0aa15c6ad4dcd7d75c7cee70522f1e13577e1104c74429`。
- 新镜像：`ite-contest-sdk:20261117-v1`，Docker ID `sha256:94471e228922848a99c5c67d8fa99ff97aef30bdab1594a249e7b488615e4eb8`。
- Docker-save tar：318,577,664字节；SHA-256 `db002f912bf3a953635466ab2d38cf46e2d191377ebaff6552a30951c9a8e00e`。

## 正式入口

```text
python3 /app/harness.py describe
python3 /app/harness.py train
python3 /app/harness.py predict
```

采用未修改的官方SDK1.0.2 template，协议`contest.harness.workspace.v2`，模型访问`host_gateway_rpc`。train每次处理一个平台启动帧。平台挂载的`/previous`指定本轮真实父检查点及代码，校验声明摘要后续训；不能从镜像内搜索另一个初始模型替代。`/state`与`/model`遵循SDK状态/预测合同；输出只写`/workspace`和`/tmp`。

每轮通过平台`rnd.model()`和当前绑定模型调用两次工具决策：先读真实历史选择冻结实验或保留，再读CPU结果和平台候选摘要选择候选或父模型。正式入口不使用旧PyTRiO私有端点、本地Key、固定tokenizer或价格预检。模型运输失败报轮次失败；无效动作或保护指标不足保留父模型，不造回执或历史。

A保留step7/48条原始分层回放/full5epoch；B保留父模型且如实记录0训练；C保留head-only2epoch及原触发。CPU worker固定NumPy1.26.4，保留官方架构、权重、Adam、标准化和真实父链。梯度train-only；独立future gate、5秒候选/20秒流/最多4次预算不变。产物`checkpoint.npz`及整个模型目录不超过64MiB。SDK独立预测逐行立即响应。

## 证据及边界

宿主751/751、Linux750通过1宿主专用skip；SDK原版宿主和Linux各15/15。A/B/C各10轮真实进程接线、9条官方预测一致性通过；最终冻结镜像又做三包各1轮及9条预测核对，save/load身份一致。验证结果和当时的上传状态见 2026-11-17 的报告。[SDK 修复报告](SDK_FIX_RESULTS.md)

模型回复与回执来自离线替身，累计33轮66个模拟回执，真实provider调用0。平台唯一一次镜像上传返回HTTP502，未保存新版本，尚未证实真实Sampler工具行为、平台协议通过或隐藏分数。已有公开开发NR-046效果判定仍为false，不能用接线夹具上的A/C改善替代完整验收。现有4B动作SFT历史全选NO的阴性结论也保持。

## 重建与来源

快照内`scripts/Dockerfile.platform`继承固定策略镜像`ite-ac-policy:20261115-v1`，父ID `sha256:03a82fb40332b2e4ae96d3e1c2ee9b4a69ff41e2ee7e05fd2e8aaee91d06cfad`。构建需准备该本地固定父镜像；只离线安装快照内的SDK，不升级依赖。完整基础Dockerfile和锁文件也在快照中。官方SDK和baseline保留其原始来源与权利，不因本快照而重新许可。

不包含API Key、私有数据或隐藏标签。平台凭据仅通过平台字段填写。
