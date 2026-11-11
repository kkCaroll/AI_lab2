"""Self-Consistency，同一提示词独立采样五次后投票。"""

from collections import Counter

from ..common.extract import extract_answer
from ..common.llm import chat
from ..common.prompts import SYSTEM, cot_prompt

SAMPLES = 5


def vote(answers: list[str]) -> str:
    answers = [a for a in answers if a]
    if not answers:
        return ""
    counts = Counter(answers)
    best = max(counts.values())
    for answer in answers:
        if counts[answer] == best:
            return answer
    return answers[0]


def solve(problem: str) -> dict:
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": cot_prompt(problem)}]
    outputs, answers = [], []
    prompt_tokens = completion_tokens = 0
    for _ in range(SAMPLES):
        r = chat(messages)
        outputs.append(r["content"])
        answers.append(extract_answer(r["content"]))
        prompt_tokens += r["prompt_tokens"]
        completion_tokens += r["completion_tokens"]
    return {
        "answer": vote(answers),
        "output": outputs[0],
        "samples": answers,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "calls": SAMPLES,
    }
