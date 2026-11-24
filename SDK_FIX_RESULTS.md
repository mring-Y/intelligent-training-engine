# 官方 SDK 1.0.2 协议与模型网关修复记录

用户在本轮诊断后明确确认，仅修复协议和模型网关，不新增训练策略。对应 NR-047；[执行计划](superpowers/plans/2026-11-17-official-sdk-adapter.md)。

## 修复后的真实调用链

`python3 /app/harness.py train` 使用未修改的官方 SDK template，加载 `contest_submission.train`。每次 start 只执行一个平台 round：校验 `/previous` 声明的 checkpoint 和 code 文件摘要，读取真实 `rnd.history()`，通过平台的 `rnd.model()` 调用当前绑定模型。首调用用函数工具 `run_frozen_experiment` 决定保留或尝试冻结实验；若尝试，复用原 `run_round` 及官方 NumPy 1.26.4 CPU worker。候选通过原独立 future gate 后提交给平台测量，再通过第二次 `select_candidate` 工具调用阅读实际实验及平台摘要、选择候选或父模型。结束引用两个实际回执和读过的历史 ID，并等待 round_ack。

正式入口不导入 `ite.trio_client`、`ite.trio_worker`、`ite.code_harness_agent` 或 PyTRiO 私有客户端。没有本地 key、endpoint、tokenizer 和价格预检。旧研究模块仍作为历史代码保留，但不是平台入口的执行路径。模型运输失败直接报 round_failed；非法动作安全保留父模型，不伪造调用回执。

A 仍为 step7、48 行原始分层回放、full5epoch；B retain；C head-only2epoch、既有漂移/损失触发。官方架构、权重、Adam、标准化、学习率、种子与原5秒候选/20秒流/最多4次预算保留。梯度只来自公开 train；validation 只用于监测、筛选和未来门控。跨轮状态复制到 `/workspace/native-state` 后写入和保存，记录已消费验证 ID；即使最终保留旧父模型，也不会把被拒候选当成已部署父模型，或重置验证账本。

候选选择还必须满足既有完整保护指标：A Macro-F1 至少增加0.005、Accuracy最多下降0.005；C RMSE严格改善、MAE最多增加2%、高估率最多增加2个百分点、平均正向高估最多增加1周期。CPU配对检查只用本轮新消费的验证ID；平台候选摘要按原返回值保留，缺少所需指标时不晋级，不补造数字。平台缺少完整父摘要时只明确使用同一公开投影的CPU父参考，不把它标为平台测量。

独立预测使用 SDK `Sample`、`CONTEST_ARTIFACT_PATH` 和 `/model`，由常驻固定 CPU worker 提供，每行立即应答并刷新，不等待 EOF。task/profile/context 不一致直接失败。分类唯一最高分保持官方 argmax 的首类选择；回归保持原单位且非负。

## 验证结果

- 先写11项协议测试，旧实现全部失败，原始红灯在 `records/01-tdd-red.txt`。状态选择和缺失指标的新增边界也分别保留红灯/绿灯。最终新增15项测试包含真实 CPU 训练、模型 retain、摘要篡改、无回执失败、跨轮被拒候选、消费账本、工具调用及逐行预测。
- 宿主完整751/751通过，1139.909秒：`records/24-host-full-final.txt`。第一次完整751项中旧SFT环境导入超过原15秒，原日志与单项复核均保留；沙箱外同一单项原时限5.670秒通过。没有修改依赖或延长时限。
- Linux完整751项中750通过、1项宿主专用skip，428.685秒：`records/28-linux-full-tests.txt`。容器4CPU/4GiB、根目录只读、network none。
- SDK原版15/15离线测试在宿主UTF-8环境通过，24.863秒：`records/10-sdk-utf8-tests.txt`；首次Windows默认编码下1项失败保留。SDK23份源文件和入口template摘要未改。SDK archive SHA-256为 `c676c8beeef69cece9cbec5a633d05dbb9832eb22b6f761913f2315bd1f85133`。
- SDK原版Linux15/15离线测试通过，10.938秒：`records/32-linux-upstream-sdk-tests-v2.txt`。中途Docker engine暂时不可用的首次日志保留，恢复后原命令通过，没有修改SDK或依赖。
- A/B/C各10轮真实进程协议复核全部完成；30个训练容器和3组预测/官方对照，通过只读挂载、4CPU/4GiB、network none、退出0、无OOM审计；9个逐行预测与官方预测器精确一致，并验证EOF之前应答。495份证据摘要已核对：`records/31-ten-round-audit.json`。

模型由离线宿主替身提供函数回复和回执；CPU训练/预测真实执行。共60次模拟网关回执、真实provider调用0、远程费用0、平台试运行0。不能将模拟回执称为真实PyTRiO调用或隐藏评测成绩。平台真实模型/当前Sampler能否正确返回工具动作，仍需平台校验；若其退化或格式无效，本实现会保留父模型，不能承诺性能提升。

