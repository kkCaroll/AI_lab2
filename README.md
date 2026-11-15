# 实验二 多智能体系统设计与评测

统一模型 qwen3.7-flash，数据 HuggingFaceH4/MATH-500 全量 500 题，比较五种规定方法与一种自研多智能体系统。

## 目录

```
code/common/   配置、模型调用、数据、答案抽取、评分、运行器
code/methods/  Direct、CoT、Self-Consistency、Self-Refine、Multi-Agent Debate
code/mas/      自研系统的角色、Skill 与调度
scripts/       运行、汇总、演示与检查
PLAN/          实验计划
LOG/           实验日志
REPORT/        LaTeX 报告
results/       原始输出与汇总表，不提交
```

## 环境

```
pip install -r requirements.txt
```

在项目根目录创建 `.env`，写入

```
DASHSCOPE_API_KEY=你的密钥
DASHSCOPE_BASE_URL=https://ws-v8k13sn68qxgwzps.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
```

## 运行

```
python scripts/run_eval.py cot --workers 8
python scripts/run_eval.py mas --workers 8
python scripts/run_all.py --per-level 10
python scripts/summarize.py --total 500
```

结果写入 `results/raw/{method}.jsonl`，按 unique_id 去重，可断点续跑。

数据集已缓存在本机，运行前设置离线变量，否则 datasets 会向 HuggingFace 发起连通性检查而长时间等待。

```
export HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1
```

## 现场演示

```
python scripts/demo_one.py --id test/precalculus/1303.json
python scripts/demo_one.py --id test/precalculus/1303.json --replay
```

第一条命令实时运行并打印每个角色的输出、传递内容与 token，第二条从已保存结果回放。

## 评测口径

答案抽取对六种方法一致，优先取最后一个 `\boxed{}`。准确率以 500 题为分母，分难度准确率以该难度题数为分母。token 分输入与输出累计后除以 500。请求失败、空输出与抽取失败单独计数，不从分母中剔除。自研系统平均每题总 token 不得超过 6500。
