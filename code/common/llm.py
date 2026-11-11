"""OpenAI 兼容接口封装，统一返回文本与 token 用量。"""

import time

from openai import OpenAI

from .config import API_KEY, BASE_URL, DECODE, MODEL

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not API_KEY:
            raise RuntimeError("未设置 DASHSCOPE_API_KEY")
        _client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    return _client


def chat(messages: list[dict], retries: int = 3, **override) -> dict:
    """单次调用，返回 content 与 prompt/completion token 数。"""
    params = {**DECODE, **override}
    enable_thinking = params.pop("enable_thinking", False)
    for attempt in range(retries):
        try:
            resp = get_client().chat.completions.create(
                model=MODEL,
                messages=messages,
                stream=False,
                extra_body={"enable_thinking": enable_thinking},
                **params,
            )
            msg = resp.choices[0].message
            return {
                "content": msg.content or "",
                "reasoning": getattr(msg, "reasoning_content", None),
                "prompt_tokens": resp.usage.prompt_tokens,
                "completion_tokens": resp.usage.completion_tokens,
            }
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2**attempt)
