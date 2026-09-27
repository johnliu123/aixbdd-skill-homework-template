---
name: git-conventional-commit
description: >-
  Drives an evidence-based, decision-tree workflow that analyzes git status/diff,
  infers change intent, decides whether to split changes into multiple atomic
  commits, chooses the Conventional Commits type/scope, detects Breaking Changes,
  drafts and validates a commit message, gets human confirmation on risky or
  uncertain steps, and safely runs `git commit` — then verifies the result. The
  user does not need to know anything about Conventional Commits, semver,
  commitlint, or git internals; this skill supplies the judgment. Use this skill
  whenever the user asks to commit changes, write/generate a commit message,
  review `git diff`/`git status` before committing, split staged changes into
  separate commits, decide a commit type/scope, or mentions "commit",
  "commit message", "git commit", "conventional commits", "commitlint",
  "semantic-release", "breaking change", "幫我 commit", "怎麼 commit",
  "commit message 怎麼寫" — even if they never say "Conventional Commits" by name.
---

# Conventional Commits — AI 自主判斷 Commit Workflow

## 定位與使用時機

這是一個**判斷力 Skill**，不是教學文件。目標：使用者完全不需要懂 Conventional
Commits，AI 就能從「看懂變更」一路做到「commit 完成並回報」。凡是使用者要求
commit、寫 commit message、或在 commit 前想先看一下變更範圍，都套用本 skill。

**不要做的事**：不要向使用者解釋 Conventional Commits 規範本身（除非他們主動問）。
使用者要的是結果，不是課程。

## 核心原則

這七條原則決定每一個判斷，優先序高於任何單一規則細節：

1. **Intent First**：先理解變更的真正意圖與影響，再決定 commit 怎麼寫。
2. **Evidence First**：以 `git diff`、檔案變更、測試結果等實際證據判斷，不靠猜測。
3. **Minimal Assumption**：資訊不足就詢問，不自行猜測。
4. **Project-Aware**：優先遵循專案既有的 Commit Convention，而不是套用教科書規則。
5. **Atomic Commit**：每個 commit 應代表一個清楚、獨立、可還原的變更目的。
6. **Validation Before Commit**：commit 前一定跑格式與語義驗證。
7. **Human Confirmation**：高風險或高度不確定的操作，一定要使用者確認。

## SOP 總覽

複製這個 checklist 追蹤進度（大部分情況每一步只需幾秒，但**不要跳過**）：

```
Progress:
- [ ] Phase 0: 偵測專案既有 commit 慣例
- [ ] Phase 1: 收集證據（git status / diff）
- [ ] Phase 2: 分析意圖（每個變更的 what/why）
- [ ] Phase 3: 判斷是否需要拆成多個 commit
- [ ] Phase 4-7: 為每個 commit 判斷 type / scope / breaking change / body / footer
- [ ] Phase 8: 驗證 commit message
- [ ] Phase 9: Human Confirmation（依風險矩陣判斷是否要停下來問）
- [ ] Phase 10: 精準 staging + 執行 git commit
- [ ] Phase 11: Commit 後驗證與回報
```

---

## Phase 0：偵測專案既有慣例（Project-Aware）

執行：

```bash
python .cursor/skills/git-conventional-commit/scripts/detect_project_convention.py --repo .
```

這一步**必須在產生任何訊息之前**做，因為 Project-Aware 原則的優先序高於「標準」
Conventional Commits 格式。依 `recommendation` 欄位判斷：

| recommendation | 代表意義 | 行動 |
|---|---|---|
| `FOLLOW_DETECTED_CONVENTION` | 有 commitlint/husky 設定,或歷史合規率高 | 直接採用偵測到的 `detected_type_enum`/`detected_scope_enum`（若為空則用預設 11 種 type） |
| `NO_HISTORY_USE_ANGULAR_DEFAULTS` | 全新 repo,沒有 commit 歷史 | 用預設 Angular 11 種 type，不限制 scope |
| `NO_ESTABLISHED_CONVENTION_PROPOSE_DEFAULTS` | 有歷史但雜亂無章 | 用預設 type，可以順口提一句「這個專案還沒有固定的 commit 慣例,我先用標準 Conventional Commits 格式」 |
| `GITMOJI_STYLE_DETECTED_ASK_USER` | 歷史主要是 gitmoji（✨🐛...）風格 | **必須先問使用者**要沿用 gitmoji 還是改用 Conventional Commits，見 `references/examples.md` 範例 4 |
| `MIXED_HISTORY_ASK_USER_OR_USE_MAJORITY` | 歷史風格不一致 | 採用出現次數最多的 type/scope 慣例；若不確定就問 |

