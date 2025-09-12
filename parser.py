"""Parser for Datalog programs.

Provides the parser and error interface for when parsing fails for Datalog
programs.
"""

from typing import Iterator, List

from project5.token import Token, TokenType
from project5.datalogprogram import DatalogProgram, Predicate, Rule, Parameter


class UnexpectedTokenException(Exception):
    """Class for parsing errors.

    A parse error is when the actual token does not have the correct type
    according to the state of the parser. In other words, the parser is
    expecting a specific token type but the actual token at that point does
    not match the expected type.

    Attributes:
        expected_type (TokenType): The type that was expected in the parse.
        token (Token): The actual token that was encountered.
    """

    __slots__ = ["expected_type", "token"]

    def __init__(
        self,
        expected_type: TokenType,
        token: Token,
        message: str = "A parse error occurred due to an unexpected token",
    ) -> None:
        super().__init__(message)
        self.expected_type = expected_type
        self.token = token


class TokenStream:
    """Class for managing the token iterator from the lexer.

    A `TokenStream` is a wrapper for the `Iterator[Token]` from the lexer that
    provides core functions for parsing -- `match` and `advance` -- along with an
    additional function for checking if the current token has a type that
    belongs to a set of types -- useful for checking FIRST and FOLLOW sets -- and
    a way to get tho value from the current token.

    Attributes:
        token_iterator (Iterator[Token]): A token iterator.
        token (Token): The current token.
    """

    __slots__ = ["token", "_token_iterator"]

    def __init__(self, token_iterator: Iterator[Token]) -> None:
        self._token_iterator = token_iterator
        self.advance()

    def __repr__(self) -> str:
        return f"TokenStream(token={self.token!r}, _token_iterator={self._token_iterator!r})"

    def advance(self) -> None:
        """Advances the iterator and updates the token.

        The last token in the iterator is stuttered meaning that it is repeated
        on every subsequent call.

        **WARNING**: `advance` side-effects the `token` and `token_iterator`.
        This side-effect means that the previous token is gone and cannot be
        recovered. There is no deep-copy for a `TokenStream`, so it's a _use
        once_ object. That is fine for parsing.
        """
        try:
            self.token = next(self._token_iterator)
        except StopIteration:
            pass

    def match(self, expected_type: TokenType) -> None:
        """Return if token matches expected type.

        `match` returns iff the expected type matches the current taken. If
        ever the token type does not match the expected type, it raises an exception
        indicating a match failure. The exception includes the expected token
        type and the token that did not match.

        Args:
            expected_type (TokenType): The expected token type in the stream for a successful match.

        Raises:
            error (UnexpectedTokenException): Error if the type of the current token does not match.
        """
        if self.token.token_type != expected_type:
            raise UnexpectedTokenException(expected_type, self.token)

    def member_of(self, token_types: set[TokenType]) -> bool:
        """Returns true iff the current token type is in the specified type.

        `member_of` is a way to determine if the type of the current token is
        in a set of token types. It is especially useful for checking membership
        in FIRST and FOLLOW sets when implementing a table driven parser.
        The FIRST and FOLLOW sets are used to determine which alternative to use
        in a grammar rule with alternatives.

        Args:
            token_types: A set of token types.

        Returns:
            out: True iff the current token type is in the set of token types.
        """
        return self.token.token_type in token_types

    def value(self) -> str:
        """Return the value attribute of the current token."""
        return self.token.value


def scheme_list(token_stream: TokenStream) -> List[Predicate]:
    schemes: List[Predicate] = []
    if token_stream.token.token_type == "FACTS":
        return schemes
    schemes.append(scheme(token_stream))
    schemes.extend(scheme_list(token_stream))
    return schemes


def fact_list(token_stream: TokenStream) -> List[Predicate]:
    facts: List[Predicate] = []
    if token_stream.token.token_type == "RULES":
        return facts
    facts.append(fact(token_stream))
    facts.extend(fact_list(token_stream))
    return facts


def rule_list(token_stream: TokenStream) -> List[Rule]:
    rules: List[Rule] = []
    if token_stream.token.token_type == "QUERIES":
        return rules
    rules.append(rule(token_stream))
    rules.extend(rule_list(token_stream))
    return rules


def query_list(token_stream: TokenStream) -> List[Predicate]:
    queries: List[Predicate] = []
    if token_stream.token.token_type == "EOF":  # Or some other stopping condition
        return queries
    queries.append(query(token_stream))
    queries.extend(query_list(token_stream))
    return queries


def scheme(token_stream: TokenStream) -> Predicate:
    name = token_stream.value()
    token_stream.match("ID")
    token_stream.advance()
    token_stream.match("LEFT_PAREN")
    token_stream.advance()
    ids: List[Parameter] = []
    token_stream.match("ID")
    ids.append(Parameter(token_stream.value(), "ID"))
    token_stream.advance()
    ids.extend(id_list(token_stream))
    token_stream.match("RIGHT_PAREN")
    token_stream.advance()
    return Predicate(name, ids)


def fact(token_stream: TokenStream) -> Predicate:
    name = token_stream.value()
    token_stream.match("ID")
    token_stream.advance()
    token_stream.match("LEFT_PAREN")
    token_stream.advance()
    ids: List[Parameter] = []
    token_stream.match("STRING")
    string_value = token_stream.value()
    param = Parameter(string_value, "STRING")
    ids.append(param)
    token_stream.advance()
    ids.extend(string_list(token_stream))
    token_stream.match("RIGHT_PAREN")
    token_stream.advance()
    token_stream.match("PERIOD")
    token_stream.advance()
    return Predicate(name, ids)
    # I think this loops when it should move onto rules


