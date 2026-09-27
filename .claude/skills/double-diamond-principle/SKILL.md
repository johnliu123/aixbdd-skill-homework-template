---
name: double-diamond-principle
description: >-
  以 Design Council 雙鑽石模型（Double Diamond：Discover/Define/Develop/Deliver）為核心的
  問題探索與方案交付判斷 Skill。啟動後 AI 會自動盤點目前的問題與專案背景、判斷現在處於哪個階段、
  判斷該 Diverge（發散）還是 Converge（收斂）、依情境選擇研究/發想/驗證方法，協助蒐集與整理資訊、
  把問題定義清楚（而非直接跳到方案）、產生並收斂解決方案、建立原型並取得使用者回饋、依證據判斷是否
  進入下一階段或退回前一階段重新探索。使用者不需要具備 Double Diamond 知識；AI 需要具備，並用證據
  （研究資料、使用者回饋、測試結果）做判斷，而不是套公式或憑空假設。資訊不足時一律先問，不猜測。
  使用情境：使用者描述一個模糊問題、新專案/新功能需求、想做使用者研究/工作坊/原型測試與驗證、
  要求「先定義問題再談方案」、或要 AI 接手完成「理解問題 → 探索 → 定義 → 發展方案 → 驗證 → 交付」
  全流程時。常見觸發詞：「雙鑽石」「Double Diamond」「Discover」「Define」「Develop」「Deliver」
  「發散」「收斂」「Diverge」「Converge」「使用者研究」「問題定義」「Problem Statement」「HMW」
  「Persona」「原型測試」「Design Sprint」「User Research」「這樣做對嗎」等，即使使用者沒有直接
  說出「Double Diamond」這個名稱也適用。
disable-model-invocation: true
---

# Double Diamond — AI Project Ownership Skill

## 定位

這不是一份 Double Diamond 教學文件，而是讓 AI 具備**判斷力**、能主動 **Own 專案從「理解問題」到「交付」全流程**的 Workflow Skill。使用者不需要懂 Discover/Define/Develop/Deliver 是什麼；AI 要懂，並且要用證據（研究資料、使用者回饋、測試結果）做判斷，而不是憑空假設或套公式跑完四個階段。

**核心工作方式**：Problem First（先理解問題再談方案）→ Evidence First（先蒐證再收斂）→ Diverge 後才 Converge → Project-Aware（依專案規模調整嚴謹度）→ 資訊不足就問 → 證據推翻假設就退回前一階段重新探索。

## 核心心智模型（道，細節見 [principles.md](references/principles.md)）

```
   ╱╲                    ╱╲
  ╱  ╲                  ╱  ╲
 ╱    ╲________________╱    ╲________________
 ╲    ╱                ╲    ╱
  ╲  ╱                  ╲  ╱
   ╲╱                    ╲╱
DISCOVER   DEFINE      DEVELOP   DELIVER
 (發散)      (收斂)       (發散)     (收斂)

└──── 問題空間 Problem Space ────┘└──── 解決方案空間 Solution Space ────┘
```

| 原則 | 一句話 |
|---|---|
| Problem First | 先確認「User 是誰、Problem 是什麼」，才輪到 Solution；沒有問題證據前不接受直接跳方案 |
| Diverge → Converge | 每個階段都先廣度優先發散，再用證據收斂，不因時間壓力跳過發散 |
| Evidence First | 收斂依據是研究資料、使用者回饋、測試結果，不是團隊/AI 的直覺共識 |
| Put people first / Communicate visually / Collaborate / Iterate | Design Council 2019 版四大原則，見 principles.md |
| Project-Aware | 依專案規模（輕量/標準/完整）調整嚴謹度，不盲目跑完整四階段 |
| Minimal Assumption | 目標使用者、成功定義、資源限制等關鍵資訊不足就問，不猜 |

## Stage 0：啟動時必做——理解問題與專案背景（Evidence First）

在做任何階段判斷之前，先盤點現況，不用等使用者主動提供：

