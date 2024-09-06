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

from pyparsing import LineEnd, Literal, SkipTo, restOfLine


def extract_fenced_code(code: str) -> str:
    # Define the parser elements
    triple_backtick = Literal("```")
    anything_until_newline = restOfLine()
    newline = LineEnd()

    # The grammar captures everything between triple backticks. It uses
    # restOfLine after the opening triple backticks to consume the
    # optional language specifier
    grammar = (
        triple_backtick
        + anything_until_newline.suppress()
        + newline.suppress()
        + SkipTo(triple_backtick)("code")
        + triple_backtick
    )

    # Parse the string and return the captured code
    parsed_results = grammar.searchString(code)
    return [result.code.strip() for result in parsed_results]
