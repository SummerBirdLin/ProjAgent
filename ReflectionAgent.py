from HelloAgentsLLM import HelloAgentsLLM
from Memory import Memory
from prompt import INITIAL_PROMPT_TEMPLATE, REFLECT_PROMPT_TEMPLATE, REFINE_PROMPT_TEMPLATE


class ReflectionAgent:
    def __init__(self, client: HelloAgentsLLM, max_iterations: int = 3):
        self.client = client
        self.max_iterations = max_iterations
        self.memory = Memory()

    def _get_llm_response(self, prompt: str) -> str:
        """一个辅助方法，用于调用LLM并获取完整的流式响应。"""
        messages = [{"role": "user", "content": prompt}]
        response_text = self.client.think(messages=messages) or ""
        return response_text

    def run(self, task: str):
        print(f"\n--- 开始处理任务 ---\n任务: {task}")

        print("\n--- 正在进行初始尝试 ---")
        init_prompt = INITIAL_PROMPT_TEMPLATE.format(task=task)
        init_response = self._get_llm_response(init_prompt)
        self.memory.add_record("execution", init_response)

        for i in range(self.max_iterations):
            print(f"\n--- 第 {i+1}/{self.max_iterations} 轮迭代 ---")

            print("\n-> 正在进行反思...")
            last_code = self.memory.get_last_execution()
            reflect_prompt = REFLECT_PROMPT_TEMPLATE.format(task=task, code=last_code)
            feed_back = self._get_llm_response(reflect_prompt)
            self.memory.add_record("reflection", feed_back)

            if "无需改进" in feed_back:
                print("\n✅ 反思认为代码已无需改进，任务完成。")
                break

            print("\n-> 正在进行优化...")
            refine_prompt = REFINE_PROMPT_TEMPLATE.format(
                task=task,
                last_code_attempt=last_code,
                feedback=feed_back
            )
            refined_code = self._get_llm_response(refine_prompt)
            self.memory.add_record("execution", refined_code)

        final_code = self.memory.get_last_execution()

        print(f"\n--- 任务完成 ---\n最终生成的代码:\n```python\n{final_code}\n```")
        return final_code


if __name__ == '__main__':
    try:
        llm_client = HelloAgentsLLM()
    except Exception as e:
        print(f"初始化LLM客户端时出错: {e}")
        exit()


    agent = ReflectionAgent(llm_client, max_iterations=3)

    task = "编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。"
    agent.run(task)