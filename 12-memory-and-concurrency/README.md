# 12 Memory and concurrency

Edition `0.2` makes values editable without references: a binding declared `edit` can be rebound, a parameter can be passed in and out, and a value can be consumed. It also runs independent work concurrently, with a result that never depends on the order the tasks ran in. And every program can be compiled to a native executable.

1. [`edit` and `take`](01-edit-and-take/)
2. [`together`](02-together/)
3. [A native executable: `una build`](03-build/)
