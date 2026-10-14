# 7 Contracts and the verifier

A contract states what a function needs and what it promises, and the verifier proves it before the program runs, for every input, with an SMT solver. When a proof fails, it shows the inputs that break it. This chapter writes preconditions, postconditions and refined kinds, and reads a counterexample.

1. [`requires`](01-requires/)
2. [`ensures`](02-ensures/)
3. [Refined kinds with `where`](03-refined/)
4. [Predicates](04-predicates/)
5. [Reading a counterexample](05-counterexample/)
6. [Overflow and division, proven](06-arithmetic/)
7. [Testcase: an account that cannot go negative](07-account/)
