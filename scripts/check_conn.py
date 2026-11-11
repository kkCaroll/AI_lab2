"""连通性检查：调用一次模型并可选加载 MATH-500。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from code.common.llm import chat


def main() -> None:
    if "--data" in sys.argv:
        from datasets import load_dataset

        ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
        print(f"数据集样例数 {len(ds)}，字段 {ds.column_names}")
        print(ds[0]["problem"][:200])
        print("answer:", ds[0]["answer"], "level:", ds[0]["level"])

    out = chat([{"role": "user", "content": "Solve: if x + 5 = 12, what is x?"}])
    print("模型回复:", out["content"])
    print(
        f"tokens 输入 {out['prompt_tokens']} 输出 {out['completion_tokens']}"
    )


if __name__ == "__main__":
    main()
