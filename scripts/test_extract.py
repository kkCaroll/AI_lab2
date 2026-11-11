"""抽取与等价判定的单元检查。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from code.common.extract import extract_answer, is_equal, normalize

EXTRACT_CASES = [
    ("所以最终结果为 \\boxed{7}", "7"),
    ("\\boxed{\\frac{1}{2}}", "\\frac{1}{2}"),
    ("先得 \\boxed{3}，再得 \\boxed{-2}", "-2"),
    ("Thus the answer is 42.", "42"),
    ("Final answer: $\\dfrac{5}{4}$", "\\dfrac{5}{4}"),
    ("", ""),
]

EQUAL_CASES = [
    ("7", "7.0", True),
    ("\\frac{1}{2}", "0.5", True),
    ("\\dfrac{1}{2}", "\\frac{1}{2}", True),
    ("1,000", "1000", True),
    ("\\binom{5}{2}", "10", True),
    ("\\sqrt{2}", "1.414", False),
    ("x=7", "7", False),
    ("", "7", False),
    ("\\{1,2\\}", "\\{1,2\\}", True),
]

NORMALIZE_CASES = [
    ("\\dfrac{1}{2}", "\\frac{1}{2}"),
    ("$1,000$", "1000"),
    ("\\left( 3, \\frac{\\pi}{2} \\right)", "(3,\\frac{\\pi}{2})"),
]


def main() -> None:
    bad = 0
    for text, want in EXTRACT_CASES:
        got = extract_answer(text)
        if got != want:
            bad += 1
            print(f"抽取失败 {text!r} 期望 {want!r} 实际 {got!r}")

    for text, want in NORMALIZE_CASES:
        got = normalize(text)
        if got != want:
            bad += 1
            print(f"规范化失败 {text!r} 期望 {want!r} 实际 {got!r}")

    for pred, gold, want in EQUAL_CASES:
        got = is_equal(pred, gold)
        if got != want:
            bad += 1
            print(f"判定失败 {pred!r} 对 {gold!r} 期望 {want} 实际 {got}")

    total = len(EXTRACT_CASES) + len(NORMALIZE_CASES) + len(EQUAL_CASES)
    print(f"共 {total} 例，失败 {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
