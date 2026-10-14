# 8 Capabilities

A function can do nothing but compute unless its header says otherwise. Everything that reaches outside the program, printing, files, the clock, the network, goes through a capability that the header names and the caller hands over. This chapter uses capabilities, writes a capability and its handlers, and, in edition `0.3`, puts conditions on operations and limits what a boundary may receive.

1. [`uses` and operations](01-uses/)
2. [The host's capabilities and grants](02-host/)
3. [A capability and handlers of your own](03-handlers/)
4. [`with`: installing and rebinding](04-with/)
5. [Conditions on operations (`0.3` preview)](05-conditions/)
6. [Boundaries (`0.3` preview)](06-boundaries/)
