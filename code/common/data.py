"""MATH-500 加载，题面与参考答案分开暴露。"""

from datasets import load_dataset

NAME = "HuggingFaceH4/MATH-500"
PROBLEM_FIELDS = ("unique_id", "problem", "level", "subject")


def _load():
    return load_dataset(NAME, split="test")


def load_problems() -> list[dict]:
    """只含题面与元信息，不含 answer 与 solution。"""
    return [{k: row[k] for k in PROBLEM_FIELDS} for row in _load()]


def load_references() -> dict[str, str]:
    """仅评分阶段调用，返回 unique_id 到 answer 的映射。"""
    return {row["unique_id"]: row["answer"] for row in _load()}


def load_solutions() -> dict[str, str]:
    """仅供人工分析，不进入任何提示词。"""
    return {row["unique_id"]: row["solution"] for row in _load()}
