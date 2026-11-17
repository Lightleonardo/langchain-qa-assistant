"""Basic LangChain Q&A assistant.

Accepts questions from a user, answers them through a LangChain chain backed by
the OpenAI API, keeps a short conversation history, and handles empty input and
API errors gracefully. The OpenAI API key is read exclusively from the
environment (never hard-coded, printed, or logged).
"""

import os

from dotenv import load_dotenv

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

import openai

# Maximum number of conversation messages to keep in memory.
# 6 messages = three question/answer pairs.
HISTORY_LIMIT = 6

# System message: controls answer length and tells the model to admit
# uncertainty rather than guess.
SYSTEM_PROMPT = (
    "You are a concise, helpful Q&A assistant. Answer the user's question "
    "directly and keep your answers short and readable. If you do not know the "
    "answer, or are not confident, say so plainly rather than guessing. Do not "
    "make up facts. Use the conversation history only when it is relevant to "
    "the current question."
)

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)


def build_chain(llm):
    """Build the prompt | llm | parser pipeline.

    ``llm`` is injected so tests can substitute a stand-in model.
    """
    return PROMPT | llm | StrOutputParser()


def make_llm():
    """Build the chat model, reading secrets only from the environment.

    Supports any OpenAI-compatible endpoint (e.g. OpenRouter at
    https://openrouter.ai/api/v1) via the OPENAI_BASE_URL environment variable.

    The API key is read explicitly and passed straight to the client so the SDK
    does not silently fall back to reading OPENAI_API_KEY itself. Without this,
    an OpenAI key (sk-proj-...) left in the environment would be sent to
    OpenRouter and rejected with 401.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini")

    default_headers = {}
    if base_url and "openrouter.ai" in base_url:
        # OpenRouter recommends these headers; harmless for other endpoints.
        default_headers = {
            "HTTP-Referer": "https://langchain-qa-assistant.example.com",
            "X-OpenRouter-Title": "LangChain Q&A Assistant",
        }

    return ChatOpenAI(
        model=model,
        base_url=base_url or None,
        api_key=api_key,
        default_headers=default_headers or None,
    )

def ask(question, history, chain):
    """Ask one question and return (answer, updated_history).

    ``chain`` is injected so tests can substitute a stand-in chain.

    Empty or whitespace-only input returns a friendly message without calling
    the model. Only successful turns are appended to history, which is then
    trimmed to the last ``HISTORY_LIMIT`` messages. API errors are caught
    most-specific-first and returned as friendly messages without touching
    history.
    """
    # Empty / whitespace-only input: friendly message, no model call.
    if not question or not question.strip():
        return "Please ask a question. I didn't receive anything to answer.", history

    # Call the chain with history and question.
    try:
        answer = chain.invoke({"history": history, "question": question})
    except openai.AuthenticationError as exc:
        return f"Authentication error: {exc}. Check your OpenAI API key.", history
    except openai.RateLimitError as exc:
        return f"Rate limit error: {exc}. You may be out of quota or credit.", history
    except openai.APIConnectionError as exc:
        return f"Connection error: {exc}. Check your network connection.", history
    except openai.APIStatusError as exc:
        return f"API error (status {getattr(exc, 'status_code', 'unknown')}): {exc}.", history

    # Only store successful turns.
    history = history + [HumanMessage(content=question), AIMessage(content=answer)]

    # Keep history short: last N messages only.
    history = history[-HISTORY_LIMIT:]

    return answer, history


def main():
    """Run an interactive question/answer loop."""
    llm = make_llm()
    chain = build_chain(llm)
    history = []
    print("LangChain Q&A Assistant. Type your questions (Ctrl+C to exit).")
    while True:
        try:
            question = input("\nYou: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        answer, history = ask(question, history, chain)
        print(f"\nAssistant: {answer}")


if __name__ == "__main__":
    main()
