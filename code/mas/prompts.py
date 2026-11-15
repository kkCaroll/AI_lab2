"""自研系统各角色与 Skill 的提示词。"""

SYSTEM = (
    "You are part of a multi-agent math solving system. "
    "Follow the required output format exactly. "
    "Final answers must be single expressions enclosed in \\boxed{}."
)


def router_prompt(problem: str) -> str:
    return (
        f"{problem}\n\n"
        "Estimate the difficulty of this problem on a scale from 1 to 5, "
        "where 1 is a single direct step and 5 is a hard olympiad problem "
        "that needs several techniques. Do not show reasoning. "
        "Reply in exactly this format:\n"
        "DIFFICULTY: an integer from 1 to 5\n"
        "PLAN: one short sentence outlining the solution approach."
    )


def decompose_prompt(problem: str) -> str:
    return (
        f"{problem}\n\n"
        "Break this problem into 2 to 5 ordered subgoals that a solver can follow. "
        "Do not solve the problem. Keep the answer under 120 words."
    )


def solver_prompt(problem: str, plan: str = "") -> str:
    if plan:
        return (
            f"{problem}\n\n"
            f"Plan:\n{plan}\n\n"
            "Solve the problem step by step following the plan. "
            "Put the final answer in \\boxed{} on the last line."
        )
    return (
        f"{problem}\n\n"
        "Solve the problem step by step. "
        "Put the final answer in \\boxed{} on the last line."
    )


def verify_prompt(problem: str, solution: str, subgoals: str = "") -> str:
    extra = ""
    if subgoals:
        extra = (
            f"Subgoals listed before solving:\n{subgoals}\n\n"
            "Check whether the solution covers every subgoal and whether the "
            "final answer follows from them.\n\n"
        )
    return (
        f"Problem:\n{problem}\n\n"
        f"Solution to check:\n{solution}\n\n"
        f"{extra}"
        "Check the reasoning and the final answer. "
        "Reply in exactly this format:\n"
        "VERDICT: PASS or FAIL\n"
        "CONFIDENCE: an integer from 0 to 100\n"
        "FEEDBACK: one short paragraph, naming the first error if any."
    )


def substitute_prompt(problem: str, answer: str) -> str:
    return (
        f"Problem:\n{problem}\n\n"
        f"Candidate answer: {answer}\n\n"
        "Verify the candidate by substituting it back into the conditions of the problem "
        "or by an independent numerical check. "
        "Reply in exactly this format:\n"
        "VERIFIED: YES or NO\n"
        "REASON: one short paragraph."
    )


def revise_prompt(problem: str, solution: str, feedback: str) -> str:
    return (
        f"Problem:\n{problem}\n\n"
        f"Previous solution:\n{solution}\n\n"
        f"Review feedback:\n{feedback}\n\n"
        "Write a corrected complete solution. "
        "Put the final answer in \\boxed{} on the last line."
    )
