# Refactoring Policy — {{project_name}}

> このファイルはリファクタリング方針の SSOT。**人間が直接編集してよい唯一の `.refactor/` ファイル**。
> 変更したら次の Wave 開始時に orchestrator が再読込する。

## 目的

{{purpose}} <!-- なぜこのリファクタリングをするのか。1-3 文 -->

## 重視観点(優先順)

<!-- /refactor-init の AskUserQuestion で確定。上ほど優先。トレードオフ時はこの順に従う -->
1. {{priority_1}}
2. {{priority_2}}
3. {{priority_3}}

## リスク許容度

{{risk_tolerance}} <!-- 例: 「挙動変化ゼロ必須。性能±10%まで許容」 -->

## 不可侵領域

<!-- 触ってはならないパス・機能。fences.md とは別(こちらは人間の指定、fences は調査での発見) -->
- {{no_touch_1}}

## コード規約(自動収集+人間確定)

<!-- policy-scout の収集結果。出典を [出典: ファイル] で残す -->
- 言語・スタック: {{stack}}
- フォーマッタ / linter: {{formatter}} [出典: {{source}}]
- 命名規約: {{naming}} [出典: {{source}}]
- コミットメッセージ: {{commit_convention}} [出典: git log]

## ディレクトリ規約

{{directory_rules}} <!-- 目標とする配置ルール。現状ではなく到達点 -->

## 完了定義 (Definition of Done)

<!-- チェック可能な形で。例: 「循環依存 0」「全公開 API に docstring」「CLAUDE.md 生成」 -->
- [ ] {{dod_1}}
- [ ] {{dod_2}}

## 要確認事項 (UNKNOWN)

<!-- policy-scout が確定できなかった事項。人間の回答が入り次第、上のセクションへ移す -->
- {{unknown_1}}

---

## 付録: 蒸留された教訓 (append-only)

<!-- Phase 5 で orchestrator が追記。次回実行の入力になる -->