## 公开夹具上的接线结果

以下不是完整效果矩阵或新独立验收，只证明候选确实训练、优化器推进和预测改变。数据沿用此前已见公开夹具，无特征漂移或标签修改。

|包/轮|父主指标|候选主指标|父steps→候选steps|训练次数/本地门控更新|最终选择|
|---|---:|---:|---|---|---|
|A 1，622条|Macro-F1 0.7342700157|0.7621646383|80→90|1/1|候选|
|A 2，另622条|Macro-F1 0.1663486005|0.1663486005|90→90|1/0|保留父|
|B 1，512条|RMSE 949.3353401分钟|相同|825→825|0/0|保留父|
|B 2，另512条|RMSE 692.5228447分钟|相同|825→825|0/0|保留父|
|C 1，512条|RMSE 39.8544885周期|38.8051611|6630→6634|3/1|候选|
|C 2，另512条|RMSE 39.7240641周期|38.0877246|6634→6636|2/1|候选|

第3至10轮复用同两份公开投影，fresh validation为0，因此实际训练次数0，继续选择当前父模型；每轮仍有两次模拟SDK工具回执。没有伪造十轮都发生训练。A/B/C各十轮累计训练次数2/0/5、接受更新1/0/2。最大候选目录分别575854/1096986/8307830字节，低于64MiB。全流已有成果及 NR-046 `effect_passed=false` 判定保持，不将此夹具成绩替代它。

## 镜像与平台交付状态

验证源 ITE SHA-256：`2f051f284963f43328676980c2b0b26fdfc77c1e09ff4a36dd89c8e2d7e282d3`；开发验证镜像为 `ite-contest-sdk:20261117-tools`，来源如实标dirty。固定父镜像为 `ite-ac-policy:20261115-v1`、ID `sha256:03a82fb40332b2e4ae96d3e1c2ee9b4a69ff41e2ee7e05fd2e8aaee91d06cfad`；未升级其依赖。

正式实现已冻结在 `3186ccd214d271f69228b4c6d5b9e494859188b2`。最终镜像 `ite-contest-sdk:20261117-v1` 的实际 image ID 为 `sha256:94471e228922848a99c5c67d8fa99ff97aef30bdab1594a249e7b488615e4eb8`，标记dirty=false；官方 `describe` 返回 workspace.v2 / host_gateway_rpc / SDK1.0.2，正式模块导入后未加载旧私有模型客户端。最终镜像再完成A/B/C各一轮真实CPU与逐行预测接线，`final-image-smoke-v1/summary.json`通过；属于同一已见夹具复核，不是新增独立效果数据。

真实 `docker save -o outputs/contest-sdk-adapter-20261117/harness.tar ite-contest-sdk:20261117-v1` 产生318,577,664字节未压缩tar，SHA-256为 `db002f912bf3a953635466ab2d38cf46e2d191377ebaff6552a30951c9a8e00e`。归档manifest只有一个Linux/amd64镜像，实际load后ID与上段一致，证据 `records/33-final-build.txt` 至 `records/41-after-load-id.txt`。完整416份冻结源码归档 `source-snapshot-3186ccd.zip` 为14,926,408字节，SHA-256 `8d8d14fc8ea6f6551f0aa15c6ad4dcd7d75c7cee70522f1e13577e1104c74429`；逐文件摘要见 `source-manifest-3186ccd.json`。另保留19,927,040字节Git原生tar，SHA-256 `2ebbb97f26622fcbadfb7802723bb64b3807c5538887aed9c9b6e475bfc140b5`。

平台新镜像仅上传尝试1次，页面明确返回“请求失败（502）”；刷新后仍只有2026/11/16的镜像1和旧v1/v2，没有新增镜像记录或版本。用户随后确认平台当前存在502上传故障，本轮停止重试。试运行仍为已用1/10、正式评测0/2，本轮均未消耗。这里是上传服务阻塞，不能据此判定新镜像协议失败，也不能声称已上传、已发布或平台验收通过。

公开GitHub仍是旧快照 `afe3820101b6f432a572bfbcdf80db2055705021`；三次命令行读取分别遇到连接重置/无法连接，网页可读但未登录，未推送任何修改。新冻结源码ZIP及清单已在本地准备；恢复后须先同步对应源码，再选择新镜像保存版本。没有读取、复制或公开API Key。

原始证据根目录：`outputs/contest-sdk-adapter-20261117/`。首次Linux smoke的测试宿主复用了候选ID，第二轮把保留的旧候选误当新候选，断言失败；已修正仅测试ID为每轮唯一，保留 `linux-smoke-v1`，复核 `linux-smoke-v2` 和最终30轮通过。未更改生产训练策略。
