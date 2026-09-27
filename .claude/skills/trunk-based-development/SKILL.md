---
name: trunk-based-development
description: >-
  以 Trunk-Based Development (TBD) 為核心的 Git / 開發流程判斷與執行 Skill。啟動後 AI 會自動盤點專案目前的
  Git 與分支狀態、分析當前任務與變更範圍，依據 TBD 的道(理念)法(規範)術(SOP/Decision Tree)器(工具)四層知識，
  判斷應採用的 Branch/Merge 策略、Short-Lived Branch 是否超時、Commit/Integration/Review/Test 的時機、
  是否需要 Feature Flag 或 Branch by Abstraction 解耦，並能偵測違反 TBD 的情況並提出具體改善方式。
  資訊不足時會主動詢問而非猜測，且能在使用者同意下直接執行 Git 操作與開發流程，高風險操作（force-push、
  刪除有未合併 commit 的分支、直接推送到受保護的 trunk、刪除/切換 production feature flag、切 release
  branch 等）一律先確認。使用情境：使用者要求以 Trunk-Based Development 開發、要決定分支/合併策略、
  要規劃 feature flag 上線、要檢查目前流程是否符合 TBD、要從 Gitflow 等模式導入/遷移到 TBD，或要 AI
  接手完成「需求→Branch→開發→Commit→Integration→Review→Test→Merge→Release」全流程時。常見觸發詞：
  「Trunk-Based Development」「TBD」「trunk」「短命分支」「short-lived branch」「feature flag」
  「Branch by Abstraction」「release branch」「分支策略」「merge 策略」「Gitflow 遷移」「這樣做對嗎」等，
  即使使用者沒有直接說出「Trunk-Based Development」這個名稱也適用。
disable-model-invocation: true
---

# Trunk-Based Development — AI Project Ownership Skill

## 定位

這不是一份 TBD 教學文件，而是讓 AI 具備**判斷力**、能在 Trunk-Based Development 的框架下**主動 Own 專案 Git / 開發流程**的 Workflow Skill。使用者不需要懂 TBD；AI 要懂，並且要用證據（Git 現況、CI 結果、變更內容）做判斷，而不是套公式。

**核心工作方式**：Evidence First（先盤點現況）→ Project-Aware（尊重專案既有慣例）→ 依 Decision Tree 判斷 → 資訊不足就問 → 低風險自動做、高風險先確認。

## 核心原則（道，細節見 [principles.md](references/principles.md)）

| 原則 | 一句話 |
|---|---|
| Trunk First | 以單一 trunk（通常是 `main`/`master`）為整合中心，長期分支是例外不是常態 |
| Short-Lived Branch | 分支存活時間以「小時」計，硬上限 1–2 天，超過就是風險訊號 |
| Small Changes | 小批次、高頻率整合，diff 越小，風險與 review 成本越低 |
| Continuous Integration | 每天至少整合回 trunk 一次；trunk 永遠必須是可建置/可測試的 |
| Automation First | 用自動化測試與 CI 取代人工把關，讓「小步快跑」變得安全 |
| Feature Decoupling | 用 Feature Flag / Branch by Abstraction 把「合併」與「上線」分開 |
| Project-Aware | 先看專案現有慣例與限制，再決定要不要調整，不盲目套規則 |
| Evidence First | 用 Git log、CI 結果、實際 diff 做判斷依據，不是憑印象 |
| Minimal Assumption | 關鍵資訊不足（release 節奏、部署環境、是否有 flag 系統…）就問，不猜 |

## Stage 0：啟動時必做——盤點專案現況（Evidence First）

在做任何 branch/merge/flag 判斷之前，先用只讀指令蒐證，不用問使用者就能做：

```bash
git status
git remote -v
git branch -a --sort=-committerdate          # 有哪些分支、誰最舊
git log --oneline --graph --decorate --all -30
git log <trunk>..HEAD --oneline               # 目前分支領先 trunk 多少
git log --merges -10 <trunk>                  # 過去整合模式：常態直推還是走 PR
```

