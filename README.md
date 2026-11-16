# 智训引擎参赛镜像冻结源码

本仓库保存2026年11月16日续训适配镜像的冻结源码快照。下载并解压 source-snapshot.zip 即可获得完整源码树、测试、配置、固定依赖、tokenizer和官方baseline包。不要仅下载根目录的两个入口文件运行；它们供浏览器预览，完整依赖位于快照中。

运行源码提交：8853fca01e1180adccdd9cc51127334f0f3f4fad。此处为公开快照，仓库首个上传提交的SHA与原始运行提交不同。SOURCE_MANIFEST.json保存248份源码文件的逐文件摘要。

镜像：ite-continuation:20261116-v1。
Docker image ID：sha256:03d09b8b489a9abca2a31af608a3cbc010e150947d365b6523acf5ab0a6c7e7c。
harness.tar SHA-256：29c426ff06ebb8a4c8529648dc8114f1673b5b3bc7a789b97f0a0a270b14ae09。
ITE源码摘要：d6a6d0552b4675c205ca48af5117cc9b03ebc7509b27202d5f4a72d9902400f2。

## 运行接口

从实际指定的父模型和允许的数据开始CPU续训，每次调用执行一个真实轮次。首轮使用 --from-baseline，后续轮次使用 --resume 及累计history。默认不隐式运行开发对照，也不自动从镜像内初始模型重启。

```text
python train.py --profile C --train /input/train.jsonl --validation /input/validation.jsonl --from-baseline /input/checkpoint.npz --output /artifacts/round-1 --stage-id round-1
python train.py --profile C --train /input/train.jsonl --validation /input/validation-next.jsonl --resume /parent/checkpoint.npz --parent-history /parent/history.jsonl --output /artifacts/round-2 --stage-id round-2
python predict.py --checkpoint /artifacts/round-2/checkpoint.npz
```

完整合同见快照内 configs/continuation-contract.json。B需要 --label-provenance。预测从stdin读取只含inputs及可选task的JSONL，输出官方预测schema。

产物为checkpoint.npz、training.json、history.jsonl及C绑定sidecar（如有），模型目录总量检查64 MiB。详细审计单独保存。已有输出拒绝覆写。缺失父模型或schema错误拒绝运行，历史不完整时保留父模型并记录原因。

## 固定策略与已有证据

A固定step7、48行分层回放及5epoch，B保留父模型并如实记录0训练，C沿用head-only 2epoch与原触发。所有候选经过独立future gate，保留5秒候选、20秒流和最多4次训练尝试限制。梯度只使用允许的train。

宿主736/736测试通过。4CPU、4GiB、network none Linux测试735通过、1宿主专用跳过。A/B/C各两轮接线、24条官方预测器一致性及docker save/load验证通过。平台完整启动合同和10轮调度仍需平台回执，不能据本地接线结果宣称正式评测通过。

公开开发成绩：A Macro-F1 0.5742767490至0.5743703129（微增，未达预登记实质门槛）；B RMSE持平；C全流RMSE 106.9741809588至104.8312569644周期（约下降2.00%）。这些结果是已见公开模拟流，不是隐藏测试。原组合effect_passed=false保持。

Qwen3.5-4B动作SFT已有公开训练记录：https://swanlab.cn/@mring-Y/Intelligent_Training_Engine/runs/6w6q826b/chart 。该次SFT全选NO，未通过动作Macro-F1门槛。真实27B三包十轮是另一次工具实验：https://swanlab.cn/@mring-Y/Intelligent_Training_Engine/runs/al0xjnid/chart ，最终选定更新为0。不能混写为当前镜像的一次有效大模型自主优化。

## 来源与重建

快照内Dockerfile固定底层Python镜像摘要并附依赖锁文件。scripts/Dockerfile.platform继承固定旧策略镜像；重建时需要该已核对身份的本地父镜像，或按快照内完整Dockerfile重新准备固定基础运行环境。官方ZIP和tokenizer保留其原来源与权利，不因本仓库公开而重新许可。

本仓库不包含API Key、私有数据或隐藏测试标签。提交页中的PyTRiO凭据应通过平台凭据栏提供，不写入源码、日志或报告。
