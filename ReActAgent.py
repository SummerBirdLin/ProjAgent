from prompt import REACT_PROMPT_TEMPLATE
from HelloAgentsLLM import HelloAgentsLLM
from ToolExecutor import ToolExecutor
import re
from action import search

class ReActAgent:
    def __init__(self, client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 6) -> None:
        self.client = client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- 第 {current_step} 步 ---")

            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)

            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str
            )

            messages = [{"role": "user", "content": prompt}]
            response = self.client.think(messages=messages)

            if not response:
                print("错误: LLM 未能返回有效响应。")
                break

            thought, action = self._parse_output(response)

            if not action:
                print("警告: 未能解析出有效的 Action，流程终止。")
                break

            # 👈 核心修改：统一使用 _parse_action 解析，自带 re.DOTALL，完美支持多行答案
            tool_name, tool_input = self._parse_action(action)
            if not tool_name:
                print(f"警告: 无法识别 Action 格式: {action}")
                break

            # 如果是 Finish，直接返回最终答案
            if tool_name == "Finish":
                print(f"🎉 最终答案: {tool_input}")
                return tool_input

            print(f"🎬 行动: {tool_name}[{tool_input}]")
            tool_function = self.tool_executor.getTool(tool_name)

            if not tool_function:
                observation = f"错误: 未找到名为 '{tool_name}' 的工具。"
            else:
                observation = tool_function(tool_input)

            print(f"👀 观察: {observation}")
            
            # 将当前轮次的交互记入历史
            self.history.append(f"Thought: {thought}")
            self.history.append(f"Action: {tool_name}[{tool_input}]")
            self.history.append(f"Observation: {observation}")

        print("已达到最大步数，流程终止。")
        return None

    def _parse_output(self, text: str):
        """解析LLM的输出，提取Thought和Action。只提取第一个Action，防止模型多说。"""
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        # 👈 核心修改：遇到下一个 Thought 或多余文本时截断，避免贪婪抓取后面的自导自演内容
        action_match = re.search(r"Action:\s*(.*?)(?=\nThought:|\nObservation:|```|$)", text, re.DOTALL)
        
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        """解析Action字符串，提取工具名称和输入。"""
        # 优先严格匹配 Tool[Input]
        match = re.match(r"^(\w+)\[(.*)\]$", action_text.strip(), re.DOTALL)
        if not match:
            # 容错：如果末尾带有多余字符，搜索第一个合法的 Tool[...]
            match = re.search(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None

if __name__ == '__main__':
    llm = HelloAgentsLLM()
    tool_executor = ToolExecutor()
    search_desc = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    tool_executor.registerTool("Search", search_desc, search)
    agent = ReActAgent(client=llm, tool_executor=tool_executor)
    question = "华为最新的手机是哪一款？它的主要卖点是什么？"
    agent.run(question)