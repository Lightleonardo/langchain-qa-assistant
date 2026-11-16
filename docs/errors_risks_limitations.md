# Errors, Risks, and Limitations

## Errors handled

`ask()` catches OpenAI API errors most-specific-first and returns a friendly message instead of crashing. History is **not** updated on a failed call.

| Error | When it happens | Friendly response |
|-------|-----------------|-------------------|
| `openai.AuthenticationError` | Bad or missing API key | Check your OpenAI API key |
| `openai.RateLimitError` | Rate limit or no credit | Rate limit / out of quota |
| `openai.APIConnectionError` | Network down | Check your network connection |
| `openai.APIStatusError` | Everything else (includes `status_code`) | API error with status code |

Empty or whitespace-only input returns a friendly message **without calling the model** at all.

## Errors NOT handled (and why)

- **Timeouts** — a hanging request can block indefinitely; no call timeout is configured.
- **Over-long input** — very long questions are sent as-is and may exceed the model's context limit or cost more than intended; no input-length guard exists.
- **Model retired/deprecated** — `ChatOpenAI` will surface an API error; no automatic fallback to another model.
- **Partial/streaming failures** — not used; the chain waits for a complete response.
- **Invalid API key format** — surfaced as `AuthenticationError` only after a call is attempted.

## Wrong answers

Language models can state falsehoods confidently (hallucination). Our system prompt reduces this by instructing the model to admit uncertainty, but it does **not** remove it. Treat answers as unverified, especially for factual, medical, legal, or recent claims.

## Prompt injection

A user can type "ignore your instructions" or similar to try to override the system prompt. The system prompt is **guidance, not a security boundary** — it should not be relied on to enforce safety or access control.

## Privacy

Every question is sent to a third party (OpenAI, or OpenRouter if `OPENAI_BASE_URL` is set). Do not enter sensitive, personal, or confidential information.

## Cost

Each call costs money and nothing limits usage. There is no per-user quota, no daily cap, and no cost ceiling in this version.

## Memory

History lives in RAM and disappears on exit. Trimming to the last 6 messages means the assistant forgets older context beyond that window.

## Suggested improvements

- Persistent storage (database/file) so history survives restarts.
- LangGraph persistence — the supported successor to the deprecated in-memory history approach.
- Per-user quotas and cost limits.
- Input-length validation and request timeouts.
- Answer citations / source verification to reduce wrong-answer risk.
