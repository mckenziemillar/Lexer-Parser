Features
Dependency Graph Construction: Generates a directed graph representing dependencies between Datalog rules using a dict[int, list[int]] structure.

SCC Optimization: Groups rules into Strongly Connected Components to determine the most efficient evaluation order.

Fix-point Evaluation: Iteratively evaluates non-trivial SCCs until no more facts can be derived.

Trivial SCC Handling: Identifies and handles "trivial" SCCs (single rules without self-loops) by evaluating them exactly once.

Modular Architecture: Leverages a custom Lexer, Parser, and Relational Algebra-based Interpreter.
