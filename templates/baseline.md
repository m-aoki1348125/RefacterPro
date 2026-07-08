# Baseline — {{project_name}}

> Phase 0 で計測した「現状」の記録。ラチェットゲート(G3/G4)の比較基準。
> このファイルは baseline 再計測(refactor-pro プラグイン docs/recovery.md §5)以外で書き換えない。

- 計測日時: {{timestamp}}
- baseline SHA: `{{baseline_sha}}`(ブランチ `refactor/main` の起点)
- 元ブランチ: `{{source_branch}}`

## 検出スタック

| 項目 | 値 | 根拠 |
|---|---|---|
| 言語 / ランタイム | {{language}} | {{evidence}} |
| ビルド | {{build_tool}} | {{evidence}} |
| テスト | {{test_framework}} | {{evidence}} |
| lint / typecheck | {{lint_tool}} | {{evidence}} |

## 解決済みコマンド(gates.env に反映済み)

| ゲート | コマンド |
|---|---|
| G1 build | `{{build_cmd}}` |
| G2 typecheck | `{{typecheck_cmd}}` |
| G3a char test | (Phase 2 で設定) |
| G3b gate test | `{{gate_test_cmd}}` |
| G4 lint count | `{{lint_count_cmd}}` |

## ベースライン現況

- build: {{build_status}}
- テスト: {{tests_passed}}/{{tests_total}} PASS
- lint エラー数: {{lint_errors}}(→ gates.env の `LINT_MAX_ERRORS`)

## 既知失敗テスト(ゲート対象外)

<!-- ベースライン時点で失敗しているテスト。GATE_TEST_CMD はこれらを除外して構成されている。
     ここに載っていない失敗が出たら、それは新規の退行 = G3 FAIL -->

| テスト | 失敗内容(要約) | 除外方法 |
|---|---|---|
| {{failing_test}} | {{reason}} | {{exclusion}} |
