"""提示词模板，六种方法共用同一答案格式约束。"""

SYSTEM = (
    "You are a careful mathematical problem solver. "
    "Reason rigorously and keep the final answer as a single expression. "
    "The final answer must be enclosed in \\boxed{}."
)


def direct_prompt(problem: str) -> str:
    return (
        f"{problem}\n\n"
        "Give only the final answer, enclosed in \\boxed{}. Do not show reasoning."
    )


def cot_prompt(problem: str) -> str:
    return (
        f"{problem}\n\n"
        "Solve the problem step by step. "
        "Put the final answer in \\boxed{} on the last line."
    )


def critique_prompt(problem: str, solution: str) -> str:
    return (
        f"Problem:\n{problem}\n\n"
        f"Proposed solution:\n{solution}\n\n"
        "Check the solution step by step. "
        "If the reasoning and the final answer are both correct, "
        "reply with CORRECT as the first line and nothing else. "
        "Otherwise state the error and the corrected final answer in \\boxed{}."
    )


def revise_prompt(problem: str, solution: str, critique: str) -> str:
    return (
        f"Problem:\n{problem}\n\n"
        f"Proposed solution:\n{solution}\n\n"
        f"Review feedback:\n{critique}\n\n"
        "Write a corrected complete solution. "
        "Put the final answer in \\boxed{} on the last line."
    )


def debate_round_prompt(problem: str, responses: list[tuple[str, str]]) -> str:
    shown = "\n\n".join(f"Agent {name}:\n{text}" for name, text in responses)
    return (
        f"Problem:\n{problem}\n\n"
        f"Solutions from the previous round:\n{shown}\n\n"
        "Compare the solutions above with your own. "
        "If another agent found an error in your reasoning, correct it. "
        "Write your complete revised solution and put the final answer in \\boxed{}."
    )
