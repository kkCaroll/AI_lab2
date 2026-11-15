"""可复用推理 Skill，由不同角色按需调用。"""

from ..common.llm import chat
from . import prompts


def decompose(problem: str) -> dict:
    """子目标分解，供 Planner 调用。"""
    return chat(
        [{"role": "system", "content": prompts.SYSTEM},
         {"role": "user", "content": prompts.decompose_prompt(problem)}],
        max_tokens=300,
    )


def substitute_check(problem: str, answer: str) -> dict:
    """候选答案代回检验，供 Verifier 调用。"""
    return chat(
        [{"role": "system", "content": prompts.SYSTEM},
         {"role": "user", "content": prompts.substitute_prompt(problem, answer)}],
        max_tokens=300,
    )
