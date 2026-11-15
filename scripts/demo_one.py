"""现场验收用，运行或回放一道题，打印每个角色的输出与传递内容。"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from code.common.data import load_problems
from code.mas.system import solve


def show(trace: list[dict], answer: str, tokens: tuple[int, int]) -> None:
    for i, step in enumerate(trace, 1):
        print(f"\n[{i}] {step['step']}")
        for key in ("plan", "checked", "candidate", "feedback", "verdict", "confidence"):
            if key in step and step[key]:
                print(f"  传入 {key}: {str(step[key])[:300]}")
        print("  输出:")
        for line in step["output"].splitlines():
            print(f"    {line}")
    print(f"\n最终答案: {answer}")
    print(f"token 输入 {tokens[0]} 输出 {tokens[1]} 合计 {sum(tokens)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--replay", action="store_true", help="从结果文件回放，不调用接口")
    parser.add_argument("--file", default="results/raw/mas.jsonl")
    args = parser.parse_args()

    if args.replay:
        with open(args.file, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                if rec["unique_id"] == args.id:
                    show(rec.get("trace", []), rec["answer"],
                         (rec["prompt_tokens"], rec["completion_tokens"]))
                    return
        raise SystemExit(f"未找到 {args.id}")

    problems = {p["unique_id"]: p for p in load_problems()}
    problem = problems[args.id]
    print(f"题目 {args.id} 难度 L{problem['level']}")
    print(problem["problem"])
    out = solve(problem["problem"])
    show(out["trace"], out["answer"], (out["prompt_tokens"], out["completion_tokens"]))


if __name__ == "__main__":
    main()
