"""Relation type for interpreting Datalog."""

from tabulate import tabulate
from typing import Any


class IncompatibleOperandError(Exception):
    """Type for relational algebra operand errors."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


RelationTuple = tuple[str, ...]
"""Defines a type for tuples in the relation. Here the tuple can be any number of strings."""


class Relation:
    """Relation class for relational algebra.

    The interface for the class is complete meaning that it defines all the
    needed attributes and relation operations to implement the Datalog interpreter.
    It is expected that additional internal functions are to be added in support
    of the published public interface. No additional attributes should be needed.

    Attributes:
        header (list[str]): The relation header.
        set_of_tuples (set[RelationTuple]): The tuples belonging to the relation.
    """

    __slots__ = ["header", "set_of_tuples"]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Relation):
            return False
        return self.header == other.header and self.set_of_tuples == other.set_of_tuples

    def __init__(self, header: list[str], set_of_tuples: set[RelationTuple]) -> None:
        """Initialize a new relation.

        The `RelationTuple` type is not mutable, so it is not necessary to make
        new copies when initializing a new relation. The list for the header and
        the set of tuples are mutable, so here new instances are created.
        """
        self.header = list(header)
        self.set_of_tuples: set[RelationTuple] = set()
        for i in set_of_tuples:
            self.add_tuple(i)

    def __repr__(self) -> str:
        return f"Relation(header={self.header!r}, set_of_tuples={self.set_of_tuples!r})"

    def __str__(self) -> str:
        """Return the relation as a string.

        A `set` type in Python is not sorted, and indeed, the order of elements
        in the set though defined by the hash of each tuple is non-deterministic
        from machine to machine and run to run. Here the tuples in the set are
        sorted so that the string representation is always deterministic.

        Returns:
            value (str): The relation as a string.
        """
        sorted_tuples = sorted(self.set_of_tuples)
        value: str = tabulate(iter(sorted_tuples), self.header, tablefmt="pretty")
        return value

    def add_tuple(self, r: RelationTuple) -> None:
        """Add a new tuple to the relation.

        Raises:
            error (IncompatibleOperandError): Error if the length of the tuple doesn't
                match the header or if the thing being added isn't a tuple of strings.
        """
        if len(self.header) != len(r):
            raise IncompatibleOperandError(
                f"Error: {r} is not compatible with header {self.header} in Relation.add_tuple"
            )
        if not isinstance(r, tuple) or any(not isinstance(i, str) for i in r):
            raise IncompatibleOperandError(
                f"Error: {r} is not type compatible with Relation.RelationTuple in Relation.add_tuple"
            )
        self.set_of_tuples.add(r)

    def difference(self, right_operand: "Relation") -> "Relation":
        """The difference between this relation and another.

        The left operand is this relation (self) and the right operand
        is provided in the function call. The headers must be the same.

        Returns:
            r (Relation): A new relation that is self - right_operand.
        Raises:
            error (IncompatibleOperandError): Error if the headers are not the same.
        """
        if self.header != right_operand.header:
            raise IncompatibleOperandError(
                f"Error: headers {self.header} and {right_operand.header} are not compatible in Relation.difference"
            )
        r = Relation(
            self.header,
            self.set_of_tuples.difference(right_operand.set_of_tuples),
        )
        return r

    def intersection(self, right_operand: "Relation") -> "Relation":
        """The intersection between this relation and another.

        The left operand is this relation (self) and the right operand
        is provided in the function call. The headers must agree.

        Returns:
            r (Relation): A new relation that is self intersect with right_operand.
        Raises:
            error (IncompatibleOperandError): Error if the headers are not the same.
        """
        if self.header != right_operand.header:
            raise IncompatibleOperandError(
                f"Error: headers {self.header} and {right_operand.header} are not compatible in Relation.difference"
            )
        intersected_tuples = set()
        for tup in self.set_of_tuples:
            if tup in right_operand.set_of_tuples:
                intersected_tuples.add(tup)

        return Relation(self.header, intersected_tuples)

    def join(self, right_operand: "Relation") -> "Relation":
        """The natural join between this relation and another.

        The left operand is this relation (self) and the right operand
        is provided in the function call.

        Returns:
            r (Relation): A new relation that is self natural join with right_operand.
        """
        if self.header == right_operand.header:
            return self.intersection(right_operand)
        common_columns: set[str] = set(self.header).intersection(right_operand.header)
        new_header: list[str] = self.header + [
            col for col in right_operand.header if col not in common_columns
        ]
        result_tuples = set()
        for tup1 in self.set_of_tuples:
            for tup2 in right_operand.set_of_tuples:
                match: bool = True
                for col in common_columns:
                    lefti = self.header.index(col)
                    righti = right_operand.header.index(col)

                    if tup1[lefti] != tup2[righti]:
                        match = False
                if match:
                    new_tuple = list(tup1)
                    for col in right_operand.header:
                        if col not in self.header:
                            righti = right_operand.header.index(col)
                            new_tuple.append(tup2[righti])

                    result_tuples.add(tuple(new_tuple))
        return Relation(new_header, result_tuples)

    def project(self, to: list[str]) -> "Relation":
        if not set(to).issubset(set(self.header)):
            invalid_columns = set(to) - set(self.header)
            raise IncompatibleOperandError(
                f"Error: columns {invalid_columns} not found in header {self.header}"
            )
        indices_to_keep = []
        for col in to:
            indices_to_keep.append(self.header.index(col))

        projected_tuples = set()
        for tup in self.set_of_tuples:
            new_tuple = []
            for index in indices_to_keep:
                new_tuple.append(tup[index])
            projected_tuples.add(tuple(new_tuple))

        # Create and return a new Relation with the projected columns
        return Relation(to, projected_tuples)

    def rename(self, to: list[str]) -> "Relation":
        if len(to) != len(self.header):
            raise IncompatibleOperandError(
                f"Error: length of new header {to} does not match length of current header {self.header}"
            )
        return Relation(to, self.set_of_tuples)

    def select_eq_col(self, src: str, col: str) -> "Relation":
        """The select of this relation where the `src` entry equals the `col` entry.

        The `src` and `col` must be known in the header. The new resulting relation
        should only include tuples where the value for `src` is equal to the value
        for `col`. The header in the new relation is the same as in this relation.

        Returns:
            r (Relation): A new relation with tuples from this relation that agree
                on values for `src` and `col`.
        Raises:
            error (IncompatibleOperandError): Error if `src` or
            `col` are not found in the header.
        """
        if src not in self.header or col not in self.header:
            raise IncompatibleOperandError(
                f"Error: {src} or {col} not found in header {self.header}"
            )

        src_index = self.header.index(src)
        col_index = self.header.index(col)

        selected_tuples = set()
        for tuple in self.set_of_tuples:
            # Check if the values in src and col are equal
            if tuple[src_index] == tuple[col_index]:
                # If they are equal, add the tuple to the selected_tuples set
                selected_tuples.add(tuple)

        return Relation(self.header, selected_tuples)

    def select_eq_lit(self, src: str, lit: str) -> "Relation":
        """The select of this relation where the `src` entry equals `lit`.

        The `src` must be known in the header. The new resulting relation
        should only include tuples where the value for `src` is equal to `lit`.
        The header in the new relation is the same as in this relation.

        Returns:
            r (Relation): A new relation with tuples from this relation where the
                values for `src` is `lit`.
        Raises:
            error (IncompatibleOperandError): Error if `src` is not found in the header.
        """
        if src not in self.header:
            raise IncompatibleOperandError(
                f"Error: {src} not found in header {self.header}"
            )

        src_index = self.header.index(src)

        selected_tuples = set()
        for tuple in self.set_of_tuples:
            # Check if the values in src and col are equal
            if tuple[src_index] == lit:
                # If they are equal, add the tuple to the selected_tuples set
                selected_tuples.add(tuple)

        return Relation(self.header, selected_tuples)

    def union(self, right_operand: "Relation") -> "Relation":
        """The union of this relation and another.

        The left operand is this relation (self) and the right operand
        is provided in the function call. The headers must agree.

        Returns:
            r (Relation): A new relation that is self union with right_operand.
        Raises:
            error (IncompatibleOperandError): Error if the headers are not the same.
        """
        if self.header != right_operand.header:
            raise IncompatibleOperandError(
                f"Error: headers {self.header} and {right_operand.header} are not compatible in Relation.difference"
            )
        unioned_tuples = set()
        for tup in self.set_of_tuples:
            unioned_tuples.add(tup)
        for tup in right_operand.set_of_tuples:
            unioned_tuples.add(tup)

        return Relation(self.header, unioned_tuples)
