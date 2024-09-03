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
