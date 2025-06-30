#!/usr/bin/env sh
export LANGSMITH_TRACING=true
export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
export LANGSMITH_API_KEY="$(pass show smith.langchain.com/apikey)"
export LANGSMITH_PROJECT="default"
git ls-files . | entr -r poetry run python virtual_controller.py
