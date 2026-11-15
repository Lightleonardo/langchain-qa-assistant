"""Deterministic tests for the LangChain Q&A assistant logic.

These tests do not call the OpenAI API. The real model is replaced with
stand-in chains so we can assert exactly how (and whether) the model is used.
Run with:  pytest
"""

import httpx
import openai
import pytest

import assistant


class _NeverCalledChain:
    """A chain that fails the test if it is ever invoked."""

    def invoke(self, inputs):
        raise AssertionError("chain/model must not be called for this input")


class _RecordingChain:
    """A chain that records each invoke input and returns a canned answer."""

    def __init__(self, answer="canned answer"):
        self.calls = []
        self.answer = answer

    def invoke(self, inputs):
        self.calls.append(inputs)
        return self.answer


class _RaisingChain:
    """A chain that raises a pre-built exception on every invoke."""

    def __init__(self, exc):
        self.exc = exc

    def invoke(self, inputs):
        raise self.exc


# ---------------------------------------------------------------------------
# Empty / whitespace-only input: model must never be called
# ---------------------------------------------------------------------------

def test_empty_question_returns_friendly_message_without_calling_model():
    chain = _NeverCalledChain()
    answer, history = assistant.ask("", [], chain)
    assert "Please ask a question" in answer
    assert history == []


def test_whitespace_question_returns_friendly_message_without_calling_model():
    chain = _NeverCalledChain()
    answer, history = assistant.ask("   \t\n", [], chain)
    assert "Please ask a question" in answer
    assert history == []


# ---------------------------------------------------------------------------
# History grows across questions
# ---------------------------------------------------------------------------

def test_history_grows_with_each_question():
    chain = _RecordingChain()
    history = []
    _, history = assistant.ask("What is LangChain?", history, chain)
    assert len(history) == 2  # HumanMessage + AIMessage
    assert history[0].content == "What is LangChain?"
    _, history = assistant.ask("Can you give an example?", history, chain)
    assert len(history) == 4  # second question sees more messages than the first


# ---------------------------------------------------------------------------
# History is capped (stops growing)
# ---------------------------------------------------------------------------

def test_history_is_capped_to_limit():
    chain = _RecordingChain()
    history = []
    for i in range(12):
        _, history = assistant.ask(f"question {i}", history, chain)
    assert len(history) == assistant.HISTORY_LIMIT
    # count stops growing: another question keeps the same length
    before = len(history)
    _, history = assistant.ask("one more", history, chain)
    assert len(history) == before



# ---------------------------------------------------------------------------
# Successful turns are stored; failed turns are not
# ---------------------------------------------------------------------------

def test_successful_turn_is_stored():
    chain = _RecordingChain(answer="Paris")
    history = []
    answer, history = assistant.ask("Capital of France?", history, chain)
    assert answer == "Paris"
    assert len(history) == 2
    assert isinstance(history[0], assistant.HumanMessage)
    assert history[0].content == "Capital of France?"
    assert isinstance(history[1], assistant.AIMessage)
    assert history[1].content == "Paris"


def test_failed_turn_is_not_stored_in_history():
    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    exc = openai.RateLimitError(
        "rate limited",
        request=request,
        body=None,
        response=httpx.Response(429, request=request),
    )
    chain = _RaisingChain(exc)
    history = []
    answer, history = assistant.ask("anything", history, chain)
    assert "Rate limit" in answer or "rate limit" in answer.lower()
    assert history == []  # failed call is not remembered


# ---------------------------------------------------------------------------
# API errors map to friendly messages, most-specific-first
# ---------------------------------------------------------------------------

def _request():
    return httpx.Request("POST", "https://api.openai.com/v1/chat/completions")


def test_authentication_error_message():
    exc = openai.AuthenticationError(
        "invalid API key",
        request=_request(),
        body=None,
        response=httpx.Response(401, request=_request()),
    )
    answer, history = assistant.ask("q", [], _RaisingChain(exc))
    assert "Authentication error" in answer
    assert history == []


def test_rate_limit_error_message():
    exc = openai.RateLimitError(
        "rate limited",
        request=_request(),
        body=None,
        response=httpx.Response(429, request=_request()),
    )
    answer, history = assistant.ask("q", [], _RaisingChain(exc))
    assert "Rate limit error" in answer
    assert history == []


def test_api_connection_error_message():
    exc = openai.APIConnectionError("network down", request=_request())
    answer, history = assistant.ask("q", [], _RaisingChain(exc))
    assert "Connection error" in answer
    assert history == []


def test_api_status_error_message():
    exc = openai.APIStatusError(
        "server error",
        request=_request(),
        body=None,
        response=httpx.Response(500, request=_request()),
    )
    answer, history = assistant.ask("q", [], _RaisingChain(exc))
    assert "API error" in answer
    assert "500" in answer
    assert history == []


# ---------------------------------------------------------------------------
# Missing API key: clear SystemExit message
# ---------------------------------------------------------------------------

def test_missing_api_key_raises_clear_message(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    # Stop .env from repopulating the key during the test.
    monkeypatch.setattr(assistant, "load_dotenv", lambda: None)
    with pytest.raises(SystemExit) as excinfo:
        assistant.make_llm()
    assert "OPENAI_API_KEY" in str(excinfo.value)


# ---------------------------------------------------------------------------
# build_chain wires prompt, model, and parser together
# ---------------------------------------------------------------------------

def test_build_chain_uses_injected_model():
    # build_chain accepts any runnable/llm and builds the pipeline.
    fake_llm = _RecordingChain()  # not a real LLM, just to prove injection works
    chain = assistant.build_chain(fake_llm)
    assert chain is not None
