"""汇总指定目录下所有方法的结果，输出表格。"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from code.common.data import load_problems, load_references
from code.common.scorer import LEVELS, evaluate, format_row, load_records, write_csv

ORDER = ["direct", "cot", "self_consistency", "self_refine", "debate", "mas"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="results/raw")
    args = parser.parse_args()

    problems = load_problems()
    levels = {p["unique_id"]: str(p["level"]) for p in problems}
    references = load_references()

    rows = []
    for path in sorted(Path(args.dir).glob("*.jsonl")):
        method = path.stem
        result = evaluate(load_records(path), references, levels)
        rows.append((method, result))
    rows.sort(key=lambda x: ORDER.index(x[0]) if x[0] in ORDER else len(ORDER))

    header = ["method", "overall", *[f"L{lv}" for lv in LEVELS], "input", "output"]
    print(" | ".join(header))
    for method, result in rows:
        print(format_row(method, result))
        print(
            f"  n={result['n_records']} missing={result['missing']} "
            f"failures={result['failures']}"
        )

    out_path = Path(args.dir) / "summary.csv"
    write_csv(rows, out_path)
    print(f"已写入 {out_path}")


if __name__ == "__main__":
    main()
