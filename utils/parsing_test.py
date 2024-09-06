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

import unittest
from textwrap import dedent

from . import parsing


class TestExtractFencedCode(unittest.TestCase):

    def test_extract_single_python_code(self):
        code = dedent(
            """
        ```python
        def hello_world():
            print("Hello, world!")
        ```
        """
        )
        expected = ['def hello_world():\n    print("Hello, world!")']
        result = parsing.extract_fenced_code(code)
        self.assertEqual(result, expected)

    def test_extract_multiple_languages(self):
        code = dedent(
            """
        ```python
        def foo():
            return 'foo'
        ```
        Some text in between.
        ```html
        <div>Bar</div>
        ```
        """
        )
        expected = ["def foo():\n    return 'foo'", "<div>Bar</div>"]
        result = parsing.extract_fenced_code(code)
        self.assertEqual(result, expected)

    def test_extract_no_language_specified(self):
        code = dedent(
            """
        ```
        Just some generic code block without language specified.
        ```
        """
        )
        expected = ["Just some generic code block without language specified."]
        result = parsing.extract_fenced_code(code)
        self.assertEqual(result, expected)

    def test_empty_code_block(self):
        code = "```\n```"
        expected = [""]
        result = parsing.extract_fenced_code(code)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
