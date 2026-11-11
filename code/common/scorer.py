"""结果统计，分母固定为 500 与各难度题数。"""

import json
from pathlib import Path

from .extract import is_equal

LEVELS = ("1", "2", "3", "4", "5")


def load_records(path: str | Path) -> list[dict]:
    records = []
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def evaluate(
    records: list[dict],
    references: dict[str, str],
    levels: dict[str, str],
    total: int = 500,
) -> dict:
    per_level = {lv: [0, 0] for lv in LEVELS}
    token_in = token_out = 0
    failures = {"request_failed": 0, "empty_output": 0, "extract_failed": 0}
    correct_total = 0

    for rec in records:
        uid = rec["unique_id"]
        ok = bool(rec.get("answer")) and is_equal(rec["answer"], references.get(uid, ""))
        level = str(rec.get("level", levels.get(uid, "")))
        if level in per_level:
            per_level[level][1] += 1
            per_level[level][0] += int(ok)
        correct_total += int(ok)
        token_in += rec.get("prompt_tokens", 0)
        token_out += rec.get("completion_tokens", 0)
        if rec.get("failure") in failures:
            failures[rec["failure"]] += 1

    return {
        "n_records": len(records),
        "overall": correct_total / total,
        "levels": {lv: (c / n if n else 0.0) for lv, (c, n) in per_level.items()},
        "level_counts": {lv: n for lv, (_, n) in per_level.items()},
        "input_tokens": token_in / total,
        "output_tokens": token_out / total,
        "total_tokens": (token_in + token_out) / total,
        "failures": failures,
        "missing": total - len(records),
    }


def format_row(method: str, result: dict) -> str:
    cells = [
        method,
        f"{result['overall'] * 100:.2f}",
        *[f"{result['levels'][lv] * 100:.2f}" for lv in LEVELS],
        f"{result['input_tokens']:.0f}",
        f"{result['output_tokens']:.0f}",
    ]
    return " | ".join(cells)


def write_csv(rows: list[tuple[str, dict]], path: str | Path) -> None:
    header = "method,overall,L1,L2,L3,L4,L5,input_tokens,output_tokens"
    lines = [header]
    for method, r in rows:
        lines.append(
            ",".join(
                [
                    method,
                    f"{r['overall']:.4f}",
                    *[f"{r['levels'][lv]:.4f}" for lv in LEVELS],
                    f"{r['input_tokens']:.1f}",
                    f"{r['output_tokens']:.1f}",
                ]
            )
        )
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
