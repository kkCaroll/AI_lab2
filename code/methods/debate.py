"""Multi-Agent Debate，三智能体四轮，首轮独立作答，末轮多数票。"""

from concurrent.futures import ThreadPoolExecutor

from ..common.extract import extract_answer, normalize
from ..common.llm import chat
from ..common.prompts import SYSTEM, cot_prompt, debate_round_prompt
from .self_consistency import vote

AGENTS = ("A", "B", "C")
ROUNDS = 4


def _messages(user: str) -> list[dict]:
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def solve(problem: str) -> dict:
    prompt_tokens = completion_tokens = calls = 0
    trace = []

    with ThreadPoolExecutor(max_workers=len(AGENTS)) as pool:
        results = list(pool.map(lambda _: chat(_messages(cot_prompt(problem))), AGENTS))
    responses = {}
    for name, r in zip(AGENTS, results):
        responses[name] = r["content"]
        prompt_tokens += r["prompt_tokens"]
        completion_tokens += r["completion_tokens"]
        calls += 1
        trace.append({"round": 1, "agent": name, "content": r["content"]})

    for round_idx in range(2, ROUNDS + 1):
        previous = [(name, responses[name]) for name in AGENTS]

        def ask(_name: str) -> dict:
            return chat(_messages(debate_round_prompt(problem, previous)))

        with ThreadPoolExecutor(max_workers=len(AGENTS)) as pool:
            results = list(pool.map(ask, AGENTS))

        updated = {}
        for name, r in zip(AGENTS, results):
            updated[name] = r["content"]
            prompt_tokens += r["prompt_tokens"]
            completion_tokens += r["completion_tokens"]
            calls += 1
            trace.append({"round": round_idx, "agent": name, "content": r["content"]})
        responses = updated

    answers = [normalize(extract_answer(responses[name])) for name in AGENTS]
    return {
        "answer": vote(answers),
        "output": responses[AGENTS[0]],
        "final_answers": dict(zip(AGENTS, answers)),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "calls": calls,
        "trace": trace,
    }
