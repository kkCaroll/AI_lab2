"""自研系统的角色实现，解析固定的输出格式。"""

import re

from ..common.llm import chat
from . import prompts

_DIFFICULTY = re.compile(r"DIFFICULTY:\s*([1-5])")
_PLAN = re.compile(r"PLAN:\s*(.+)", re.IGNORECASE)


def _route(score: int) -> str:
    if score <= 1:
        return "easy"
    if score == 2:
        return "medium"
    return "hard"
_VERDICT = re.compile(r"VERDICT:\s*(PASS|FAIL)", re.IGNORECASE)
_CONFIDENCE = re.compile(r"CONFIDENCE:\s*(\d{1,3})")
_VERIFIED = re.compile(r"VERIFIED:\s*(YES|NO)", re.IGNORECASE)


def router(problem: str) -> dict:
    r = chat(
        [{"role": "system", "content": prompts.SYSTEM},
         {"role": "user", "content": prompts.router_prompt(problem)}],
        max_tokens=120,
    )
    match = _DIFFICULTY.search(r["content"])
    score = int(match.group(1)) if match else 2
    plan = _PLAN.search(r["content"])
    return {
        "score": score,
        "difficulty": _route(score),
        "plan": plan.group(1).strip() if plan else "",
        "text": r["content"],
        "prompt_tokens": r["prompt_tokens"],
        "completion_tokens": r["completion_tokens"],
    }


def solver(problem: str, plan: str = "") -> dict:
    user = prompts.solver_prompt(problem, plan) if plan else prompts.solver_prompt(problem)
    r = chat(
        [{"role": "system", "content": prompts.SYSTEM},
         {"role": "user", "content": user}],
        max_tokens=8192,
    )
    return {
        "text": r["content"],
        "prompt_tokens": r["prompt_tokens"],
        "completion_tokens": r["completion_tokens"],
    }


def verifier(problem: str, solution: str, subgoals: str = "") -> dict:
    r = chat(
        [{"role": "system", "content": prompts.SYSTEM},
         {"role": "user", "content": prompts.verify_prompt(problem, solution, subgoals)}],
        max_tokens=512,
    )
    verdict = _VERDICT.search(r["content"])
    confidence = _CONFIDENCE.search(r["content"])
    return {
        "verdict": verdict.group(1).upper() if verdict else "FAIL",
        "confidence": min(int(confidence.group(1)), 100) if confidence else 0,
        "text": r["content"],
        "prompt_tokens": r["prompt_tokens"],
        "completion_tokens": r["completion_tokens"],
    }


def reviser(problem: str, solution: str, feedback: str) -> dict:
    r = chat(
        [{"role": "system", "content": prompts.SYSTEM},
         {"role": "user", "content": prompts.revise_prompt(problem, solution, feedback)}],
        max_tokens=8192,
    )
    return {
        "text": r["content"],
        "prompt_tokens": r["prompt_tokens"],
        "completion_tokens": r["completion_tokens"],
    }


def parse_verified(text: str) -> bool:
    match = _VERIFIED.search(text)
    return bool(match and match.group(1).upper() == "YES")
