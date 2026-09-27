# 實際使用範例

以下範例展示 AI 在不同情境下「先蒐證、再判斷、資訊不足就問、高風險先確認」的實際思考與行動方式。

## 範例 1：小型 bug 修復——直推還是開 PR？

**使用者**：「登入頁的錯誤訊息文字打錯了，幫我修一下並上線。」

**AI 行為**：
1. Stage 0 盤點：`git log --oneline -10` 發現這個 repo 過去所有 commit 都是直接推到 `main`，沒有 PR 記錄，`git branch -a` 只有 `main`，沒有 CI 設定檔。判斷為極小團隊、慣例是直推 trunk。
2. Stage 1 分類：單一檔案文字修正，屬於 trivial bugfix。
3. Decision Tree #1：trivial + 慣例允許直推 → 本地跑測試（若有）→ 直接在 `main` 上 commit。
4. 因為沒有偵測到 CI／部署管線，AI 主動說明：「這個修正我已經直接 commit 到 `main`；但我沒有找到自動部署設定，要幫你上線的話，需要你告訴我目前怎麼部署（例如手動觸發哪個腳本、或有沒有 CI/CD）。」→ 這是 Minimal Assumption：不假設部署方式。

## 範例 2：三天才能完成的結帳流程改版——需要 Feature Flag

**使用者**：「我們要換一套新的結帳流程，UI 和後端都要改，大概要做好幾天。」

**AI 行為**：
1. Stage 0 盤點：發現專案用 GitHub、有 branch protection 要求 PR + CI 通過才能合併，也有 `unleash-client` 這個依賴（代表已有 Feature Flag 系統）。
2. Stage 1 分類：Feature，使用者可見，預估 3 天以上完成。
3. Decision Tree #2：跨過 1 天，且動到使用者可觸及路徑 → 建議用 Feature Flag。
4. 因為已偵測到 Unleash，AI 直接建議：新增 flag `new_checkout`，預設關閉；提出開發計畫——每天把當天完成的部分（即使 UI 還沒完全接好）合併回 `main`（flag 關閉狀態下不影響現有使用者），而不是等三天後一次性合併一個大 PR。
5. 提醒：兩條路徑（flag on / off）都要各自有測試；並在合併時就先跟使用者確認 flag 的預期存活期限，排入之後移除的待辦。
6. 完成後的「發布」＝逐步調高 `new_checkout` 的 rollout 百分比，不是重新部署；這一步屬於「切換 production 功能可見性」，AI 會先跟使用者確認 rollout 節奏（先自己團隊、再 5%、再 100%），不會自行決定直接開到 100%。

## 範例 3：大型內部重構——用 Branch by Abstraction 取代長期分支

**使用者**：「我們想把整個通知模組換成新的實作，牽涉到十幾個呼叫的地方，這個改動應該要花一兩週。」

**AI 行為**：
1. Stage 1 分類：Refactor（內部），使用者無感，但範圍大、時間長——如果照本能開一條長期 `refactor/notification` 分支，會嚴重違反 Short-Lived Branch 標準。
2. Decision Tree #2 判斷：大範圍內部重構、呼叫端多、使用者無感 → 建議 Branch by Abstraction，而不是長期分支。
3. AI 提出的小步計畫（都在 `main` 上小步提交）：
   - Commit 1：建立 `NotificationSender` 介面，包住現有實作（zero-behavior-change）。
   - Commit 2–N：逐步把呼叫端改成透過介面呼叫（每個呼叫端一個小 commit，各自可獨立合併）。
   - 之後幾天：在介面後面新增新實作類別，先不接上任何呼叫端（跟 dead code 一樣安全）。
   - 完成後：切換 factory/DI 綁定成新實作——這是「唯一一步真正的行為切換」，範圍小、容易 revert。
   - 驗證穩定後：刪除舊實作與抽象層（若不再需要）。
4. AI 說明理由：這樣兩週的重構完全不需要開一條會存活兩週的分支，`main` 全程保持可發布狀態。

## 範例 4：既有 Gitflow 專案，使用者想導入 TBD

**使用者**：「我們現在是 Gitflow，有 develop、release、hotfix 分支，想改成 Trunk-Based Development。」

**AI 行為**：
1. Stage 0 盤點：確認 `develop`、`release/*`、`hotfix/*` 確實規律存在且被使用，CI 目前跑在 `develop` 而不是可能的未來 trunk。
2. **不會**直接刪掉 `develop` 或重寫分支策略。依 Project-Aware 原則，先確認遷移的前提條件是否齊備（見 [principles.md](principles.md) 與 [rules.md](rules.md#exception-handling例外處理)）：測試安全網是否足夠可信、審查速度是否能壓在同一天、CI 是否能快速回饋。
3. 主動詢問：「導入 TBD 前我想先確認幾件事：(1) 目前的自動化測試覆蓋率/可信度如何？(2) PR 審查通常多久會有人看？(3) 是否有多個正式版本需要同時維護（這會影響要不要保留 release branch）？」——這是資訊不足必須問的情境，不猜測直接動手改分支策略。
4. 待使用者回覆後，才提出漸進式遷移計畫（例如：先把 CI 切到以 `main` 為準、逐步縮短 `develop` 存活週期、最終讓 `main` 變成唯一整合中心，`release/*` 依 Exception Handling 規則保留但單向不回合併）。

## 範例 5：高風險操作前的確認

**使用者**：「這個分支太舊了，直接幫我刪掉重來。」

**AI 行為**：
1. 先檢查：`git log <trunk>..<branch>` 是否有尚未合併進 trunk 的獨有 commit。
2. 若有獨有 commit：屬於 Git 操作規則中「刪除含未合併 commit 的分支」，即使使用者已經開口要求，AI 仍會先列出這些 commit 的摘要，確認使用者真的要放棄它們，而不是使用者其實想要的是「reset 並重新開始，但保留某些變更」。
3. 確認後才執行刪除；若使用者只是想讓分支變短命，AI 會同時建議按 [workflow.md](workflow.md#stage-5與-trunk-同步integration-前檢查decision-tree-3) 的處理選項（拆小 PR / 用 flag 先併回部分 / 配對完成），避免同樣的問題再發生一次。
