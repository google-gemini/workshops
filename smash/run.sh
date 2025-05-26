#!/usr/bin/env sh
git ls-files . | entr -r poetry run python virtual_controller.py
