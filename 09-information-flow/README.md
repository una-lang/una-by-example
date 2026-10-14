# 9 Information flow

A label says how sensitive a value is, and the checker follows labels through every computation and every branch. Data reaches a place only if that place accepts its label, and the console accepts only `public` data. A label is lowered only through a declared policy, in a trusted module. This chapter labels data, sees what a branch on a secret does, and writes policies.

1. [Labels and levels](01-labels/)
2. [Branches raise the program counter](02-branches/)
3. [Categories](03-categories/)
4. [Policies and `via`](04-policies/)
5. [Trusted modules](05-trusted/)
6. [Testcase: a contact book that never prints a phone number](06-contact-book/)
