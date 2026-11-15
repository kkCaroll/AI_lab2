"""难度自适应的多智能体系统，按难度选择角色并按置信度提前终止。"""

from ..common.extract import extract_answer
from . import agents, skills

BUDGET = 6500
CONFIDENCE_THRESHOLD = 75


def _text(result: dict) -> str:
    return result.get("text") or result.get("content", "")


def solve(problem: str) -> dict:
    prompt_tokens = completion_tokens = calls = 0
    trace: list[dict] = []
    skills_used: list[str] = []

    def log(step: str, result: dict, **extra) -> None:
        nonlocal prompt_tokens, completion_tokens, calls
        prompt_tokens += result["prompt_tokens"]
        completion_tokens += result["completion_tokens"]
        calls += 1
        trace.append({"step": step, "output": _text(result), **extra})

    def remaining() -> int:
        return BUDGET - (prompt_tokens + completion_tokens)

    route = agents.router(problem)
    difficulty = route["difficulty"]
    log("router", route, difficulty=difficulty, score=route.get("score"))
    plan = route["plan"] if difficulty != "easy" else ""

    solution = agents.solver(problem, plan)
    log("solver", solution, plan=plan)
    final_text = solution["text"]
    answer = extract_answer(final_text)

    if difficulty == "easy":
        return _result(answer, final_text, prompt_tokens, completion_tokens,
                       calls, trace, difficulty, skills_used, 0, "", 0)

    subgoals = ""
    if difficulty == "hard" and remaining() > 700:
        decomposed = skills.decompose(problem)
        log("skill_decompose", decomposed)
        skills_used.append("decompose")
        subgoals = _text(decomposed)

    verdict = agents.verifier(problem, final_text, subgoals)
    log("verifier", verdict, checked=final_text,
        verdict=verdict["verdict"], confidence=verdict["confidence"])
    passed = verdict["verdict"] == "PASS" and verdict["confidence"] >= CONFIDENCE_THRESHOLD
    confidence = verdict["confidence"]
    final_verdict = verdict["verdict"]

    if difficulty == "hard" and passed and remaining() > 700:
        check = skills.substitute_check(problem, answer)
        log("skill_substitute_check", check, candidate=answer)
        skills_used.append("substitute_check")
        passed = agents.parse_verified(_text(check))

    revisions = 0
    if not passed and remaining() > 500:
        revised = agents.reviser(problem, final_text, verdict["text"])
        log("reviser", revised, feedback=verdict["text"])
        revisions = 1
        final_text = revised["text"]
        answer = extract_answer(final_text)

        if remaining() > 900:
            recheck = agents.verifier(problem, final_text, subgoals)
            log("verifier_recheck", recheck,
                verdict=recheck["verdict"], confidence=recheck["confidence"])
            confidence = recheck["confidence"]
            final_verdict = recheck["verdict"]

    return _result(answer, final_text, prompt_tokens, completion_tokens,
                   calls, trace, difficulty, skills_used, revisions,
                   final_verdict, confidence)


def _result(answer, output, prompt_tokens, completion_tokens, calls, trace,
            difficulty, skills_used, revisions, verdict, confidence) -> dict:
    return {
        "answer": answer,
        "output": output,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "calls": calls,
        "trace": trace,
        "difficulty": difficulty,
        "skills_used": skills_used,
        "revisions": revisions,
        "verdict": verdict,
        "confidence": confidence,
    }
