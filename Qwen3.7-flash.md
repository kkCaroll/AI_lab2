QpenAI 兼容地址
https://ws-v8k13sn68qxgwzps.cn-beijing.maas.aliyuncs.com/compatible-mode/v1

模型名
qwen3.7-flash

测试代码
```python
import os
from openai import OpenAI

# 1. 配置客户端 (Base URL 对应华北2北京地域)
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"), # 确保已设置环境变量
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 2. 准备一条测试消息 (模拟 MATH-500 题目)
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Solve: If x + 5 = 12, what is the value of x?"}
]

# 3. 调用模型，关键是在 extra_body 中关闭 thinking
try:
    completion = client.chat.completions.create(
        model="qwen3.7-flash",  # 模型 ID
        messages=messages,
        temperature=0.1,        # 实验要求六种方法统一解码参数，此处仅为示例
        extra_body={"enable_thinking": False}, # 核心：关闭思考模式
        stream=False,           # 实验场景通常用非流式，便于统一抽取答案
    )
    
    # 4. 提取答案与 Token 消耗 (实验报告需要记录)
    content = completion.choices[0].message.content
    usage = completion.usage
    
    print("模型回答：\n", content)
    print(f"\nToken消耗 - 输入: {usage.prompt_tokens}, 输出: {usage.completion_tokens}, 总计: {usage.total_tokens}")

except Exception as e:
    print(f"调用失败: {e}")
```

