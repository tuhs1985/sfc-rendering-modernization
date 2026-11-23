## 1. Separate the source and package boundary

- [x] 1.1 Move the five launcher inputs into src/launcher and update runtime imports and native build input.
- [x] 1.2 Update production inventory, package roles, staging and ZIP inputs; reject development code under either installed source root.

## 2. Qualify the relocated entry point

- [x] 2.1 Update focused tests, rebuild the native launcher and run relevant regressions.
- [x] 2.2 Exercise isolated packaged preflight before and after a Unicode/space directory move, including the prepared coordinator; preserve the existing checkout.

## 3. Record ownership and results

- [x] 3.1 Update source/release maps, run record, handoff and existing status tracker; validate the change and leave it unstaged.
