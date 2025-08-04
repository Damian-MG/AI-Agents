from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0.9,
    max_tokens=2048,
    timeout=None,
    max_retries=2
)

messages = [
    (
        "system",
        "You are a helpful assistant that speaks like Mario from Mario Bros."
    ),
    ("human", "Hello world! Where can I find Peach?")
]
ai_msg = llm.invoke(messages)
print(ai_msg.content)

