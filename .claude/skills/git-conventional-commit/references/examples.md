# 實際使用範例（Worked Examples）

這些範例示範完整流程：從「使用者只說了一句話」到「commit 完成並回報」，
包含 AI 內部的判斷過程（用縮排註解標示），不是單純的輸入輸出對照。

---

## 範例 1：單一、清楚的變更（最常見情況）

**使用者輸入**：「幫我 commit 一下」

**AI 執行流程**：
1. 執行 `detect_project_convention.py` → 專案有 `commitlint.config.js`，
   `type-enum` 偵測到標準 11 種，`scope-enum` 未限制。`recommendation: FOLLOW_DETECTED_CONVENTION`。
2. 執行 `analyze_git_changes.py` → staged 只有 `src/api/rateLimiter.ts` 一個檔案，
   diff 顯示新增了一個 `checkRateLimit()` 函式並在 middleware 中呼叫它，無測試檔異動。
3. **Intent Analysis**：這是新增一個「原本不存在的能力」→ 候選 type：`feat`。
   不是修 bug（沒有錯誤行為被糾正的證據）、不是 refactor（新增了可觀察的行為）。
4. **Split 判斷**：只有一個檔案、一個邏輯改動 → 不需拆分。
5. **Scope 判斷**：改動集中在 `api` 模組，歷史上 `api` 是已使用過的 scope → 採用 `api`。
6. **Body 判斷**：這是一個有設計決策的新功能（為什麼要加 rate limit、限制策略是什麼）
   且沒有對應測試——**這件事本身要點出來詢問使用者**，而不是自己猜。

**AI 提問**（因為缺少關鍵資訊，且沒有測試，屬於「主動詢問而非猜測」情境）：
> 我看到 `rateLimiter.ts` 新增了 `checkRateLimit()`，但沒看到對應的測試檔或呼叫端的
> 使用範例。這個 rate limit 是要防範什麼情境（例如：全域 API 限流、還是特定 endpoint）？
> 我會把這個原因寫進 commit body。要不要順便加測試,還是先不用？

**使用者回覆**：「防止 `/login` 被暴力破解，先不加測試,之後補」

**AI 產生訊息**（寫入暫存檔）：
```
feat(api): add rate limiting to prevent login brute-force attempts

Introduce checkRateLimit() and wire it into the /login middleware to
cap repeated attempts from the same client. Test coverage will follow
in a separate commit.
```

7. `validate_commit_message.py` 驗證 → `valid: true`，無 error。
8. **Human Confirmation**：這是低風險、單一檔案、無 breaking change → 顯示訊息與將被
   commit 的檔案清單，執行 `git commit -F <tempfile>`（不需要停下來等待，但仍完整呈現）。
9. **Commit 後驗證**：`git log -1 --stat` 確認 SHA、確認只包含 `rateLimiter.ts`，
   回報：「已建立 commit `a1b2c3d`：`feat(api): add rate limiting...`，預期觸發 MINOR 版本。」

---

## 範例 2：混合關注點 → 判斷需要拆分

**使用者輸入**：「這些改動幫我 commit」

**證據**（`analyze_git_changes.py` 輸出摘要）：
- `src/billing/invoice.ts`：新增 `generatePdf()` 函式（新功能）。
- `src/billing/invoice.test.ts`：對應新測試。
- `src/utils/date.ts`：修掉一個時區轉換的 bug（跟上面兩個檔案無關的既有問題）。
- `.prettierrc`：調整縮排設定，導致 12 個不相關檔案的格式被重新排版。

**判斷（Atomic Commit 決策樹）**：
- `invoice.ts` + `invoice.test.ts`：同一個邏輯改動（功能 + 驗證它的測試）→ **合併成一個 commit**。
- `date.ts` 的 bug fix：與發票 PDF 功能無關 → **獨立 commit**（"and test"：如果要用一句話描述
  會變成「新增發票 PDF 功能 *and* 修時區 bug」，一出現 "and" 就代表要拆）。
- `.prettierrc` + 12 個格式變動檔案：純格式、不影響邏輯 → **獨立 commit**，且不與任何邏輯改動
  混在一起（避免 review 時邏輯改動被格式雜訊淹沒）。

