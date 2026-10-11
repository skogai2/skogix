#!/usr/bin/env bash
export MAX_THINKING_TOKENS=0 
claude -p --no-session-persistence --model=haiku --tools='' --safe-mode --setting-sources='user' --system-prompt='' "$@"

