# Prompt Leverage

Preserve the user's objective, language, constraints, and tone. Add only what
would change how the task is carried out. If the prompt already works, say so
and keep the edit small.

## Upgrade the prompt

1. Identify the task, the result the user wants, and the constraints that must survive.
2. Use [the framework](prompt-leverage-framework.md) to fill gaps. Add context or tool
   requirements only where they affect correctness. For a non-trivial task, name
   the observable check that decides when the work is done.
3. Return the requested form: the prompt alone, the prompt with a short rationale,
   a reusable fill-in template, or a hook specification.

For a local first pass, [augment_prompt.py](../scripts/augment_prompt.py) wraps the
original prompt, including its internal whitespace and code fences, in an
English scaffold. It uses a general profile in every language unless the caller
selects one: `--task coding`, for example, adds instructions to inspect and
validate code. Choose the profile from the user's intent; do not translate or
classify the text by keywords. Use `--help` for the supported profiles. The
helper needs no network or credentials.

## When the user asks for a hook

Specify a preprocessing step: accept the raw prompt, use the task profile
supplied by the caller (general if omitted), add the missing framework blocks,
and return the prompt for execution. If the caller needs to see what was
injected, also return a diff or short summary.
