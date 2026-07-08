# 障害回復ランブック (Recovery) — 正典

ロールバック・レジューム・台帳修復の手順。[workflow.md](workflow.md) §7 の停止条件と対で読む。

## 1. ロールバック

すべて git ベース。作業は `refactor/main`(= `REFACTOR_BRANCH`)上でのみ行われており、
ユーザーの既存ブランチには一切触れていないため、最悪でもブランチ破棄で影響ゼロに戻せる。

| 状況 | 手順 |
|---|---|
| Wave 失敗(自動) | `git reset --hard <wave start_sha>` → ledger の該当 Wave を `failed_rolled_back` に、status を `blocked` に。イベントログに失敗ゲートと生ログパスを記録 |
| 過去 Wave まで戻す (`/refactor-rollback wave-N`) | `git reset --hard <wave-N の end_sha>` → 後続 Wave の status を `void` に → **plan.md の再承認を要求**(void になった Wave は承認済み計画から外れたため) |
| 全撤退 | `git checkout <元ブランチ>` して `refactor/main` を破棄(`git branch -D`)。`.refactor/` も消える(ブランチ上にのみ存在)ため痕跡なし |

**禁止事項**: `push --force` / ユーザーの既存ブランチへの checkout・reset / `refactor/*` 以外のブランチでの
`git reset --hard` / reflog の削除。

## 2. blocked からの再開 — 人間への選択肢

停止報告には必ず以下を含める: 失敗ゲート名と生ログ(`.refactor/logs/`)、rollback 済みか否か、
そして次の選択肢:

1. **再計画** — `/refactor-plan` を再実行し、失敗 Wave をより小さく分割 or Tier を上げて再承認
2. **フェンス登録** — 問題のコードを fences.md に登録して不可侵化し、Wave の fileset から除外して再実行
3. **Wave スキップ** — 該当 Wave を `skipped` にして次へ(スキップ理由を ledger と report.md に記録)
4. **全撤退** — §1 の手順

選択は人間が行う。orchestrator が勝手に選んではならない。

## 3. ledger 修復

- frontmatter(機械可読ヘッダ)とイベントログ(append-only)が矛盾した場合、**イベントログを正**とし
  frontmatter を再構築する(ログは追記のみで改竄余地が小さいため)。
- 再構築手順: イベントログを時系列に読み、各 Wave の最後のイベントからその Wave の status を導出、
  最後の phase 遷移イベントから phase/status を導出。`git log refactor/main` のコミット列と突合し、
  コミットがあるのにログにない Wave(またはその逆)があれば人間に報告して指示を仰ぐ。
- ledger 自体が消失した場合: `git log` のコミットメッセージ(`refactor(wave-NN): ...`)と
  waves/wave-NN.md から Wave 完了状況を再構築できる。plan.md の承認ブロックが無事なら execute を再開可能。

## 4. 中断(kill・クラッシュ)からのレジューム

全コマンドは再入可能([workflow.md](workflow.md) §7 の表)。原則:

- **Wave 単位で冪等**: worker 実行後・コミット前に中断した場合、未コミット diff は
  `git reset --hard <start_sha>` で破棄し、その Wave を最初からやり直す。
  部分適用された diff を「続きから」やろうとしてはならない(どこまで適用されたか証明できない)。
- 中断が疑われる状態(ledger が in_progress のまま新しいセッションが始まった)を検出したら、
  `/refactor-status` 相当の確認を先に行い、上記の破棄→やり直しを適用してから続行する。

## 5. gates.env / baseline の陳腐化

- 対象リポジトリの依存やツールチェーンが Wave の途中で変わることは想定しない(refactor/main 上では
  リファクタリング以外の変更を行わないため)。もし人間が refactor/main に手動コミットを入れた場合、
  orchestrator は次の Wave 開始時に `git log` で自分のコミット以外を検出し、baseline の再計測
  (`/refactor-init` の手順 5 のみ再実行)を提案する。
- 特性テストが「未改変コードで FAIL する」状態を検出したら、それはコードではなく環境・テストの問題。
  Wave を開始せず停止して報告する。
