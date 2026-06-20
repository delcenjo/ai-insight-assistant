from .config import CHAT_MODEL, MAX_STEPS
from .tools import Toolbox

SYSTEM_PROMPT = (
    "You are Helios's internal assistant. Use search_docs for questions about "
    "company policies and processes, and query_database for questions about "
    "employees, departments and salaries. Base every answer on tool results and "
    "cite document sources when you use them. Be concise."
)


class Assistant:
    def __init__(self, model=CHAT_MODEL, max_steps=MAX_STEPS):
        import anthropic

        self.client = anthropic.Anthropic()
        self.model = model
        self.max_steps = max_steps
        self.toolbox = Toolbox()

    def run(self, message):
        messages = [{"role": "user", "content": message}]
        for _ in range(self.max_steps):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=Toolbox.DEFINITIONS,
                messages=messages,
            )
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                return "".join(block.text for block in response.content if block.type == "text")

            tool_results = [
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": self.toolbox.execute(block.name, block.input),
                }
                for block in response.content
                if block.type == "tool_use"
            ]
            messages.append({"role": "user", "content": tool_results})

        return "Stopped: reached the maximum number of tool-use steps."
