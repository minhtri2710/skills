#!/bin/zsh
# Prints only whether each secret name is present in this shell; never a value.
for n in TYPESAFE_API_KEY EXA_API_KEY ANTHROPIC_AUTH_TOKEN CLAUDE_CODE_MESSAGING_TOKEN; do
  if [[ -n "${(P)n+x}" ]]; then echo "$n present"; else echo "$n absent"; fi
done
