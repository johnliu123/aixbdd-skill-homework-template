# 關鍵字 / 術語速查表

集中列出本 Skill 會用到的核心術語一句話定義，方便快速查閱。完整脈絡與判斷規則見對應章節連結；本檔只做定義，不重複判斷邏輯。

## 核心概念

| 術語 | 一句話定義 |
|---|---|
| **Trunk-Based Development (TBD)** | 以單一 trunk（`main`/`master`）為整合中心的開發模式，長期分支是例外不是常態 |
| **Trunk** | 專案唯一的整合中心分支，理論上永遠必須是可建置/可測試的 |
| **Short-Lived Branch** | 存活時間以「小時」計、硬上限 1–2 天的分支，是 TBD 中分支的唯一合理形式 |
| **Continuous Integration (CI)** | 每天至少把工作整合回 trunk 一次，並用自動化測試驗證的實踐 |
| **Small Changes（小批次）** | 小範圍、高頻率的變更與整合，diff 越小風險與 review 成本越低 |
| **Merge Skew** | 兩個分支各自測試都過，但合併在一起後才出現的衝突/壞狀態 |

## 分支與整合

| 術語 | 一句話定義 |
|---|---|
| **Squash Merge** | 把一個分支的所有 commit 壓成一個再合併，保持 trunk 歷史乾淨（TBD 預設選項） |
| **Merge Commit** | 保留分支上原始多個 commit 與脈絡的合併方式 |
| **Rebase Merge** | 讓分支歷史線性化後再合併，只能用在未被他人 fork 的分支 |
| **Merge Queue / Merge Train** | 依序自動化驗證並合併多個 PR 的機制，避免 Merge Skew |
| **Build Cop** | Trunk 變紅（build broken）時負責立即修復或 revert 的指定角色 |

## Feature 解耦技術

| 術語 | 一句話定義 |
|---|---|
| **Feature Flag / Release Toggle** | 用開關把「合併到 trunk」與「對使用者上線」分開，flag 關閉時功能對使用者不可見 |
| **Branch by Abstraction** | 先引入抽象介面，讓新舊實作並存並逐步切換呼叫端，取代長期分支做大範圍重構 |
| **Dark Launch / Parallel Run** | 讓新路徑（尤其後端邏輯）在背景跑並比對結果，但不影響正式回應，用於在不影響使用者前提下拿真流量驗證 |

## Release 與資料變更

| 術語 | 一句話定義 |
|---|---|
| **Release Branch** | 就地從 trunk 切出、用於 hardening/多版本並存的分支；絕不合併回 trunk，修 bug 一律先進 trunk 再 cherry-pick |
| **Expand → Migrate → Contract** | 資料庫 schema 變更的安全模式：先擴充相容結構、雙寫雙讀驗證、確認穩定後才移除舊結構 |
| **Flaky Test** | 結果不穩定（時好時壞）的測試，需隔離並排入修復，不能長期忽略 |

## 判斷原則

| 術語 | 一句話定義 |
|---|---|
| **Evidence First** | 用 Git log、CI 結果、實際 diff 做判斷依據，不是憑印象 |
| **Project-Aware** | 先看專案現有慣例與限制，再決定要不要調整，不盲目套規則 |
| **Minimal Assumption** | 關鍵資訊（release 節奏、部署環境、是否有 flag 系統）不足就問，不猜 |

## 何時該讀哪份文件

| 需求 | 讀這份 |
|---|---|
| 想快速查一個術語的定義 | 本檔（glossary.md） |
| 想知道「為什麼」、TBD 與 DevOps 的關係 | [principles.md](principles.md) |
| 想做 branch/merge/review/flag/release 判斷 | [rules.md](rules.md) |
| 想知道完整 SOP 步驟 | [workflow.md](workflow.md) |
| 想評估工具鏈 | [tools.md](tools.md) |
