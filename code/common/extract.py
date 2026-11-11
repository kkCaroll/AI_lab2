"""答案抽取、规范化与等价判定，六种方法共用。"""

import math
import re

from sympy import simplify
from sympy.parsing.latex import parse_latex

_BOXED = re.compile(r"\\boxed\s*\{")
_ANSWER_LINE = re.compile(
    r"(?:final\s+answer|answer)\s*(?:is|:)\s*(.+)", re.IGNORECASE
)


def _matching_brace(text: str, open_pos: int) -> int:
    depth = 0
    for i in range(open_pos, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _last_boxed(text: str) -> str:
    matches = list(_BOXED.finditer(text))
    if not matches:
        return ""
    start = matches[-1].end() - 1
    end = _matching_brace(text, start)
    return text[start + 1 : end] if end > start else ""


def extract_answer(text: str) -> str:
    """优先取最后一个 \\boxed，其次 answer is 行，最后取末行公式。"""
    if not text:
        return ""
    boxed = _last_boxed(text)
    if boxed.strip():
        return boxed.strip()

    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    hits = _ANSWER_LINE.findall("\n".join(lines))
    if hits:
        return hits[-1].strip().strip(".$")

    for line in reversed(lines):
        if "=" in line or "\\" in line:
            return line.strip(".$ ")
    return lines[-1].strip(".$ ") if lines else ""


_REPLACE = (
    (r"\\left\s*\.", ""),
    (r"\\right\s*\.", ""),
    (r"\\left", ""),
    (r"\\right", ""),
    (r"\\displaystyle", ""),
    (r"\\[dt]frac", r"\\frac"),
    (r"\\cdot", r"\\times"),
    (r"\\!", ""),
    (r"\\,", ""),
    (r"\\;", ""),
    (r"\\quad", ""),
    (r"\\qquad", ""),
    (r"\$", ""),
)


def normalize(answer: str) -> str:
    s = answer.strip()
    s = re.sub(r"^\\boxed\s*", "", s)
    for pattern, repl in _REPLACE:
        s = re.sub(pattern, repl, s)
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", s)
    s = s.rstrip(".,;:")
    return s


def _as_float(s: str):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _sympy_equal(a: str, b: str) -> bool:
    if len(a) > 120 or len(b) > 120:
        return False
    try:
        ea, eb = parse_latex(a), parse_latex(b)
        return simplify(ea - eb) == 0
    except Exception:
        return False


def is_equal(pred: str, gold: str) -> bool:
    a, b = normalize(pred), normalize(gold)
    if not a:
        return False
    if a == b:
        return True

    fa, fb = _as_float(a), _as_float(b)
    if fa is not None and fb is not None:
        return math.isclose(fa, fb, rel_tol=1e-6, abs_tol=1e-9)

    if _sympy_equal(a, b):
        return True

    if a.startswith("\\frac") and b.startswith("\\frac"):
        return False
    return False