## Phase 1：收集證據（Evidence First）

執行：

```bash
python .cursor/skills/git-conventional-commit/scripts/analyze_git_changes.py --repo .
```

檢查回傳的 JSON，依優先序處理：

1. `status.nothing_to_commit == true` → 停止，告知使用者沒有變更可 commit（見
   `references/examples.md` 範例 5）。
2. `special_state.merge_in_progress` / `rebase_in_progress` / `cherry_pick_in_progress`
   為 true → 停止，先完成 merge/rebase/cherry-pick，不要在這個狀態下額外做
   Conventional Commits 判斷（merge commit 有自己的慣例，見 `references/anti-patterns.md` #12）。
3. `status.conflicted` 非空 → 停止，必須先解決 conflict markers。
4. `security.possible_secrets` 或 `security.sensitive_filenames` 非空 → **立即停止**，
   警告使用者可能誤 staged 了憑證/密鑰，不要自動 commit，等待使用者確認已處理。
5. 若 `status.unstaged` 或 `status.untracked` 非空但使用者沒說要不要包含它們 →
   只針對 `status.staged` 分析（若 staged 為空，才詢問使用者要 stage 哪些檔案，
   不要自己猜要 add 全部還是部分）。
6. 讀 `staged_diff`（或 `unstaged_diff` 如果還沒 stage）進行 Phase 2。若
   `*_diff_truncated == true` 且該檔案是判斷的關鍵,針對該檔案單獨跑
   `git diff --staged -- <file>` 取得完整內容。

## Phase 2：Intent Analysis（意圖分析）

對每一個變更的檔案/hunk，回答：
- **What**：程式碼實際做了什麼改變？（用 diff 內容判斷，不是用檔名猜）
- **Why**：為什麼需要這個改變？（commit 訊息裡的 "why" 往往來自：修正的錯誤現象、
  新需求、效能數據、上游依賴變化、程式碼註解、關聯的 issue/branch 名稱）

`analyze_git_changes.py` 回傳的 `issue_refs_from_branch` 可以提供 why 的線索
（例如 branch 叫 `fix/482-login-timeout` → 這次改動大概是為了 issue #482）。

**若從 diff 看不出 why，且沒有其他線索（commit 訊息模板、PR 描述、issue 連結）**：
依 Minimal Assumption 原則，直接問使用者，不要編造一個聽起來合理的原因。

## Phase 3：Atomic Commit 拆分決策樹

對著整組變更問以下問題（依序判斷，命中就停）：

1. **"And" 測試**：能不能只用一句話、不含 "and"/"以及"/"和"，描述整組變更？
   不能 → 拆分。
2. **可還原測試**：如果只 revert 其中一部分,剩下的部分還能正常運作/編譯嗎？
   不能（互相依賴）→ 保持在同一個 commit。能 → 是拆分的訊號（但還要看下一條）。
3. **關注點是否相同**：是否混雜了不同性質的改動（例如：新功能 + 不相關的 bug fix；
   邏輯改動 + 純格式重排；功能改動 + 不相關的依賴升級）？是 → 拆分。
4. **例外（即使檔案很多也不拆）**：
   - 功能程式碼 + 它自己的測試 → 同一個 commit。
   - Migration + 使用該 migration 的 model/程式碼 → 同一個 commit。
   - 設定檔改動 + 讀取該設定的程式碼 → 同一個 commit。
   - 依賴更新造成的 lockfile 變化 + 觸發該更新的改動 → 同一個 commit。
   - 生成檔案（codegen/型別/schema）+ 觸發重新生成的原始碼 → 同一個 commit。
5. **值得留意但不代表一定要拆**：改動跨越多個不相關目錄、或 staged 檔案數 > 10 —
   這是「該檢查一下」的訊號，不是自動判斷的規則；用前面 4 條實際判斷。

