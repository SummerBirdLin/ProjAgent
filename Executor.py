from HelloAgentsLLM import HelloAgentsLLM
from prompt import EXECUTOR_PROMPT_TEMPLATE

class Executor:
    def __init__(self, client: HelloAgentsLLM) -> None:
        self.client = client

    def execute(self, question: str, plan: list[str]) -> str | None:
        history = ""
        final_answer = ""

        print("\n--- 正在执行计划 ---")

        for i, step in enumerate(plan):
            print(f"\n-> 正在执行步骤 {i+1}/{len(plan)}: {step}")

            prompt = EXECUTOR_PROMPT_TEMPLATE.format(question=question, plan=plan, history=history or "无", current_step=step)
            messages = [{"role": "user", "content": prompt}]
            response = self.client.think(messages)

            history += f"步骤 {i+1}: {step}\n结果: {response}\n\n"

            print(f"✅ 步骤 {i+1} 已完成，结果: {response}")

            if i == len(plan) - 1:
                final_answer = response

        return final_answer
