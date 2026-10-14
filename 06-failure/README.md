# 6 Failure

In Una, failure is a value of a kind you declare. A function that may fail says so with `fails`, and every call that may fail is followed by a clause that says what to do. There are no exceptions and no panics: nothing fails without the code saying so.

1. [`fails` and `fail`](01-fails/)
2. [`if error` and `if none`](02-handling/)
3. [`attempt` and `Result`](03-attempt/)
4. [`checked`, and the escape budget](04-checked/)
