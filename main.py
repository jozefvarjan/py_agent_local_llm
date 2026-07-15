import os

from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver

from tools import TOOLS

# Ollama chat model. Must support tool calling.
CHAT_MODEL = os.environ.get("CHAT_MODEL", "qwen3.5:0.8b")

# Base URL of the Ollama server. Override with OLLAMA_BASE_URL when running in a
# container (e.g. http://host.docker.internal:11434 to reach Ollama on the host).
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to tools for getting the current time and counting words in text. "
    "Use tools when the user's request needs one. "
    "If the question doesn't need a tool, answer directly. "
    "If a tool returns an error, explain the error plainly."
)


def build_agent():
    model = ChatOllama(model=CHAT_MODEL, temperature=0, base_url=OLLAMA_BASE_URL)

    # InMemorySaver keeps conversation history in memory, keyed by thread ID.
    # When the process exits, the history is gone because of short-term memory.
    checkpointer = InMemorySaver()

    return create_agent(
        model=model,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )


def main():
    agent = build_agent()

    # The thread ID tells the checkpointer which conversation to load and save.
    config = {"configurable": {"thread_id": "thread"}}

    print("Ready! Ask the agent something. It remembers the conversation.\n")

    # Track how many messages existed before this turn, so we can slice out
    # only the new ones (tool calls + final answer) from the returned state.
    prev_message_count = 0

    while True:
        question = input("You: ").strip()
        if not question or question.lower() == "exit":
            break

        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config=config,
        )

        # Only look at messages added during this turn, not the full history.
        new_messages = result["messages"][prev_message_count:]

        # Print any tool calls made in this turn.
        for msg in new_messages:
            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                for call in tool_calls:
                    print(f"[tool call] {call['name']}({call['args']})")

        print(f"\nAnswer: {result['messages'][-1].content}\n")

        # Update the count for the next turn.
        prev_message_count = len(result["messages"])



if __name__ == "__main__":
    main()