若判斷要拆成多個 commit：**先列出完整拆分計畫（每個 commit 要包含哪些檔案/hunk）
呈現給使用者**，這屬於 Phase 9 的「需要確認」情境（多個 commit = 較高不確定性）。
只有單一檔案內混雜了不同 hunk 時，才需要用 `git apply --cached` 做 hunk 級 staging
（見 `references/tooling.md` 第 1 節）；辦不到的情況下，誠實告知使用者這個限制。

## Phase 4：Type 判斷樹

對每一個（拆分後的）commit 依序判斷：

```
這個改動...
├─ 是撤銷之前的 commit？                              → revert
├─ 只改 .github/workflows、.gitlab-ci.yml、Jenkinsfile？ → ci
├─ 只改 build 工具/打包設定/npm scripts（非 CI）？       → build
├─ 只新增/修改測試檔，沒動產品程式碼？                    → test
├─ 只改文件（README、註解、docs/）？                     → docs
├─ 純格式（空白、分號、排版），邏輯完全沒變？               → style
├─ 修正了「不符合預期的行為」（無論是不是順便修的）？        → fix
│    └─ 判斷標準：使用者/呼叫端會觀察到行為從「錯」變「對」
├─ 引入「原本就不存在」的新能力/功能？                     → feat
│    └─ 判斷標準：這是全新引入，不是修復缺失的預期行為
├─ 改變程式碼結構、但外部可觀察行為完全不變、也不是修 bug？ → refactor
├─ 純粹提升效能，行為不變？                              → perf
└─ 不影響 src/test，且以上都不符合的雜務？                → chore
```

**fix vs refactor 是最容易誤判的一組**：問「有沒有一個『不對的行為』被糾正了？」
有 → `fix`，即使是在重構過程中順便修的（見 `references/anti-patterns.md` #5）。

若專案的 `detected_type_enum`（Phase 0）跟預設 11 種不同,以偵測到的清單為準。
完整 type 定義與範例見 `references/spec.md` 第 2 節。

## Phase 5：Scope 判斷樹

```
├─ 專案很小/單一模組，沒有明顯劃分？        → 不加 scope
├─ 變更集中在單一模組/元件？                → scope = 該模組名稱
│    └─ 該名稱是否已出現在 Phase 0 偵測到的 scopes_used 或 detected_scope_enum？
│         是 → 直接沿用；否 → 選最接近的既有詞彙,或詢問使用者是否要新增這個 scope
├─ 變更跨越多個不相關模組（且 Phase 3 判斷不拆）？  → 不加 scope（或考慮回頭重新拆分）
└─ 是 build/ci/chore(release) 等專案層級雜務？      → 通常不加 scope
```

一致性優先於「選最精確的詞」：已經用過的詞彙,永遠優先沿用（見
`references/anti-patterns.md` #7）。Scope 格式：小寫 kebab-case，不含空格。

## Phase 6：Breaking Change 判斷樹

```
這個改動是否要求「使用它的人」修改自己的程式碼/設定才能維持原行為？
├─ 公開 API 簽名/回傳型別/HTTP contract 改變？        → 是
├─ 移除/改名任何 export、CLI 參數、設定鍵值？          → 是
├─ 改變預設值或預設行為？                             → 是
├─ 需要資料遷移才能相容的 DB schema 變更？             → 是
├─ 提高依賴/執行環境的最低版本需求？                   → 是
├─ 純內部實作改動，沒有任何外部呼叫端受影響？           → 否
└─ 不確定外部是否有未知的消費者依賴這個行為？           → 不要猜，詢問使用者
```

若判定為 Breaking Change：
- 描述本身已經足夠說明 → 只用 `!`：`feat(api)!: ...`
- 需要說明遷移方式 → 加 footer：`BREAKING CHANGE: <說明與遷移方式>`（**必須全大寫**、
  **必須在 footer**，不能放在 subject 或裸露的一行,否則 semantic-release 等工具偵測不到）
- 需要解釋 + 想在標題就標明 → 兩者都用
- **一個 commit 只描述一個 breaking change**，多個就拆多個 commit

判定為 Breaking Change 一律進入 Phase 9 的「必須確認」情境，不論證據多明確。
完整規則見 `references/spec.md` 第 7 節；真實陷阱案例見 `references/anti-patterns.md` #2、#3。

## Phase 7：Body / Footer 判斷 + Message 產生

**Body 何時必須有**：
- 修的是不明顯的 bug（why 不會、也不該從 diff 猜出來）
- `feat` 涉及非顯而易見的設計決策
- `refactor` 改變核心結構
- 任何 Breaking Change
**Body 何時可以省略**：改動本身自我解釋、瑣碎（typo、單純版本號 bump）。

