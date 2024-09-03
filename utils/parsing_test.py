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
