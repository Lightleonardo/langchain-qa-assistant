# Prompt and Chain

This document explains how the Q&A assistant turns a user question into an answer,
piece by piece, using LangChain.

## The pipeline

```python
chain = PROMPT | llm | StrOutputParser()
```

The `|` operator builds a LangChain **Runnable** pipeline: the output of each step is
fed as the input to the next.

| Part | What it does |
|------|--------------|
| `PROMPT` | A `ChatPromptTemplate` that turns `{"history": [...], "question": "..."}` into a list of chat messages (system + history + human). It is the **input adapter**. |
| `llm` | The chat model (e.g. `ChatOpenAI`). It receives the formatted messages and returns an `AIMessage`. It is the **reasoning engine**. |
| `StrOutputParser()` | Extracts the plain text string from the model's `AIMessage`. It is the **output adapter**, so `chain.invoke(...)` returns a `str`, not a message object. |

## The prompt template

```python
PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])
```

- `("system", SYSTEM_PROMPT)` — fixed instructions given once at the start of every call. Tells the model to be concise, answer directly, and **admit uncertainty rather than guess**.
- `MessagesPlaceholder(variable_name="history")` — inserts the prior conversation (a list of `HumanMessage` / `AIMessage` objects) at this position. Each turn appends to `history`, so the model sees recent context. See "History handling" below.
- `("human", "{question}")` — the current user question, substituted at call time.

## Why the system message is written this way

The system message is the main design lever for answer quality. Ours is written to:

1. **Control answer length** — "keep your answers short and readable." Without this the model tends to ramble.
2. **Reduce hallucination** — "If you do not know the answer, or are not confident, say so plainly rather than guessing. Do not make up facts."
3. **Scope history use** — "Use the conversation history only when it is relevant to the current question," so older turns don't force irrelevant context into every answer.

This is the part we explain and defend because it shapes every response.

## History handling

`ask()` keeps `history` as a plain list of `HumanMessage` and `AIMessage` objects and passes it as `{"history": history, "question": question}`. After each successful turn it appends the question and answer, then trims to the last `HISTORY_LIMIT` (6 = three Q/A pairs) so the prompt stays small and the assistant doesn't remember forever. Failed turns are not appended.

## Limitations of this design

- History lives in RAM only and vanishes when the process exits.
- Trimming means older context is forgotten.
- The system message is guidance, not a security boundary (see `docs/errors_risks_limitations.md`).
