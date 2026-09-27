# 術：完整 SOP 與 Decision Tree

## Stage 0：啟動——理解問題與專案背景

在做任何階段判斷之前，先蒐集現況，不用等使用者主動提供：

1. **盤點既有資訊**：專案內是否已有 PRD/spec、issue/backlog、使用者回饋、analytics 數據、先前的研究文件？（讀取，不用先問）
2. **判斷專案類型**：新產品／既有產品新功能／服務或內部流程／策略性專案／單純的 bug 或規格調整。
3. **判斷嚴謹度分級**：依 [principles.md](principles.md#project-aware專案規模決定嚴謹度不是流程決定專案) 分成輕量／標準／完整。
4. **判斷目前所處階段**：見下方 Phase Detection Decision Tree。
5. **檢查關鍵資訊缺口**：目標使用者、成功定義、資源/時間限制、既有研究資料、決策權歸屬。任一缺口且會影響下一步判斷 → 依 [rules.md](rules.md#user-interaction-rules何時該問何時可以直接做) 先問，不猜。

盤點完成後，內部形成一份「現況摘要」（所處階段、嚴謹度分級、已有的證據、缺口），作為後續所有判斷的依據。**任何階段/方法判斷都要能回答「我是根據哪個證據或使用者回覆做的判斷」**。

## Phase Detection Decision Tree（你現在在哪個階段？）

```
Q1: 有沒有一個「已被使用者/關係人認可」的 solution-neutral Problem Statement？
 ├─ 沒有，且完全沒有研究/資料
 │    → DISCOVER：從研究與資料蒐集開始
 ├─ 沒有，但已有一些研究/資料尚未收斂
 │    → 仍在 DISCOVER，或已可進入 DEFINE 做收斂（檢查 Discover Exit Criteria）
 └─ 有（已認可）
      ↓
Q2: 有沒有 ≥1 個「已經過真實使用者測試」的原型/方案？
 ├─ 沒有
 │    → DEVELOP：產生並測試候選方案
 └─ 有
      ↓
Q3: 是否已選定最終方案，且通過 feasibility/viability 檢查？
 ├─ 沒有 → 仍在 DEVELOP（收斂子階段：篩選/確認優選方案）
 └─ 有 → DELIVER：定案、上線、建立回饋機制
```

## Diverge vs Converge Decision Tree（階段內部，任何時刻都可套用）

```
Q1: 目前蒐集/產生的 [洞察 或 方案候選] 數量與多樣性，
    是否足以代表這個問題/方案空間，而不只是第一個想到的答案？
 ├─ 否 → DIVERGE：繼續擴大蒐集/發想，先不篩選、不評判
 └─ 是
      ↓
Q2: 是否已有足夠證據（重複模式／測試結果／三角驗證）
    可以安全刪除選項而不遺漏重要可能性？
 ├─ 否 → 還不能收斂；用小規模驗證或補資料點填補證據缺口（仍偏 Diverge）
 └─ 是 → CONVERGE：分群、排序、篩選、做決定
```

**常見誤判提醒**：因時間壓力跳過發散直接收斂 → 見 [anti-patterns.md](anti-patterns.md#2-fake-divergence--假發散) 的 Fake Divergence；發散過久遲遲不收斂 → 見 anti-patterns.md 的 Analysis Paralysis。

## 完整 SOP 流程

### Stage 1 — Discover（發散）
1.1 界定初始問題範疇（哪怕模糊）— 用一句話寫下「目前以為的問題」，明確標註這只是待驗證的假設
1.2 盤點既有資料（analytics、support tickets、先前研究、市場/競品資訊）
1.3 依 [tools.md](tools.md) 的「研究方法」選擇規則挑研究方法，執行研究（訪談/觀察/日誌研究/問卷等）
1.4 整理 raw data：逐字稿、觀察筆記、量化摘要，先不下結論
1.5 檢查 [Discover Exit Criteria](rules.md#1-discover發散--問題空間左半) → 達標進 Stage 2；未達標則繼續研究，或依 Exception Handling 與使用者確認是否接受較弱證據前進

### Stage 2 — Define（收斂）
2.1 Synthesis：affinity mapping／分群，找出重複主題
2.2 產出 insight 清單與候選機會領域清單
2.3 撰寫多個候選 Problem Statement（每個都 solution-neutral，見句型規則）
2.4 轉換成 How Might We（HMW）清單並排序（依 impact／feasibility／與目標的關聯度）
2.5 與使用者/關係人確認，sign-off Design Brief 與成功指標
2.6 檢查 [Define Exit Criteria](rules.md#2-define收斂--問題空間右半) → 達標進 Stage 3

### Stage 3 — Develop（發散→內部小收斂循環）
3.1 依 Design Brief 進行 ideation（見 [tools.md](tools.md) 的「Ideation 方法」）
3.2 初步篩選候選概念（dot voting／impact-effort matrix），**避免把全部 idea 都做成原型**
3.3 針對候選概念做低成本原型（paper sketch／wireframe／service blueprint／wizard of oz，依內容類型選）
3.4 使用者測試 + 回饋收集，每輪記錄學習
3.5 依回饋決定：繼續迭代同一概念 / 切換其他候選概念 / 退回 Define 重新定義問題（見 [rules.md](rules.md#exception-handling例外情況處理)）
3.6 檢查 [Develop Exit Criteria](rules.md#3-develop發散--解決方案空間左半) → 達標進 Stage 4

### Stage 4 — Deliver（收斂）
4.1 最終化選定方案的細節（視覺/技術/內容/流程）
4.2 執行最終測試（usability／UAT／QA）
4.3 準備上線：launch plan、rollout 策略、風險應對、正式 sign-off
4.4 建立回饋與監測機制（analytics、回饋管道、成功指標儀表板）
4.5 上線／交付
4.6 回顧與知識回饋：把本輪學習（哪些假設對/錯、哪些方法有效）記錄下來，作為下一個週期 Discover 的輸入

## 迴圈與迭代規則

退回哪一階段，取決於「哪個假設被打破」，不是「哪個階段做完了想重做」：

| 什麼被推翻 | 退回到 |
|---|---|
| 使用者根本沒有這個問題/需求不存在 | Discover |
| 問題存在但定義的方向/範圍不對 | Define |
| 問題定義沒錯，但這個方案不是對的解法 | Develop |
| 方案沒錯，但上線後執行細節/採用度不如預期 | Deliver 內部迭代，或視嚴重度退回 Develop |

## Gate 通過的具體 Artifact 清單（可直接照抄檢查）

| Gate | 必備 Artifact |
|---|---|
| Discover → Define | 研究紀錄（訪談/觀察/資料摘要）、insight 清單、候選機會領域清單 |
| Define → Develop | 已認可的 Problem Statement、優先排序的 HMW、Design Brief、成功指標 |
| Develop → Deliver | ≥2 個原型的使用者測試結果、feasibility/viability 檢查結果、風險清單與對策、MVP 範圍與驗收標準 |
| Deliver → 完成/下一週期 | 上線紀錄、回饋機制、成效追蹤指標、事後學習紀錄 |
