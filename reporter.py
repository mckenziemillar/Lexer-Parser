"""Functions for output matching in pass-off tests."""

from functools import reduce

from project5.datalogprogram import Predicate, Rule
from project5.relation import Relation, RelationTuple


def _graph_to_str(graph: dict[int, list[int]]) -> str:
    """The string representation of a dependency graph."""

    def _rule_id_to_str(id: int) -> str:
        return f"R{id}"

    def _graph_entry_to_str(src: int, dsts: list[int]) -> str:
        src_str: str = _rule_id_to_str(src)
        dsts_str: str = ",".join([_rule_id_to_str(i) for i in dsts])
        return f"{src_str}:{dsts_str}"

    return "\n".join([_graph_entry_to_str(i, j) for i, j in sorted(graph.items())])


def _is_only_strings(predicate: Predicate) -> bool:
    """True iff every parameter in the predicate is of type string."""
    return reduce(
        lambda is_only_string, parameter: is_only_string and parameter.is_string(),
        predicate.parameters,
        True,
    )


def _tuple_to_str(header: list[str], r: RelationTuple) -> str:
    """The string representation of a tuple given its associated header."""
    assert len(header) == len(r)
    entries = [f"{i[0]}={i[1]}" for i in zip(header, r)]
    return ", ".join(entries)


def project_4_report(
    num_rule: int,
    rule_evals: list[tuple[Relation, Rule, Relation]],
    query_evals: list[tuple[Predicate, Relation]],
) -> str:
    """The string representation for the project 4 report

    Assumes (and enforces) at least rule and at least one entry in each list.
    """
    assert num_rule > 0 and len(rule_evals) > 0 and len(query_evals) > 0

    rule_reports = "\n".join([rule_report(i, j, k) for i, j, k in rule_evals])
    query_reports = "\n".join([query_report(i, j) for i, j in query_evals])
    num_passes = len(rule_evals) // num_rule
    passes = f"Schemes populated after {num_passes} passes through the Rules."

    return f"Rule Evaluation\n{rule_reports}\n\n{passes}\n\nQuery Evaluation\n{query_reports}"


def project_5_report(
    dependency_graph: dict[int, list[int]],
    rule_evals: list[tuple[Relation, Rule, Relation]],
    query_evals: list[tuple[Predicate, Relation]],
) -> str:
    """The string representation for the project 5 report

    Assumes (and enforces) at least rule and at least one entry in each list.
    """
    dependency_graph_str = _graph_to_str(dependency_graph)
    rule_reports = "\n".join([rule_report(i, j, k) for i, j, k in rule_evals])
    query_reports = "\n".join([query_report(i, j) for i, j in query_evals])

    return f"Dependency Graph\n{dependency_graph_str}\n\nRule Evaluation\n{rule_reports}\n\nQuery Evaluation\n{query_reports}"


def query_report(query: Predicate, answer: Relation) -> str:
    """The string representation of a query report.

    Here the format is the query followed by yes/no with how
    many tuples match the query. The printing of the tuples
    includes the header information as in the below.

    SK(A,B)? Yes(3)
      A='a', B='b'
      A='a', B='c'
      A='b', B='c'
    """
    tuples: list[RelationTuple] = sorted(answer.set_of_tuples)
    if len(tuples) == 0:
        return f"{query}? No"

    if _is_only_strings(query):
        return f"{query}? Yes({len(tuples)})"

    entries = [_tuple_to_str(answer.header, row) for row in tuples]
    entries_str = "\n  ".join(entries)
    return f"{query}? Yes({len(tuples)})\n  {entries_str}"


def rule_report(before: Relation, rule: Rule, after: Relation) -> str:
    """The string representation of a rule evaluation report

    Here the format is the rule followed by the printing of the tuples
    newly added. These are determined with the `before` and `after`
    relations.

    r(E,F) :- f(E,F).
      e='1', f='2'
      e='4', f='3'
    """
    assert before.header == after.header
    tuples: list[RelationTuple] = sorted(
        after.set_of_tuples.difference(before.set_of_tuples)
    )

    if len(tuples) == 0:
        return f"{rule}."

    entries = [_tuple_to_str(after.header, row) for row in tuples]
    entries_str = "\n  ".join(entries)
    return f"{rule}.\n  {entries_str}"
