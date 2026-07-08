# Refactoring Plan — {{project_name}}

> Phase 3 の成果物。**末尾の承認ブロックが記入されるまで Phase 4 に進んではならない。**
> 承認後の変更(Wave の追加・fileset 変更・Tier 変更)は再承認が必要。

## 計画サマリ

- 目的: {{goal_summary}}(policy.md の重視観点: {{priorities}})
- Wave 数: {{n_waves}} / 想定合計 diff: ~{{total_lines}} 行
- 延期した Tier 3 項目: {{deferred_count}} 件(下記)

## Wave 一覧

| Wave | 目的 | 主タスク (Tier) | fileset 要約 | diff 上限 | 依存 |
|---|---|---|---|---|---|
| 1 | {{goal}} | {{tasks_with_tiers}} | {{fileset_summary}} | {{max_lines}} | — |

<!-- 詳細は waves/wave-NN.md。fileset の非重複性は Wave をまたいでは要求しない
     (同一 Wave 内の worker 間でのみ非重複必須)が、同一ファイルに触る Wave は順序依存を明記 -->

## 非重複性の確認

<!-- 同一 Wave 内の worker 割当が相互に非重複であることの確認結果(機械的に照合) -->
{{overlap_check_result}}

## 延期・除外した項目

| 項目 | 理由 | 行き先 |
|---|---|---|
| {{deferred_item}} | {{reason}} | Tier 3 延期 / fences.md / 対象外 |

## プレモーテム

<!-- wave-planner が記入: この計画が 6 ヶ月後に失敗していたとしたら、その理由トップ 3 -->
1. {{premortem_1}}
2. {{premortem_2}}
3. {{premortem_3}}

---

## 承認ブロック (APPROVAL)

- [ ] 上記計画を承認する
- 承認者: {{approver}}
- 日時: {{approved_at}}
- 承認スコープ: Wave {{approved_waves}}(これ以外の Wave の実行は不可)
- 条件・修正指示: {{conditions}}
