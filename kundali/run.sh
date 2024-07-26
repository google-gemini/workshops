#!/usr/bin/env sh
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


function main() {
    python3 -m venv /tmp/venv
    . /tmp/venv/bin/activate
    python -m pip install pip-tools
    pip-compile --generate-hashes requirements.in
    pip install -r requirements.txt
    git ls-files | entr -r "$@"
}

# Fail early.
set -e
set -o pipefail

# Start!
main "$@"
