"""Interpreter for Datalog programs.

Provides an interpreter interface for interpreting Datalog
programs using relational algebra.
"""

from typing import Iterator

from project5.datalogprogram import DatalogProgram, Predicate, Rule
from project5.relation import Relation


class Interpreter:
    """Interpreter class for Datalog.

    Defines the interface, and a place for the implementation, for interpreting
    Datalog programs. The interpreter must be implemented using relational algebra,
    so new attributes must be added to track the named relations in the Datalog
    program during the lifetime of the interpreter.

    Attributes:
        datalog (DatalogProgram): The Datalog program to interpret.
    """

    database: dict[str, Relation]
    __slots__ = ["datalog", "database"]

    def __init__(self, datalog: DatalogProgram) -> None:
        self.datalog = datalog
        self.database: dict[str, Relation] = {}

    def eval_schemes(self) -> None:
        """Evaluate the schemes in the Datalog program.

        Create, and store in the interpreter, a relation for each scheme
        in the Datalog program. The _name_ of the scheme must be stored
        separate from the relation since the `Relation` type has no name
        attribute.
        """
        for scheme in self.datalog.schemes:
            scheme_name = scheme.name
            params: list[str] = []
            for param in scheme.parameters:
                params.append(param.value)
            self.database[scheme_name] = Relation(params, set_of_tuples=set())

    def eval_facts(self) -> None:
        """Evaluate the facts in the Datalog program.

        Create, and store in the appropriate relation belonging to the
        interpreter, a tuple for each fact in the Datalog program.
        """
        for fact in self.datalog.facts:
            fact_name = fact.name
            if fact_name in self.database:
                values = tuple(param.value for param in fact.parameters)
                self.database[fact_name].set_of_tuples.add(values)
            else:
                raise KeyError(f"Relation '{fact_name}' not found in the database.")

    def eval_queries(self) -> Iterator[tuple[Predicate, Relation]]:
        """Yield each query and resulting relation from evaluation."

        For each query in the Datalog program, evaluate the query to get a
        resulting relation that is the answer to the query, and then yield
        the resulting `(query, relation)` tuple.

        Returns:
            out (tuple[Predicate, Relation]): An iterator to a tuple where the
            first element is the predicate for the query and the second element
            is the relation for the answer.
        """
        for query in self.datalog.queries:
            query_name = query.name
            if query_name not in self.database:
                raise KeyError(f"Relation '{query_name}' not found in the database.")

            result = self.database[query_name]

            seen_variables: dict[str, int] = {}
            for i, param in enumerate(query.parameters):
                if param.is_string():
                    # If parameter is a string constant, select matching tuples
                    result = result.select_eq_lit(result.header[i], param.value)
                elif param.value in seen_variables:
                    # Select repeated variable
                    result = result.select_eq_col(
                        result.header[i], result.header[seen_variables[param.value]]
                    )
                else:
                    seen_variables[param.value] = i

            project_columns = []
            seen_vars = set()
            for i, param in enumerate(query.parameters):
                if param.is_id() and param.value not in seen_vars:
                    project_columns.append(result.header[i])
                    seen_vars.add(param.value)

            if project_columns:
                result = result.project(project_columns)

            new_header = []
            seen_vars = set()
            for param in query.parameters:
                if param.is_id() and param.value not in seen_vars:
                    new_header.append(param.value)
                    seen_vars.add(param.value)

            if new_header:
                result = result.rename(new_header)

            yield (query, result)

    def eval_rules(self) -> Iterator[tuple[Relation, Rule, Relation]]:
        """Yield each _before_ relation, rule, and _after_ relation from evaluation.

        For each rule in the Datalog program, yield as a tuple the relation associated
        with the rule before evaluating the rule one time, the rule itself, and then
        the resulting relation after evaluating the rule one time. This process
        should repeat until the associated relations stop changing.
        All the generated facts should be stored in the appropriate relation
        in the interpreter.

        For example, given `rule_a` for relation `A`, `rule_b` for
        relation `B`, and that it takes three evaluations to see no change, then
        `eval_rules` should:

            yield((A_0, rule_a, A_1))
            yield((B_0, rule_b, B_1))
            yield((A_1, rule_a, A_2))
            yield((B_1, rule_b, B_2))
            yield((A_2, rule_a, A_3))
            yield((B_2, rule_b, B_3))

        Here `A_0` is the initial relation for `A`, `A_1` is the relation after evaluating
        `rule_a` on `A_0` etc. The same for `B`. The iteration stops because `A_2 == A_3` and
        `B_2 == B_3`.

        Returns:
            out (Iterator[tuple[Relation, Rule, Relation]]): An iterator to a tuple where the
                first element is the relation before rule evaluation, the second element is
                the rule associated with the relation, and the third element is the relation
                resulting from the rule evaluation.
        """
        changes_made = True
        passes = 0

        while changes_made:
            changes_made = False
            passes += 1

            for rule in self.datalog.rules:
                head_name = rule.head.name
                before_relation = Relation(
                    self.database[head_name].header,
                    self.database[head_name].set_of_tuples.copy(),
                )

                # Evaluate predicates on the right-hand side
                intermediate_results = []
                for predicate in rule.predicates:
                    result = self.evaluate_predicate(predicate)
                    intermediate_results.append(result)

                # Join intermediate results
                joined_result = intermediate_results[0]
                for i in range(1, len(intermediate_results)):
                    joined_result = joined_result.join(intermediate_results[i])

                # Project columns that appear in the head predicate
                head_variables = [param.value for param in rule.head.parameters]
                projected_result = joined_result.project(head_variables)

                # Rename to make union-compatible
                renamed_result = projected_result.rename(
                    self.database[head_name].header
                )

                # Union with the existing relation
                new_tuples = (
                    renamed_result.set_of_tuples
                    - self.database[head_name].set_of_tuples
                )
                self.database[head_name].set_of_tuples |= new_tuples

                if new_tuples:
                    changes_made = True
                yield (
                    before_relation,
                    rule,
                    Relation(self.database[head_name].header, new_tuples),
                )

        print(f"\nSchemes populated after {passes} passes through the Rules.")

    def evaluate_predicate(self, predicate: Predicate) -> Relation:
        relation = self.database[predicate.name]
        result = relation
        seen_variables: dict[str, int] = {}

        for i, param in enumerate(predicate.parameters):
            if param.is_string():
                result = result.select_eq_lit(result.header[i], param.value)
            elif param.value in seen_variables:
                result = result.select_eq_col(
                    result.header[i], result.header[seen_variables[param.value]]
                )
            else:
                seen_variables[param.value] = i

        project_columns = []
        rename_columns = []
        seen_vars = set()
        for i, param in enumerate(predicate.parameters):
            if param.is_id() and param.value not in seen_vars:
                project_columns.append(result.header[i])
                rename_columns.append(param.value)
                seen_vars.add(param.value)

        if project_columns:
            result = result.project(project_columns)
            result = result.rename(rename_columns)

        return result

    def eval_rules_optimized(self) -> Iterator[tuple[Relation, Rule, Relation]]:
        """Yield each _before_ relation, rule, and _after_ relation from optimized evaluation.

        This function is the same as the `eval_rules` function only it groups rules by strongly
        connected components (SCC) in the dependency graph from the rules in the Datalog
        program. So given the first SCC is with `rule_a` for relation `A`, `rule_b` for
        relation `B`, that takes three evaluations to see no change, and the second SCC with
        `rule_c for relation C that takes two evaluations to see no change, then
        `eval_rules_opt` should:

            yield((A_0, rule_a, A_1))
            yield((B_0, rule_b, B_1))
            yield((A_1, rule_a, A_2))
            yield((B_1, rule_b, B_2))
            yield((A_2, rule_a, A_3))
            yield((B_2, rule_b, B_3))
            yield((C_0, rule_c, C_1))
            yield((C_1, rule_c, C_2))

        Here `A_0` is the initial relation for `A`, `A_1` is the relation after evaluating
        `rule_a` on `A_0` etc. The same for `B` and `C`. The iteration on the first SCC stops
        because `A_2 == A_3` and `B_2 == B_3`. After the iteration for the second SCC starts
        and stops after two iterations when `C_1 == C_2`.

        Returns:
            out (Iterator[tuple[Relation, Rule, Relation]]): An iterator to a tuple where the
                first element is the relation before rule evaluation, the second element is the
                rule associated with the relation, and the third element is the relation resulting
                from the rule evaluation.
        """
        dependency_graph = self.get_rule_dependency_graph()
        sccs = self.compute_SCCs(dependency_graph)
        # Step 2: Iterate over each SCC and evaluate the rules within it until stabilization
        for scc in sccs:
            scc_rules: list[Rule] = [self.datalog.rules[i] for i in scc]
            if len(scc) == 1 and not self.rule_depends_on_itself(scc_rules[0]):
                rule = scc_rules[0]
                head_name = rule.head.name
                before_relation = Relation(
                    self.database[head_name].header,
                    self.database[head_name].set_of_tuples.copy(),
                )

                # Evaluate the rule once
                self.evaluate_rule(rule, before_relation, head_name)
                passes = 1
                yield (
                    before_relation,
                    rule,
                    Relation(
                        self.database[head_name].header,
                        self.database[head_name].set_of_tuples,
                    ),
                )
            else:
                changes_made = True
                passes = 0

                while changes_made:
                    passes += 1
                    changes_made = False

                    for rule in scc_rules:
                        new_tuples = set()
                        head_name = rule.head.name
                        before_relation = Relation(
                            self.database[head_name].header,
                            self.database[head_name].set_of_tuples.copy(),
                        )

                        # Evaluate predicates on the right-hand side
                        new_tuples = self.evaluate_rule(
                            rule, before_relation, head_name
                        )

                        if new_tuples:
                            changes_made = True

                        yield (
                            before_relation,
                            rule,
                            Relation(self.database[head_name].header, new_tuples),
                        )

        print(f"SCC evaluated after {passes} passes.")

    def evaluate_rule(
        self, rule: Rule, before_relation: Relation, head_name: str
    ) -> set[tuple[str, ...]]:
        """Evaluate the rule and return the new tuples to be added."""
        # Evaluate predicates on the right-hand side
        intermediate_results = []
        for predicate in rule.predicates:
            result = self.evaluate_predicate(predicate)
            intermediate_results.append(result)

        # Join intermediate results
        joined_result = intermediate_results[0]
        for i in range(1, len(intermediate_results)):
            joined_result = joined_result.join(intermediate_results[i])

        # Project columns that appear in the head predicate
        head_variables = [param.value for param in rule.head.parameters]
        projected_result = joined_result.project(head_variables)

        # Rename to make union-compatible
        renamed_result = projected_result.rename(self.database[head_name].header)

        # Union with the existing relation and return the new tuples
        new_tuples = (
            renamed_result.set_of_tuples - self.database[head_name].set_of_tuples
        )
        self.database[head_name].set_of_tuples |= new_tuples

        return new_tuples

    def rule_depends_on_itself(self, rule: Rule) -> bool:
        """Check if the rule depends on itself."""
        head_name = rule.head.name
        for predicate in rule.predicates:
            if predicate.name == head_name:
                return True
        return False

    def get_rule_dependency_graph(self) -> dict[int, list[int]]:
        """Return the rule dependency graph.

        Computes and returns the graph formed by dependencies between rules.
        The graph is used to compute strongly connected components of rules
        for optimized rule evaluation.

        Rules are zero-indexed so the first rule in the Datalog program is `R0`,
        the second rules is `R1`, etc. A return of `{R0 : [R0, R1], R1 : [R2]}`
        means that `R0` has edges to `R0` and `R1`, and `R1` has an edge to `R2`.

        Returns:
            out: A map with an entry for each rule and the associated rules connected to it.
        """
        dependency_graph = {}
        rule_index: int = 0
        for rule in self.datalog.rules:
            dependencies = []
            for other_index, other_rule in enumerate(self.datalog.rules):
                for predicate in rule.predicates:
                    if (
                        other_rule.head.name == predicate.name
                        and other_index not in dependencies
                    ):
                        dependencies.append(other_index)
            dependency_graph[rule_index] = dependencies
            rule_index += 1
        return dependency_graph

    def dfs(
        self,
        node: int,
        graph: dict[int, list[int]],
        visited: set[int],
        postorder: list[int],
    ) -> None:
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                self.dfs(neighbor, graph, visited, postorder)
        postorder.append(node)

    def get_postorder(self, graph: dict[int, list[int]]) -> list[int]:
        reversed_graph = self.reverse_graph(graph)
        visited: set[int] = set()
        post_order: list[int] = []

        for node in sorted(reversed_graph):
            if node not in visited:
                self.dfs(node, reversed_graph, visited, post_order)
        return post_order

    def reverse_graph(self, graph: dict[int, list[int]]) -> dict[int, list[int]]:
        reversed_graph: dict[int, list[int]] = {}
        for rule in graph:
            dependencies = []
            for other_rule in graph:
                if graph[other_rule].__contains__(rule):
                    dependencies.append(other_rule)
            reversed_graph[rule] = dependencies
        return reversed_graph

    def compute_SCCs(self, graph: dict[int, list[int]]) -> list[list[int]]:
        postorder = self.get_postorder(graph)

        visited: set[int] = set()
        sccs: list[list[int]] = []

        def dfs_scc(node: int, scc: list[int]) -> None:
            if node in visited:
                return
            visited.add(node)
            scc.append(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs_scc(neighbor, scc)

        for node in reversed(postorder):
            if node not in visited:
                scc: list[int] = []
                dfs_scc(node, scc)
                sccs.append(sorted(scc))

        return sccs
