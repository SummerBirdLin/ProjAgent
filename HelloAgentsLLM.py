import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv
from typing import Dict, List, Any, cast

load_dotenv()

class HelloAgentsLLM:
    def __init__(self, model: str | None = None, apikey: str | None = None, baseUrl: str | None = None, timeout: int | None = None) -> None:
        model = model or os.getenv("LLM_MODEL_ID")
        apikey = apikey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        if not model or not apikey or not baseUrl:
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(api_key=apikey, base_url=baseUrl, timeout=timeout)
        self.model = model

    def think(self, messages: List[Dict[str, Any]], temperature: float = 0) -> str | None:

        print(f"正在调用{self.model}模型...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=cast(List[ChatCompletionMessageParam], messages),
                temperature=temperature,
                stream=True
            )

            print("模型响应成功:")
            print()

            collected_content = []

            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)

            print()
            return "".join(collected_content)
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None


if __name__ == "__main__":
    try:
        llm = HelloAgentsLLM()

        exampleMessage = [
            {"role": "system", "content": "You are a helpful assistant that writes Python code."},
            {"role": "user", "content": "写一个快速排序算法"}
        ]

        print("--- 调用LLM ---")
        responseText = llm.think(exampleMessage)
        
    except ValueError as e:
        print(e)