1. **讀取既有資訊**：專案內是否已有 PRD/spec、issue/backlog、使用者回饋、數據、先前研究文件？
2. **判斷專案類型**：新產品／既有產品新功能／服務或內部流程／策略性專案／明確規格的小改動
3. **判斷嚴謹度分級**：輕量／標準／完整（見 [principles.md](references/principles.md#project-aware專案規模決定嚴謹度不是流程決定專案)）
4. **判斷目前所處階段**：見下方 Decision Snapshot
5. **檢查關鍵缺口**：目標使用者、成功定義/KPI、資源與時間限制、既有研究資料、決策權歸屬——任一缺口影響下一步判斷，先問，不猜（見下方 User Interaction Rules）

完整版見 [workflow.md](references/workflow.md#stage-0啟動理解問題與專案背景)。

## 四階段總覽（法，完整定義/輸入輸出/Gate 見 [rules.md](references/rules.md)）

| 階段 | 發散/收斂 | 目的 | 進入條件 | 離開條件（Gate） |
|---|---|---|---|---|
| **Discover** | Diverge | 理解問題、使用者與情境，建立洞察庫 | 有初始問題/機會敘述、有可接觸的使用者或資料 | 研究涵蓋目標使用者/情境；洞察出現重複模式；有候選機會領域 |
| **Define** | Converge | 收斂成解法中立的 Problem Statement | Discover Gate 達成 | 有被認可的 Problem Statement；優先排序的 HMW；可衡量的成功指標 |
| **Develop** | Diverge | 大量產生並測試多元解法 | Define Gate 達成 | ≥2 概念做過使用者測試；證據指向優選方向；feasibility/viability 通過；風險已辨識 |
| **Deliver** | Converge | 定案、交付、建立回饋機制 | Develop Gate 達成 | 已上線；回饋機制就位；有成效追蹤指標；學習已文件化 |

## Decision Snapshot（三個核心判斷）

**Q1 — 我現在在哪個階段？**
```
沒有被認可的 Problem Statement → Discover（無研究）或 Discover→Define 過渡（有研究未收斂）
有 Problem Statement 但沒有測試過的原型 → Develop
有測試過的原型但未選定方案/未做 feasibility 檢查 → 仍在 Develop
已選定方案並通過 feasibility/viability 檢查 → Deliver
```

**Q2 — 現在該 Diverge 還是 Converge？**
```
目前的[洞察/方案候選]數量與多樣性，還不足以代表這個問題/方案空間 → Diverge，繼續擴大、不篩選
已有足夠證據（重複模式/測試結果）可以安全刪選項而不遺漏重要可能性 → Converge，開始分群/排序/決定
```

**Q3 — 可以進下一階段，還是要退回？**
```
對照上表的「離開條件」逐項檢查 → 全部滿足才進下一階段
若驗證結果推翻了「問題本身」的假設 → 退回 Discover/Define
若推翻的只是「這個方案」，問題定義仍成立 → 退回 Develop 重新發想
```

完整 Phase Detection / Diverge-Converge 流程圖與逐步 SOP 見 [workflow.md](references/workflow.md)。

## 規則索引（詳見 [rules.md](references/rules.md)）

`rules.md` 是規範核心，包含逐項可執行的判斷標準：四階段完整定義（Purpose/Input/Output/Entry/Exit Criteria）、Decision Rules、Diverge/Converge 判斷規則、**Validation Rules**（證據夠不夠、樣本量依規模調整）、**Exception Handling**（跳階段要求、資源受限、驗證推翻假設、關係人意見不一致等例外情境）、**User Interaction Rules**（何時該問、何時可直接做、怎麼問）。**做任何非顯而易見的判斷前，先讀這份文件。**

## 器：研究／發想／驗證方法選擇（詳見 [tools.md](references/tools.md)）

`tools.md` 依階段與 Diverge/Converge 分類列出：Research（既有資料/訪談/問卷/情境訪查/日誌研究/Service Safari/競品分析）、綜合與定義工具（Affinity Mapping/Persona/JTBD/Journey Map/Problem Statement/HMW/Empathy Map/Design Brief）、Workshop 引導技巧、Ideation 方法（Brainstorming/SCAMPER/Crazy 8s）、Prototype 方法（Paper Sketch/Wireframe/Wizard of Oz/Service Blueprint）、Validation/User Testing（可用性測試/A/B Test/Fake Door/UAT）、Prioritization 工具（Impact-Effort/RICE/MoSCoW）、常見軟體工具對應。**先偵測專案已在用什麼工具/資料，不擅自引入新方法或軟體**，只有在必要且專案缺乏對應能力時才建議並徵詢使用者。

## User Interaction Rules（何時該問，何時可以直接做）

**可直接執行（低風險，Evidence First 支撐）：**
- 讀取專案既有文件/資料，整理現況與缺口
- 用既有資訊草擬 Journey Map、Persona、Problem Statement、HMW（明確標註為**待確認的草稿**）
- 產出 ideation 候選清單、方法選擇建議、驗證方案建議

**必須先問，不能假設（Minimal Assumption 常見觸發點）：**
- 目標使用者是誰、他們的情境與目標
- 專案的成功定義/KPI
- 資源與時間限制（能否做正式研究、能做幾輪原型）
- 是否已有既有研究資料，避免重複蒐集
- 使用者要求跳階段時，是否已知情並同意承擔風險
- 誰有最終決策權（Problem Statement、方案取捨的 sign-off owner）

**提問方式**：用情境化提問，不要求使用者先懂術語（❌「你現在在 Discover 還是 Define？」 ✅「這個問題有沒有跟實際使用者聊過，或有數據可以參考？」）；一次把同一決策所需的關鍵缺口問完。完整規則見 [rules.md](references/rules.md#user-interaction-rules何時該問何時可以直接做)。

## 驗證與異常處理

- **Validation Rules**（證據夠不夠）：依專案規模調整樣本量/飽和度標準；Develop→Deliver 一律要求至少 1 輪真實使用者測試 + feasibility/viability 檢查。見 [rules.md](references/rules.md#validation-rules證據夠不夠的判斷標準)。
- **發現偏離模式時**：對照 [anti-patterns.md](references/anti-patterns.md) 找到症狀→根因→改善建議，用提示+尊重使用者決定的方式處理，不強制重寫。
- **迭代退回**：退回哪一階段取決於「哪個假設被推翻」，不是「哪個階段做完了想重做」，對照表見 [rules.md](references/rules.md#exception-handling例外情況處理)。

## 常見錯誤與 Anti-patterns

Solution-First（跳過問題直接做方案）、Fake Divergence（假發散）、Persona Theater（無研究支撐的憑空 persona）、Endless Discover（分析癱瘓）、HMW 裡預埋解法、Prototype 當成品直接上線、測試找同意的人、一次性交付無回饋機制、為流程而流程、只看 desirability 忽略 feasibility/viability、Brief 未 sign-off 就開發、把 workshop 當唯一決策依據。每項的症狀/根因/偵測/改善建議見 [anti-patterns.md](references/anti-patterns.md)。

## 實際使用範例

5 個完整情境（模糊問題的標準規模全流程、服務類流程優化、使用者要求跳過探索的例外處理、驗證推翻問題假設後的退回、明確規格小改動的輕量路徑）見 [examples.md](references/examples.md)。

## 補充資源索引

| 檔案 | 何時讀 |
|---|---|
| [glossary.md](references/glossary.md) | 需要快速查一個術語的定義（Discover/HMW/Persona/Feasibility…）時 |
| [principles.md](references/principles.md) | 需要說明「為什麼」、Double Diamond 的官方定義與四大原則、或要向使用者解釋理念時 |
| [rules.md](references/rules.md) | 做任何階段判斷、Gate 檢查、Diverge/Converge 判斷、例外處理、決定該不該問時（最常用） |
| [workflow.md](references/workflow.md) | 需要完整 SOP 步驟、Phase Detection/Diverge-Converge 流程圖細節、或 Gate Artifact 清單時 |
| [tools.md](references/tools.md) | 需要選擇或建議研究/發想/原型/驗證方法與工具時 |
| [anti-patterns.md](references/anti-patterns.md) | 偵測到可能偏離 Double Diamond 精神、或使用者問「這樣做對嗎」時 |
| [examples.md](references/examples.md) | 需要具體範例校準行為、或想看 AI 在例外情境下如何應對時 |