def rule(token_stream: TokenStream) -> Rule:
    head: Predicate = head_predicate(token_stream)
    token_stream.match("COLON_DASH")
    token_stream.advance()
    preds: List[Predicate] = []
    preds.append(predicate(token_stream))
    token_stream.advance()
    preds.extend(predicate_list(token_stream))
    token_stream.match("PERIOD")
    token_stream.advance()
    return Rule(head, preds)


def query(token_stream: TokenStream) -> Predicate:
    pred = predicate(token_stream)
    token_stream.advance()
    token_stream.match("Q_MARK")
    token_stream.advance()
    return pred


def head_predicate(token_stream: TokenStream) -> Predicate:
    ids: List[Parameter] = []
    token_stream.match("ID")
    name = token_stream.value()
    token_stream.advance()
    token_stream.match("LEFT_PAREN")
    token_stream.advance()
    token_stream.match("ID")
    ids.append(Parameter(token_stream.value(), "ID"))
    token_stream.advance()
    ids.extend(id_list(token_stream))
    token_stream.match("RIGHT_PAREN")
    token_stream.advance()
    return Predicate(name, ids)


def predicate(token_stream: TokenStream) -> Predicate:
    ids: List[Parameter] = []
    token_stream.match("ID")
    name = token_stream.value()
    token_stream.advance()
    token_stream.match("LEFT_PAREN")
    token_stream.advance()
    ids.append(parameter(token_stream))
    token_stream.advance()
    ids.extend(parameter_list(token_stream))
    token_stream.match("RIGHT_PAREN")
    return Predicate(name, ids)


def predicate_list(token_stream: TokenStream) -> List[Predicate]:
    preds: List[Predicate] = []
    if token_stream.token.token_type == "PERIOD":
        return preds
    token_stream.match("COMMA")
    token_stream.advance()
    preds.append(predicate(token_stream))
    token_stream.advance()
    preds.extend(predicate_list(token_stream))
    return preds


def parameter_list(token_stream: TokenStream) -> List[Parameter]:
    params: List[Parameter] = []
    if token_stream.token.token_type == "RIGHT_PAREN":
        return params
    token_stream.match("COMMA")
    token_stream.advance()
    params.append(parameter(token_stream))
    token_stream.advance()
    params.extend(parameter_list(token_stream))
    return params


def parameter(token_stream: TokenStream) -> Parameter:
    if token_stream.member_of({"ID"}):
        return Parameter(token_stream.value(), "ID")
    elif token_stream.member_of({"STRING"}):
        return Parameter(token_stream.value(), "STRING")
    else:
        raise UnexpectedTokenException(expected_type="ID", token=token_stream.token)


def id_list(token_stream: TokenStream) -> List[Parameter]:
    ids: List[Parameter] = []
    if token_stream.token.token_type == "RIGHT_PAREN":
        return ids
    token_stream.match("COMMA")
    token_stream.advance()
    token_stream.match("ID")
    ids.append(Parameter(token_stream.value(), "ID"))
    token_stream.advance()
    ids.extend(id_list(token_stream))
    return ids


def string_list(token_stream: TokenStream) -> List[Parameter]:
    params: List[Parameter] = []
    if token_stream.token.token_type == "RIGHT_PAREN":
        return []
    token_stream.match("COMMA")
    token_stream.advance()
    token_stream.match("STRING")
    param_value = token_stream.value()
    param = Parameter(param_value, "STRING")
    params.append(param)
    token_stream.advance()
    params.extend(string_list(token_stream))
    return params


def datalog_program(token: TokenStream) -> DatalogProgram:
    """Top-level grammar rule for a Datalog program.

    The function directly matches its associated grammar rule by matching
    on keywords and collecting returns from other non-terminal rules to
    build an instance of a `DatalogProgram`.

    Pseudo-code:
    ```
    token.match('SCHEMES')
    token.advance()
    token.match('COLON')
    token.advance()

    schemes: list[Predicate] = [scheme(token)]
    schemes.extend(scheme_list(token))

    # Other matches, advances, and rules for the rest of a Datalog Program

    return DatalogProgram(schemes, facts, rules, queries)
    ```

    Args:
        token (TokenStream]): A token stream.

    Returns:
        program (DatalogProgram): The Datalog program from the parse.
    """
    # Parse Schemes
    token.match("SCHEMES")
    token.advance()
    token.match("COLON")
    token.advance()

    schemes: list[Predicate] = [scheme(token)]
    schemes.extend(scheme_list(token))

    # Parse Facts
    token.match("FACTS")
    token.advance()
    token.match("COLON")
    token.advance()
    facts: list[Predicate] = []
    facts.extend(fact_list(token))

    # Parse Rules
    token.match("RULES")
    token.advance()
    token.match("COLON")
    token.advance()
    rules: list[Rule] = []
    rules.extend(rule_list(token))

    # Parse Queries
    token.match("QUERIES")
    token.advance()
    token.match("COLON")
    token.advance()
    queries: list[Predicate] = [query(token)]
    queries.extend(query_list(token))

    token.match("EOF")
    return DatalogProgram(schemes, facts, rules, queries)


def parse(token_iterator: Iterator[Token]) -> DatalogProgram:
    """Parse a datalog program.

    A convenience function that avoids having to create an instance of the
    `TokenStream`

    Args:
        token_iterator (Iterator[Token]): A token iterator.

    Returns:

        program (DatalogProgram): The Datalog program from the parse.
    """
    token: TokenStream = TokenStream(token_iterator)
    return datalog_program(token)