Body 寫 **what + why**，不寫 how（how 該從 diff 本身看得出來）。

**Footer 何時要加**：
- Branch 名稱含 issue 編號（Phase 1 的 `issue_refs_from_branch`）→ `Refs #123` 或
  使用者指示的用語（`Closes`/`Fixes`）
- 有 Breaking Change → `BREAKING CHANGE: ...`
- type 是 `revert` → `Refs: <被還原的 commit SHA>`
- 使用者提到多人協作 → `Co-authored-by: Name <email>`

**訊息模板**：

```
<type>[(scope)][!]: <祈使句、小寫開頭、不加句號、≤72字元的簡短描述>

<body：說明 what/why，每行 ≤100 字元（URL 例外）>

<footer：BREAKING CHANGE / Refs / Closes / Co-authored-by 等>
```

Description 撰寫規則（`validate_commit_message.py` 會擋掉違規項）：祈使句
（`add`、`fix`，不是 `added`/`fixes`）、不用 sentence-case/PascalCase/全大寫、
不列檔名、不含 "and"（否則考慮拆 commit）、避免空泛詞（`update`/`fix bug`/`wip`）。
完整規則見 `references/spec.md` 第 4–6 節。

**把訊息寫入暫存檔**（而不是準備一堆 `-m` 參數），下一步驗證與 commit 都用這個檔案。
**寫檔案時不要帶 BOM**（Windows PowerShell 的 `Out-File -Encoding utf8` 會偷加 BOM，
造成 type 比對失敗但外觀正常——用 Cursor 的 `Write` 工具，或見
`references/tooling.md`「Windows BOM 陷阱」的正確寫法）。

## Phase 8：Validation（commit 前一定跑）

```bash
python .cursor/skills/git-conventional-commit/scripts/validate_commit_message.py \
  --file <暫存訊息檔> \
  --types <Phase 0 偵測到的 type 清單，逗號分隔；若無限制則省略此參數用預設值> \
  --scopes <Phase 0 偵測到的 scope 清單；若無限制則省略>
```

- 回傳 `valid: false`（有 error）→ 修正訊息後重跑，**不要帶著已知 error 進入 commit**。
- 有 `warnings` 但無 error → 用自己的判斷力評估是否要改（例如 `type-breaking-mismatch`
  警告通常代表要重新檢視 type 選擇，`subject-contains-'and'` 代表要重新檢視 Phase 3）。
- 這個腳本涵蓋格式與部分語義規則，但**涵蓋不了「type 選錯」這種需要理解 diff 才能
  發現的錯誤**——Phase 4-6 的判斷樹本身才是最後一道防線。

## Phase 9：Human Confirmation Gate

**必須停下來、明確等待使用者確認**（不可逕行 commit）：

| 情境 | 原因 |
|---|---|
| 偵測到 Breaking Change | 影響 semver MAJOR、下游相容性 |
| 需要拆成多個 commit | 拆分方式有多種合理選擇，一旦 commit 難以無痛重組 |
| Phase 0/6 判斷不確定，需要詢問使用者 | Minimal Assumption 原則 |
| `possible_secrets`/`sensitive_filenames` 有內容 | 可能洩漏憑證 |
| 涉及 `git commit --amend`、`rebase`、`push --force`、`reset --hard` | 會改寫或破壞既有歷史 |
| 專案慣例與 Conventional Commits 衝突（gitmoji 等） | 需要使用者決定方向 |
| 使用者要求 `--no-verify` 跳過 commit hook | 繞過既有的品質關卡 |

**可以直接執行、但仍完整呈現訊息與檔案範圍給使用者看**（低風險、證據充分）：
- 單一檔案/單一邏輯改動、無 breaking change、驗證全部通過、Phase 0 判斷為
  `FOLLOW_DETECTED_CONVENTION` 或證據非常清楚的情況。
- 即使不用停下來等待，也一律在回報中列出：最終 commit message、包含的檔案、
  預期的 semver 影響——**不要靜默 commit**。

## Phase 10：Git 執行規則

1. **精準 staging**：`git add <明確路徑>`；絕不 `git add -A`/`git add .` 帶過一整個工作區
   （見 `references/anti-patterns.md` #9）。同檔案內混雜不同關注點時，用
   `git apply --cached <patch>` 做 hunk 級 staging。
