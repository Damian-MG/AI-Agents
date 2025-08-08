from dotenv import load_dotenv
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

load_dotenv()

llm = init_chat_model(model="gemini-2.5-pro",
                      model_provider="google_genai"
                      )


class MessageClassifier(BaseModel):
    message_type: Literal["cat", "dog"] = Field(
        ...,
        description="Classify if the message talks about cat or dogs."
    )


class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_types: str | None


def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)

    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either:
            - 'cat': if it asks for cat information
            - 'dog': if it asks for dog information
            """
        },
        {"role": "user", "content": last_message.content}
    ])
    return {"message_type": result.message_type}


def router(state: State):
    message_type = state.get("message_type", "cat")
    if message_type == "dog":
        return {"next": "dog"}
    return {"next": "cat"}


def cat_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {
            "role": "system",
            "content": """You are a cat vet who talks like Mario from Super
            Mario Bros, ask questions to get why the cat is sick."""
        },
        {"role": "user", "content": last_message.content}
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}


def dog_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {
            "role": "system",
            "content": """ You are a french dog vet, ask questions in french
            to get why the dog is sick."""
        },
        {"role": "user", "content": last_message.content}
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}


graph_builder = StateGraph(State)

graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("cat", cat_agent)
graph_builder.add_node("dog", dog_agent)

graph_builder.add_edge(START, end_key="classifier")
graph_builder.add_edge(start_key="classifier", end_key="router")
graph_builder.add_conditional_edges(
    source="router",
    path=lambda state: state.get("next"),
    path_map={"cat": "cat", "dog": "dog"}
)
graph_builder.add_edge(start_key="cat", end_key=END)
graph_builder.add_edge(start_key="dog", end_key=END)

graph = graph_builder.compile()


def run_chatvet():
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("Message for the vet: ")
        if user_input == "exit":
            print("Bye")
            break

        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}")


if __name__ == "__main__":
    run_chatvet()
