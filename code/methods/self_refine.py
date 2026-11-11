"""Self-Refine，初答后自评并按反馈修改，最多三轮反馈。"""

from ..common.extract import extract_answer
from ..common.llm import chat
from ..common.prompts import SYSTEM, cot_prompt, critique_prompt, revise_prompt

MAX_ROUNDS = 3


def _is_correct(critique: str) -> bool:
    first = critique.strip().splitlines()[0].strip().upper() if critique.strip() else ""
    return first.startswith("CORRECT")


def solve(problem: str) -> dict:
    r = chat([{"role": "system", "content": SYSTEM},
              {"role": "user", "content": cot_prompt(problem)}])
    solution = r["content"]
    prompt_tokens, completion_tokens, calls = r["prompt_tokens"], r["completion_tokens"], 1
    rounds = 0

    for _ in range(MAX_ROUNDS):
        c = chat([{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": critique_prompt(problem, solution)}])
        prompt_tokens += c["prompt_tokens"]
        completion_tokens += c["completion_tokens"]
        calls += 1
        if _is_correct(c["content"]):
            break
        r = chat([{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": revise_prompt(problem, solution, c["content"])}])
        solution = r["content"]
        prompt_tokens += r["prompt_tokens"]
        completion_tokens += r["completion_tokens"]
        calls += 1
        rounds += 1

    return {
        "answer": extract_answer(solution),
        "output": solution,
        "rounds": rounds,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "calls": calls,
    }
