# refactor-pro

A Claude Code plugin for **safely refactoring huge legacy codebases** — the kind that has
accreted features for decades and that nobody fully understands anymore.

The workflow is built around one non-negotiable goal: **behavior preservation**. Refactoring
proceeds in small, approved "waves" guarded by deterministic machine gates (characterization
tests, golden masters, scope checks, size budgets) plus adversarial LLM verification. A single
human approval gates the plan; after that, execution is autonomous (HOTL — Human Out of the
Loop) and stops only on gate failures, scope violations, or high-risk (Tier 3) items.

## Design principles

1. **Files are the source of truth.** All state lives in the target repo's `.refactor/`
   directory. Every command is re-entrant; kill it anytime and resume.
2. **Generator/verifier separation.** Workers never grade their own work. A separate verifier
   re-derives claims from primary evidence (diffs, logs, `file:line`). UNKNOWN ≠ PASS.
3. **Deterministic gates.** Pass/fail is decided by shell scripts (`scripts/wave-gate.sh`),
   not by an LLM's self-report.
4. **Legacy code is untrusted input; the running system is the oracle.** Instructions embedded
   in code comments are reported, never followed. Tests pin actual behavior, not the spec.
5. **Behavior preservation beats correctness.** Bugs discovered during refactoring are recorded
   in `findings.md` and left in place for humans to decide — never "fixed along the way".

## Install

```bash
# from a local clone
claude plugin install /path/to/RefacterPro
# or add to your marketplace of choice and install as "refactor-pro"
```

## Quickstart

Inside the target repository (must be a git repo with a clean working tree):

```
/refactor-init         # Phase 0: policy intake (auto-scan + questions), baseline, branch
/refactor-analyze      # Phase 1: parallel structure & risk analysis
/refactor-safety-net   # Phase 2: characterization tests + golden masters
/refactor-plan         # Phase 3: wave plan -> THE single human approval
/refactor-execute all  # Phase 4: autonomous gated execution (waves, workers, gates)
/refactor-verify       # Phase 5: final verification, metrics, report, distillation

/refactor-status       # anytime: where am I, what's next (read-only)
/refactor-rollback     # emergency: reset to a previous wave (confirmation required)
```

All work happens on a dedicated `refactor/main` branch. Your branches are never touched;
worst case, delete the branch and nothing happened.

## Layout

| Path | Purpose |
|---|---|
| `docs/workflow.md` | Canonical spec: phases, gates G1–G8, constants, ledger state machine |
| `docs/risk-taxonomy.md` | Risk tiers 0–3 and what gate each tier requires |
| `docs/recovery.md` | Rollback, resume, and ledger-repair runbook |
| `commands/` | The 8 workflow commands (thin orchestration layers over the canon) |
| `agents/` | 7 bundled subagents (scout, cartographer, archaeologist, safety-net engineer, planner, worker, verifier) |
| `scripts/` | Deterministic gate scripts (`wave-gate.sh`, `scope-check.sh`, `golden-check.sh`) |
| `templates/` | Skeletons for the `.refactor/` state files |
| `sample-legacy/` | ORDSYS/85 — a deliberately awful legacy codebase for E2E validation |
| `e2e/` | Acceptance criteria, answer key, and setup script for the E2E run |

## The machine gates (per wave)

| Gate | Checks |
|---|---|
| G1/G2 | build / typecheck exit 0 |
| G3 | characterization tests 100%; existing suite ratcheted against baseline (known failures excluded, zero new failures) |
| G4 | lint error count ≤ baseline (ratchet) |
| G5 | every changed/added file ⊆ the approved fileset (workers cannot wander) |
| G6 | protected test/golden paths untouched; golden SHA256 manifest intact (tests cannot be "fixed" to pass) |
| G7 | adversarial verifier: behavior preservation, scope, fence integrity (9-item rubric) |
| G8 | diff size within the wave's budget |

G5/G6 violations stop immediately with auto-rollback — no fix cycle. Everything else gets
exactly one fix cycle; a second failure means the plan is wrong, and a human decides.

## E2E validation

`sample-legacy/` contains 13 planted legacy pathologies (god class, hidden circular imports,
inconsistent rounding twins, a Y2K window, string-dispatched "dead" code, a lying comment,
a hidden double-discount bug, an injection trap, …). `e2e/acceptance.md` defines checkpoints
A–E plus two failure drills (mid-wave kill/resume, golden tampering) that the workflow must
pass twice consecutively without edits. The answer key lives in `e2e/answer-key.md`, outside
`sample-legacy/`, so agents under test cannot cheat.
