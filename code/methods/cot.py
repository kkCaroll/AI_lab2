"""Chain-of-Thought，单次调用分步推理。"""

from ..common.extract import extract_answer
from ..common.llm import chat
from ..common.prompts import SYSTEM, cot_prompt


def solve(problem: str) -> dict:
    r = chat([{"role": "system", "content": SYSTEM},
              {"role": "user", "content": cot_prompt(problem)}])
    return {
        "answer": extract_answer(r["content"]),
        "output": r["content"],
        "prompt_tokens": r["prompt_tokens"],
        "completion_tokens": r["completion_tokens"],
        "calls": 1,
    }
