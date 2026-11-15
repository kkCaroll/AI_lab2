"""统计自研系统的路由分布、Skill 使用与 token。"""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from code.common.data import load_references
from code.common.extract import is_equal
from code.common.scorer import load_records


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "results/raw/mas.jsonl")
    records = load_records(path)
    references = load_references()

    meta = [r.get("meta", {}) for r in records]
    difficulties = Counter(m.get("difficulty") for m in meta)
    skills = Counter(s for m in meta for s in m.get("skills_used", []))
    revisions = Counter(m.get("revisions", 0) for m in meta)
    calls = sum(r["calls"] for r in records) / len(records)
    token_in = sum(r["prompt_tokens"] for r in records) / len(records)
    token_out = sum(r["completion_tokens"] for r in records) / len(records)
    correct = sum(is_equal(r["answer"], references[r["unique_id"]]) for r in records)

    print(f"题数 {len(records)} 准确率 {correct / len(records) * 100:.2f}")
    print(f"难度分布 {dict(difficulties)}")
    print(f"Skill 调用 {dict(skills)}")
    print(f"修订轮数 {dict(revisions)}")
    print(f"平均调用 {calls:.2f} 输入 {token_in:.0f} 输出 {token_out:.0f} "
          f"合计 {token_in + token_out:.0f}")
    over = sum(1 for r in records if r["prompt_tokens"] + r["completion_tokens"] > 6500)
    print(f"单题超过 6500 的题数 {over}")


if __name__ == "__main__":
    main()
