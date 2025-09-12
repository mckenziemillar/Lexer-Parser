"""Turn a input string into a stream of tokens with lexical analysis.

The `lexer(input_string: str)` function is the entry point. It generates a
stream of tokens from the `input_string`.

Examples:

    >>> from project1.lexer import lexer
    >>> input_string = ":\\n  \\n:"
    >>> for i in lexer(input_string):
    ...     print(i)
    ...
    (COLON,":",1)
    (COLON,":",3)
    (EOF,"",3)
"""

from typing import Iterator

from project5.token import Token, TokenType
from project5.fsm import (
    run_fsm,
    FiniteStateMachine,
    Colon,
    Eof,
    WhiteSpace,
    ColonDash,
    QMark,
    LeftParen,
    RightParen,
    ID,
    String,
    Rules,
    Queries,
    Facts,
    Schemes,
    Period,
    Comma,
    Comment,
)


def _get_new_lines(value: str) -> int:
    return value.count("\n")


def _is_last_token(token: Token, input_string: str) -> bool:
    return token.token_type == "EOF" or (
        token.token_type == "UNDEFINED" and len(token.value) != 0
    )


def _get_token(input_string: str, fsms: list[FiniteStateMachine]) -> Token:
    if not input_string:
        return Token.eof("")

    best_token = Token.undefined("")
    best_length = 0
    for fsm in fsms:
        length, token = run_fsm(fsm, input_string)
        if length > best_length:
            best_token = token
            best_length = length
    if best_length == 0:
        best_token = Token.undefined(input_string[0])
    return best_token


def lexer(input_string: str) -> Iterator[Token]:
    """Produce a stream of tokens from a given input string.

    Pseudo-code:"""
    fsms: list[FiniteStateMachine] = [
        WhiteSpace(),
        Comment(),
        Schemes(),
        Facts(),
        Rules(),
        Queries(),
        ID(),
        String(),
        Colon(),
        ColonDash(),
        Comma(),
        LeftParen(),
        RightParen(),
        Period(),
        QMark(),
        Eof(),
    ]
    hidden: list[TokenType] = ["WHITESPACE", "COMMENT"]
    line_num: int = 1
    token: Token = Token.undefined("")
    while not _is_last_token(token, input_string):
        token = _get_token(input_string, fsms)
        token.line_num = line_num
        line_num += _get_new_lines(token.value)
        # counts how many newlines were in the last token to figure out what line I'm on
        input_string = input_string.removeprefix(token.value)
        # removeprefix removes the part of the input we've already read
        #
        if token.token_type in hidden:
            continue
        yield token

    """The `_get_token` function should return the token from the FSM that reads
    the most characters. In the case of two FSMs reading the same number of
    characters, the one that comes first in the list of FSMs, `fsms`, wins.
    Some care must be given to determining when the _last_ token has been
    generated and how to update the new `line_num` for the next token.

    Args:
        input_string: Input string for token generation.

    Yields:
        token: The current token resulting from the string.

    fsms: list[FiniteStateMachine] = [Colon(), Eof(), WhiteSpace()]
    hidden: list[TokenType] = ["WHITESPACE"]
"""
