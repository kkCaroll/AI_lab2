"""Multi-Agent Debate，三智能体四轮，首轮独立作答，末轮多数票。"""

from ..common.extract import extract_answer
from ..common.llm import chat
from ..common.prompts import SYSTEM, cot_prompt, debate_round_prompt
from .self_consistency import vote

AGENTS = ("A", "B", "C")
ROUNDS = 4


def solve(problem: str) -> dict:
    prompt_tokens = completion_tokens = calls = 0
    trace = []

    responses = {}
    for name in AGENTS:
        r = chat([{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": cot_prompt(problem)}])
        responses[name] = r["content"]
        prompt_tokens += r["prompt_tokens"]
        completion_tokens += r["completion_tokens"]
        calls += 1
        trace.append({"round": 1, "agent": name, "content": r["content"]})

    for round_idx in range(2, ROUNDS + 1):
        previous = [(name, responses[name]) for name in AGENTS]
        updated = {}
        for name in AGENTS:
            r = chat([{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": debate_round_prompt(problem, previous)}])
            updated[name] = r["content"]
            prompt_tokens += r["prompt_tokens"]
            completion_tokens += r["completion_tokens"]
            calls += 1
            trace.append({"round": round_idx, "agent": name, "content": r["content"]})
        responses = updated

    answers = [extract_answer(responses[name]) for name in AGENTS]
    return {
        "answer": vote(answers),
        "output": responses[AGENTS[0]],
        "final_answers": dict(zip(AGENTS, answers)),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "calls": calls,
        "trace": trace,
    }
