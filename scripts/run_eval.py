"""运行指定方法，结果写入 results/raw/{method}.jsonl。"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from code.common.data import load_problems
from code.common.runner import Runner
from code.methods import cot, debate, direct, self_consistency, self_refine

METHODS = {
    "direct": direct.solve,
    "cot": cot.solve,
    "self_consistency": self_consistency.solve,
    "self_refine": self_refine.solve,
    "debate": debate.solve,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("method", choices=METHODS)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out-dir", default="results/raw")
    args = parser.parse_args()

    problems = load_problems()
    runner = Runner(args.method, METHODS[args.method],
                    out_dir=args.out_dir, workers=args.workers)
    records = runner.run(problems, limit=args.limit)
    failed = sum(1 for r in records if r["failure"])
    print(f"{args.method} 本次完成 {len(records)} 题，失败 {failed} 题")


if __name__ == "__main__":
    main()