**AI 提出的拆分計畫**（先呈現計畫，再詢問是否照此拆分與 stage 各檔案，因為涉及多個 commit
屬於「需要確認」情境）：

> 我打算拆成 3 個 commit：
> 1. `feat(billing): add PDF invoice generation` — `invoice.ts` + `invoice.test.ts`
> 2. `fix(utils): correct timezone offset in date conversion` — `date.ts`
> 3. `style: reformat with updated prettier indentation rule` — `.prettierrc` + 12 個格式檔
>
> 確認要這樣拆嗎？

使用者確認後，依序：`git add` 對應檔案 → 產生訊息 → 驗證 → `git commit -F` → 驗證下一個。
每個 commit 完成後都先 `git diff --staged` 確認範圍完全符合預期，才真正送出。

---

## 範例 3：Breaking Change

**證據**：`src/config/loader.ts` 中，`loadConfig(path)` 的參數簽名改成
`loadConfig({ path, env })`，且移除了舊的 `loadConfig(path)` 呼叫方式的相容處理。

**判斷**：呼叫端（其他模組、甚至外部使用這個套件的專案）如果沒有更新呼叫方式，
程式會直接壞掉 → **Breaking Change**。這是「補上一個更彈性的能力」而非修 bug → `feat`。

**訊息**：
```
feat(config)!: require object argument for loadConfig

BREAKING CHANGE: loadConfig(path) no longer accepts a bare string.
Call loadConfig({ path, env }) instead. See migration guide in
docs/migrating-to-v3.md.
```

`validate_commit_message.py` 確認 `is_breaking_change: true`、
`breaking_change_footer_present: true`，無 error。

**Human Confirmation（此處必須停下來等待）**：Breaking change 屬於 SKILL.md 定義的
「高風險，一定要確認」情境，即使 diff 證據很清楚：

> 這是一個 Breaking Change（`loadConfig` 呼叫方式不相容）。確認要用
> `feat(config)!: require object argument for loadConfig` 進行 commit 嗎？
> 這會讓下一次 `semantic-release` 觸發 MAJOR 版本升級。

使用者確認後才執行 commit。

---

## 範例 4：專案已有非 Conventional Commits 慣例（Project-Aware 原則的實戰）

**證據**（`detect_project_convention.py` 輸出）：
- `conventional_compliance_rate: 0.05`
- `gitmoji_style_ratio: 0.87`（例如 `✨ Add dark mode toggle`、`🐛 Fix null pointer in parser`)
- `recommendation: GITMOJI_STYLE_DETECTED_ASK_USER`

**判斷**：Project-Aware 原則優先於「教科書式套用 Conventional Commits」。不應該不由分說
把訊息改成 `feat: add dark mode toggle`——這違反了「優先遵循專案既有 Commit Convention」。

**AI 提問**：
> 這個專案目前的 commit 歷史主要是 gitmoji 風格（例如 `✨ Add dark mode toggle`），
> 不是 Conventional Commits。我要：
> (a) 沿用現有的 gitmoji 風格，還是
> (b) 從這次開始改用 Conventional Commits（並跟你確認要不要順便補一份 CONTRIBUTING.md 說明)？

只有在使用者明確選擇 (b) 時，才切換到 Conventional Commits 流程；選 (a) 則改用對應的
gitmoji 對照表產生訊息，且仍然套用 Atomic Commit / Evidence First 等與格式無關的核心原則。

---

## 範例 5：資訊不足，且沒有 diff 可看（Minimal Assumption 原則）

**使用者輸入**：「commit」（沒有任何上下文，且 `git status` 顯示 nothing to commit）

**AI 回應**（不猜測、不創造一個假的 commit）：
> 目前工作區沒有任何已 staged 或未 staged 的變更（`git status` 是乾淨的），
> 沒有東西可以 commit。你是不是還沒存檔，或者變更在其他分支/worktree？

這示範 Exception Handling 中的「無變更」情境：直接停止並回報事實，而不是編造一個
commit message 或詢問一連串不相關的問題。
