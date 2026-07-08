---
phase: intake            # intake|analysis|safety-net|plan|execute|verify|done
status: in_progress      # in_progress|blocked|awaiting_approval|done
branch: refactor/main
source_branch: "{{source_branch}}"
baseline_sha: "{{baseline_sha}}"
current_wave: 0
waves: []
# waves の要素例:
#   - {id: 1, status: passed, start_sha: abc1234, end_sha: def5678, gates: "G1-G8 PASS"}
#   status: planned|in_progress|passed|failed_rolled_back|void|skipped
blocked_reason: null
---

# Ledger — 実行状態の SSOT

> orchestrator のみが書く。frontmatter = 機械可読な現在状態、以下 = append-only イベントログ。
> 両者が矛盾したらログを正とする(refactor-pro プラグイン docs/recovery.md §3)。

## Event Log (append-only)

- {{timestamp}} [init] ledger initialized on branch refactor/main (baseline {{baseline_sha}})