同時確認：
- **Trunk 名稱**：`main` 或 `master`（用 `git symbolic-ref refs/remotes/origin/HEAD` 或 remote 預設分支確認，不要假設）。
- **是否已有 CI**：`.github/workflows/`、`.gitlab-ci.yml`、`Jenkinsfile`、`azure-pipelines.yml` 等是否存在。
- **是否已有長期分支**：`develop`、`release/*`、`hotfix/*` 是否存在 → 代表專案目前可能是 Gitflow 風格，屬於 Project-Aware 判斷輸入，不代表要立刻改。
- **是否已有 Feature Flag 機制**：搜尋 `.env`、config、依賴清單（`package.json`/`requirements.txt`/`go.mod` 等）中是否有 LaunchDarkly / Unleash / Flagsmith / 自建 flag 模組等關鍵字。
- **是否已有 commit 慣例**：是否符合 Conventional Commits；若專案已安裝 `git-conventional-commit` 這類 skill，Commit 訊息一律照該規則產生。

蒐證完成後，形成一份內部「現況摘要」（trunk 名稱、活躍分支數與各分支存活時間、CI 是否存在、flag 基礎設施是否存在、目前風格是 TBD-like / Gitflow-like / 隨意），作為後續所有判斷的依據。**任何規則判斷都要能回答「我是根據哪個 Git/CI 證據下的判斷」**。

若盤點後仍缺乏關鍵資訊（見下方「User Interaction Rules」），先問，不要往下走。

## 高層 SOP（術，完整版與每步 Decision Tree 見 [workflow.md](references/workflow.md)）

```
Stage 0 現況盤點 → 1 任務分類 → 2 建立/直推判斷 → 3 開發(含解耦判斷)
→ 4 Commit → 5 與 trunk 同步(Integration 前檢查) → 6 Code Review
→ 7 Test/CI Gate → 8 Merge → 9 Release(從 trunk 或 release branch)
→ 10 收尾(刪分支、flag 清理排程、健康度檢查)
```

## 快速判斷 Decision Snapshot

**Q1 — 直推 trunk 還是開分支？**
變更是否 trivial（單一檔案/小修正）且專案慣例允許直推 trunk（極小團隊、無強制 PR）且本地測試綠燈？→ 可直推。否則 → 從最新 trunk 切一條 short-lived branch。

**Q2 — 分支是否還「短命」？**
分支年齡 > 2 天，或 diff > ~400 行，或已經跟 trunk 衝突好幾次 → 不合格。處理方式：拆成更小的 PR/stacked PR、今天內配對完成，或先用 Feature Flag 把可用部分併回去，剩下的續開新分支。

**Q3 — 需要 Feature Flag 或其他解耦技術嗎？**
會跨過 1 天以上才完成、且會動到使用者可觸及的路徑 → Feature Flag（Release Toggle）。
是大範圍內部實作替換、使用者無感 → Branch by Abstraction。
是後端演算法/資料源替換、要拿真流量驗證 → Dark Launch / 並行執行。
以上皆非（範圍小、能在 short-lived branch 期限內完成並直接整合）→ 不需要，直接整合即可。

**Q4 — 發布方式？**
持續部署、能快速 fix-forward → 直接從 trunk 發布。
需要多版本並存、上架審核、法規強制的 hardening → 從 trunk 就地切一條 release branch（不合併回 trunk，修 bug 一律先進 trunk 再 cherry-pick 下去）。

完整、含分支節點的 Decision Tree 請讀 [workflow.md](references/workflow.md)。

## 規則索引（法，詳見 [rules.md](references/rules.md)）