2. **Stage 完後先驗證範圍**：`git diff --staged` 確認裡面**只有**這次要 commit 的內容，
   沒有多也沒有少，才進入下一步。
3. **用檔案提交,不用多個 `-m`**：`git commit -F <暫存訊息檔>`（原因見
   `references/tooling.md` 第 1 節「為什麼不用 -m」——避免漏空行、避免跨平台 shell 轉義問題）。
4. **絕不繞過 commit hook**，除非使用者明確要求 `--no-verify` 且已在 Phase 9 確認。
5. **絕不改寫已推送/共享的歷史**（`--amend`、`rebase`、`push --force`）除非使用者明確
   要求，且已確認該分支未被他人依賴。
6. 若 commit-msg hook（commitlint 等）reject 了訊息 → 讀取 hook 的錯誤輸出、對照
   `references/spec.md` 第 8 節規則表修正，重新產生訊息後重試,不要用 `--no-verify` 硬闖。

## Phase 11：Commit 後驗證與回報

```bash
git log -1 --stat
```

檢查：
- Commit 是否真的建立（有新的 SHA）？
- `--stat` 顯示的檔案是否正好是預期的那些（沒有意外多包含或漏掉的檔案）？
- 若專案有 `commit-msg` hook，hook 是否成功執行（沒有錯誤輸出）？

回報格式（給使用者的最終訊息應包含）：
- Commit SHA（短版即可）與完整訊息
- 包含的檔案清單
- 預期的 semver 影響（PATCH/MINOR/MAJOR/無）——依 type + 是否 breaking 判斷
- 若是多 commit 拆分,列出全部 commit 的清單與順序
- 若還有其他未處理的變更（例如 Phase 3 拆分後還有其他組還沒 commit）,主動告知

---

## Exception Handling 快速對照表

| 情境 | 處理方式 |
|---|---|
| 沒有任何變更可 commit | 停止並告知，不編造內容（`references/examples.md` 範例 5） |
| Merge/rebase/cherry-pick 進行中 | 停止，先完成該操作，不套用一般 commit 判斷 |
| 偵測到 conflict markers | 停止，要求先解決衝突 |
| 偵測到可能的密鑰/憑證 | 停止並警告，不自動 stage/commit |
| 全新 repo、無 commit 歷史 | 用 Angular 11 種預設 type，不限制 scope |
| 專案慣例與 Conventional Commits 衝突（gitmoji 等） | 詢問使用者要沿用還是改用（見範例 4） |
| Diff 過大或跨越明顯不相關領域 | 先提出拆分計畫，等確認後才開始 stage |
| commit-msg hook 執行失敗 | 讀錯誤訊息修正後重試，不用 `--no-verify` 繞過 |
| 使用者要求「全部照你判斷,不用問」 | 仍執行 Phase 8 驗證與 Phase 11 回報；Breaking Change/機密/歷史改寫仍需確認，這是安全底線不可被此指令取消 |

## Anti-patterns 快速清單

空泛描述（`update`/`fix bug`/`wip`）、Breaking Change 偽裝成 `chore`、
`BREAKING CHANGE` 放在 subject 而非 footer、description 含 "and"、
bug fix 藏在 `refactor` 裡、scope 深到檔案路徑層級、scope 用詞不一致、
`git commit -m` 多行漏空行、盲目 `git add -A`、lockfile 與觸發它的改動拆開、
revert 不附 SHA。**完整案例與正確寫法見 `references/anti-patterns.md`**。

## Additional Resources

- **關鍵字/術語速查表（type/scope/breaking change/footer…）** → `references/glossary.md`
- **完整規範、type 定義表、commitlint 規則對照、道法理念** → `references/spec.md`
- **工具生態（Git/Commitlint/Husky/Commitizen/Semantic Release）與 workflow 定位** → `references/tooling.md`
- **常見錯誤與 anti-pattern 完整案例** → `references/anti-patterns.md`
- **5 個完整實戰範例（含 AI 內部判斷過程）** → `references/examples.md`
- **腳本**：`scripts/analyze_git_changes.py`、`scripts/detect_project_convention.py`、
  `scripts/validate_commit_message.py`（皆為純 Python 標準庫，不需額外安裝套件）
