"""Token type for Datalog parsing.

The Datalog parser takes a stream of _tokens_ as input. A `Token` type
maps a string to its syntactic type in the grammar. For example, the string
'Facts' maps to the syntactic type 'FACTS'. The grammar itself defines the
allowed orders of the syntactic types that constitute valid Datalog syntax.
This module defines the syntactic types for Datalog.

Examples:
    >>> from project5.token import Token
    >>> colon = Token.colon(":")
    >>> colon.line_num = 10
    >>> print(colon)
    (COLON,":",10)
    >>> id = Token.id("id")
    >>> id.line_num = 42
    >>> print(id)
    (ID,"id",42)
"""

from typing import Literal, Any

TokenType = Literal[
    "COLON",
    "COLON_DASH",
    "COMMA",
    "COMMENT",
    "UNDEFINED",
    "EOF",
    "FACTS",
    "ID",
    "LEFT_PAREN",
    "PERIOD",
    "QUERIES",
    "Q_MARK",
    "RIGHT_PAREN",
    "RULES",
    "SCHEMES",
    "STRING",
    "WHITESPACE",
]
"""
`TokenType` is an algebraic data type, and more specifically, it is a
"sum type". A sum type is a list of allowed types, or in this case,
allowed string literals that belong to `TokenType`. The mypy tool uses
`TokenType` to statically check that the string indicating the type of
token to create belongs to the `TokenType` sum type. `TokenType`
includes all the allowed syntactic types for the Datalog grammar.

For more on algebraic types in Python see
https://threeofwands.com/algebraic-data-types-in-python/
"""


class Token:
    """Token class for Datalog.

    `Token` defines the allowed syntactic types for Datalog. Here a single
    class is used rather than define a class for each syntactic type. Every
    tokes identifies its type, the string value associated with it, and
    the line where it was found in the input.

    Attributes:
        token_type (TokenType): The syntactic type of this token.
        value (str): The string associated with the token.
        line_num (int): The line number associated with the token -- where it starts in the input.
    """

    __slots__ = ["token_type", "value", "line_num"]

    def __init__(self, token_type: TokenType, value: str, line_num: int = 0) -> None:
        """Initialize a `Token` with its type, value, and line number.

        NOTE: use the static methods to create instances of `Token` rather than call
        `__init__` directly (e.g., `Token.colon(":")`). See _Example_ in module docstring.

        Args:
            token_type: The type of this token.
            value: The value to use for this taken.
            line_num: The line number from the input where the token value begins.
        """
        self.token_type: TokenType = token_type
        self.value: str = value
        self.line_num: int = line_num

    def __repr__(self) -> str:
        return f"Token(token_type={self.token_type!r}, value={self.value!r}, line_num={self.line_num!r})"

    def __str__(self) -> str:
        """Return the string representation of the token

        This function makes it so that `str(token)` works as expected.
        """
        return (
            "(" + self.token_type + ',"' + self.value + '",' + str(self.line_num) + ")"
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Token):
            return (
                self.token_type == other.token_type
                and self.value == other.value
                and self.line_num == other.line_num
            )
        return False

    @staticmethod
    def colon(value: Literal[":"]) -> "Token":
        """Create a COLON token with ':' as its value."""
        return Token("COLON", value)

    @staticmethod
    def colon_dash(value: Literal[":-"]) -> "Token":
        """Create a "COLON_DASH token with ':-' as its value."""
        return Token("COLON_DASH", value)

    @staticmethod
    def comma(value: Literal[","]) -> "Token":
        """Create a COMMA token with ',' as its value."""
        return Token("COMMA", value)

    @staticmethod
    def comment(value: str) -> "Token":
        """Create a COMMENT token with the input value as its value."""
        return Token("COMMENT", value)

    @staticmethod
    def undefined(value: str) -> "Token":
        """Create an UNDEFINED token with the input value as its value."""
        return Token("UNDEFINED", value)

    @staticmethod
    def eof(value: Literal[""]) -> "Token":
        """Create an EOF token."""
        return Token("EOF", value)

    @staticmethod
    def facts(value: Literal["Facts"]) -> "Token":
        """Create a FACTS token with 'Facts' as its value."""
        return Token("FACTS", value)

    @staticmethod
    def id(value: str) -> "Token":
        """Create an ID token with the input value as its value."""
        return Token("ID", value)

    @staticmethod
    def left_paren(value: Literal["("]) -> "Token":
        """Create a LEFT_PAREN token with '(' as its value."""
        return Token("LEFT_PAREN", value)

    @staticmethod
    def period(value: Literal["."]) -> "Token":
        """Create a PERIOD token with '.' as its value."""
        return Token("PERIOD", value)

    @staticmethod
    def queries(value: Literal["Queries"]) -> "Token":
        """Create a QUERIES token with 'Queries' as its value."""
        return Token("QUERIES", value)

    @staticmethod
    def q_mark(value: Literal["?"]) -> "Token":
        """Create a Q_MARK token with '?' as its value."""
        return Token("Q_MARK", value)

    @staticmethod
    def right_paren(value: Literal[")"]) -> "Token":
        """Create a RIGHT_PAREN token with ')' as its value."""
        return Token("RIGHT_PAREN", value)

    @staticmethod
    def rules(value: Literal["Rules"]) -> "Token":
        """Create a RULES token with 'Rules' as its value."""
        return Token("RULES", value)

    @staticmethod
    def schemes(value: Literal["Schemes"]) -> "Token":
        """Create a SCHEMES token with 'Schemes' as its value."""
        return Token("SCHEMES", value)

    @staticmethod
    def string(value: str) -> "Token":
        """Create a STRING token with the input value as its value."""
        return Token("STRING", value)

    @staticmethod
    def whitespace(value: str) -> "Token":
        """Create a WHITESPACE token with the input value as its value.

        Raises:
            AssertionError: if the input `value` has anything other than whitespace.
        """
        for i in value:
            assert i == " " or i == "\t" or i == "\n" or i == "\r"
        return Token("WHITESPACE", value)