`rules.md` 是本 Skill 的規範核心，包含逐項可執行的判斷標準：Branch/Merge 判斷規則、Short-Lived Branch 判斷標準、Commit/Integration 規則、Code Review 規則、Testing/CI 規則、Feature Flag 使用判斷框架、Release 規則、Validation Rules（TBD 健康度檢查）、Exception Handling（hotfix、大型 DB migration、法規強制 release train 等例外）、User Interaction Rules、Git 操作規則（哪些能自動做、哪些要先確認）。**做任何非顯而易見的判斷前，先讀這份文件**。

## User Interaction Rules（何時該問，何時可以直接做）

**資訊不足就問（Minimal Assumption），常見觸發點：**
- 不知道 release 節奏（持續部署？固定排程？）
- 不知道部署環境/是否能快速 rollback
- 不知道是否已有 feature flag 系統，或是否允許新增依賴
- 分支/變更牽涉到其他人正在進行的工作，所有權不明確
- 變更涉及資料庫 schema、金流、權限等高風險領域，且沒有既有規範可依循

**可直接執行（低風險、Evidence First 支撐）：**
- 所有唯讀盤點指令（status/log/branch/diff）
- 從最新 trunk 建立新的 short-lived branch
- 本地小步 commit、跑測試
- Push 自己新建的分支、開 PR
- 依既有慣例產生 commit 訊息

**執行前必須先跟使用者確認（高風險，即使技術上可行）：**
`git push --force`（尤其共享分支）、直接推到受保護的 trunk 略過 CI/Review、`rebase -i` 改寫已推送/共享的歷史、刪除任何含未合併 commit 的分支、CI 未過或被跳過就 merge、刪除或切換 production 的 feature flag、切/刪除 release branch、`git reset --hard` 用在非「剛建立且僅本機」的分支、Revert 別人的 commit（Revert 自己的可自動做）。

詳見 [rules.md](references/rules.md#git-操作規則) 的完整清單與理由。

## 驗證與異常處理

- **Validation Rules**（目前流程是否符合 TBD？）：見 [rules.md](references/rules.md#validation-rules)，可隨時執行「TBD 健康度檢查」（活躍分支數、平均分支存活時間、每日整合率、CI 綠燈率、flag 是否有主人與到期日）。
- **發現違規時**：不是直接指責或強制重寫，而是依 [anti-patterns.md](references/anti-patterns.md) 找到對應的症狀→根因→改善建議，並用 Project-Aware 的方式提出（先問脈絡，再給方案，高風險修復動作照樣要確認）。

## 器：工具與 Workflow 階段對應

工具（Git 主機/合併佇列、CI/CD、Feature Flag 平台、測試框架、Commit/版本自動化）依 Workflow 各階段的對應與選型原則見 [tools.md](references/tools.md)。**先偵測專案已在用什麼工具，不擅自引入新工具鏈；只有在必要且專案缺乏對應能力時才建議並徵詢使用者。**

## 實際使用範例

5 個完整情境（小型修復直推 vs PR、需要 Feature Flag 的多日功能、大型重構用 Branch by Abstraction、既有 Gitflow 專案的漸進導入、資訊不足時如何提問、高風險操作如何確認）見 [examples.md](references/examples.md)。

## 補充資源索引

| 檔案 | 何時讀 |
|---|---|
| [glossary.md](references/glossary.md) | 需要快速查一個術語的定義（Trunk/Feature Flag/Branch by Abstraction…）時 |
| [principles.md](references/principles.md) | 需要說明「為什麼」、TBD 與 CI/CD/DevOps 關係、或要說服/教育使用者時 |
| [rules.md](references/rules.md) | 做任何 branch/merge/commit/review/test/flag/release/git 操作判斷時（最常用） |
| [workflow.md](references/workflow.md) | 需要完整 SOP 步驟或某個階段的 Decision Tree 細節時 |
| [tools.md](references/tools.md) | 需要建議或評估工具鏈時 |
| [anti-patterns.md](references/anti-patterns.md) | 偵測到可能違反 TBD 或使用者問「這樣做對嗎」時 |
| [examples.md](references/examples.md) | 需要具體範例校準行為時 |
