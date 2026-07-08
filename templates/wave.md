# Wave {{NN}} — {{goal}}

- 状態: planned <!-- ledger と同期: planned|in_progress|passed|failed_rolled_back|void|skipped -->
- diff 上限: {{max_diff_lines}} 行(G8)
- 依存 Wave: {{depends_on}}

## タスク

| # | タスク | Tier | 担当 worker | 受入基準 |
|---|---|---|---|---|
| 1 | {{task}} | {{tier}} | worker-{{n}} | {{acceptance}} |

<!-- Tier は docs/risk-taxonomy.md 準拠。Tier 3 は実行前に AskUserQuestion 必須 -->

## fileset(worker ごと・相互非重複)

<!-- scope-check.sh に渡す fileset ファイルの内容。1 行 1 エントリ。
     正確なパス、または `dir/` で prefix 指定。#で始まる行はコメント -->

### worker-1
```
{{path_or_prefix}}
```

## 安全網の充足(pre-gate 記録)

- この fileset を保護する特性テスト: {{char_tests}}(safety-net.md と突合済み: {{yes_no}})
- 不足時の JIT 追加: {{jit_added_tests}}

## ゲート実行ログ

<!-- orchestrator が追記。各試行の wave-gate.sh 結果と G7 判定、ログファイルパス -->

| 試行 | 日時 | G1-G6,G8 | G7 | 結果 |
|---|---|---|---|---|
| 1 | {{timestamp}} | {{result}} | {{verdict}} | {{outcome}} |

## worker 完了報告(要約)

<!-- 変更ファイル一覧、実行した確認、遭遇した問題(フェンス候補・findings 候補) -->
