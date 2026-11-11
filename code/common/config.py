"""全局实验配置，所有方法共用。"""

import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
BASE_URL = os.getenv(
    "DASHSCOPE_BASE_URL",
    "https://ws-v8k13sn68qxgwzps.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
)
MODEL = "qwen3.7-flash"

# 六种方法统一解码参数；temperature 需大于 0 才能让 Self-Consistency 的多次采样产生差异
DECODE = {
    "temperature": 0.7,
    "top_p": 0.8,
    "max_tokens": 2048,
    "enable_thinking": False,
}
