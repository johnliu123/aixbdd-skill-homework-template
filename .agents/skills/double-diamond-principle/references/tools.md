# 器：方法與工具選擇規則

原則：**先看專案已在用什麼工具/資料，不擅自引入新方法論或軟體**；只有在必要且專案缺乏對應能力時才建議，並徵詢使用者（見 [rules.md](rules.md#user-interaction-rules何時該問何時可以直接做)）。以下每類方法都附「何時選這個 vs 其他」的判斷規則，不是列出來讓你全部套用。

## 研究方法（Research）— 適用 Discover，Diverge

| 方法 | 何時選用 | 產出 |
|---|---|---|
| **既有資料/桌面研究**（analytics、support tickets、既有文件、市場資訊） | 永遠先做這個，成本最低；資源極有限時可能是唯一的研究來源 | 現況數據摘要、已知痛點清單 |
| **使用者訪談**（半結構化為主） | 需要理解「為什麼」、動機與情境，而非單純的量化行為 | 逐字稿、行為與動機洞察 |
| **問卷/量化調查** | 需要驗證某個假設在多大比例使用者身上成立、或需要可統計的分布 | 量化分布數據，用於三角驗證質化洞察 |
| **情境訪查/User Shadowing** | 使用者「說的」和「做的」可能不一致，或行為發生在特定實體/操作環境中 | 觀察筆記、真實行為紀錄（而非自我報告） |
| **日誌研究（Diary Study）** | 需要瞭解跨較長時間（數天至數週）的行為模式，且不適合單次訪談捕捉 | 縱向紀錄，含情境時間軸 |
| **Service Safari**（親身體驗服務） | 團隊對某類服務缺乏第一手體驗，需要快速建立共同感受與詞彙 | 團隊共同的體驗筆記，激發後續訪談問題 |
| **競品/對照分析** | 需要瞭解市場上已有的解法、避免重複踩坑或錯失已驗證的模式 | 對照表：他人怎麼解、優劣與可借鑑點 |

**選擇規則**：資訊來源優先度＝既有資料 > 觀察/情境訪查 > 訪談 > 問卷（問卷通常用於「驗證」訪談已發現的模式，很少單獨作為第一步）。

## 綜合與定義工具 — 適用 Define，Converge

| 方法 | 何時選用 | 產出 |
|---|---|---|
| **Affinity Mapping（親和圖）** | Discover 產出的洞察/紀錄量大、需要找出重複主題 | 分群後的主題/機會領域 |
| **Persona / Jobs-to-be-Done（JTBD）** | 使用者類型不只一種，需要在後續 Develop 階段維持對「誰」的聚焦；JTBD 更適合強調「使用者想完成的任務」而非人口統計特徵 | 1 個或一組使用者代表輪廓，**必須基於研究**，否則視為 [Persona Theater](anti-patterns.md#3-persona-theater--沒有研究支撐的憑空persona) |
| **User Journey Mapping** | 問題橫跨多個接觸點/步驟，需要看清全貌與痛點位置 | 視覺化的階段/接觸點/痛點/情緒地圖 |
| **Problem Statement Canvas** | 需要把發散的洞察收斂成一句可執行、解法中立的問題定義 | 「[使用者] 在 [情境] 中需要 [需求]，但 [障礙]」格式的陳述 |
| **How Might We（HMW）** | Problem Statement 定案後，需要把「問題」轉成可發想的「問句」，進入 Develop 前的橋接 | 一組可排序的 HMW 問句 |
| **Empathy Map** | 需要快速對齊團隊對某使用者群的「說/想/做/感受」的共同理解 | 四象限圖（說、想、做、感受） |
| **Design Brief** | Define 收斂完成，需要正式文件讓關係人 sign-off 並guide Develop | 正式問題定義文件（目標、範圍、限制、成功指標） |

**選擇規則**：先做 Affinity Mapping 找主題 → 視需要產出 Persona/JTBD 與 Journey Map → 收斂成 Problem Statement → 轉成 HMW → 寫成 Design Brief 取得 sign-off。不是每個專案都需要全部工具，依 [principles.md](principles.md#project-aware專案規模決定嚴謹度不是流程決定專案) 的嚴謹度分級取捨。

## Workshop 引導技巧 — 跨階段協作工具

| Workshop 類型 | 適用階段 | 目的 |
|---|---|---|
| **Discovery Workshop** | Discover | 快速對齊團隊對問題現況的認知，激發後續研究方向 |
| **Synthesis / Prioritization Workshop**（含 Dot Voting、Impact-Effort Matrix） | Define | 集體從大量洞察/機會中收斂出優先項目 |
| **Design Studio / Co-Design Workshop** | Develop | 讓多元角色（含使用者）一起快速草繪、比較概念 |
| **Retrospective / Learning Workshop** | Deliver 結束後 | 回顧本輪學習，作為下一週期輸入 |

**選擇規則**：Workshop 是「加速協作與共識」的手段，不是必須項目；決策仍要有證據支撐，不能讓 workshop 討論結果取代真實使用者證據（見 [anti-patterns.md](anti-patterns.md#12-把-workshop-當成唯一決策依據)）。

## Ideation 方法 — 適用 Develop，Diverge

| 方法 | 何時選用 |
|---|---|
| **Brainstorming**（遵守 defer judgement／build on others'／one idea per note 等規則） | 預設起手方法，適合大部分情境 |
| **SCAMPER**（Substitute/Combine/Adapt/Modify/Put to other use/Eliminate/Reverse） | 已有既有方案/產品，需要系統性地從既有基礎變形出新想法 |
| **Crazy 8s**（8 分鐘畫 8 個概念） | 需要快速逼出比第一個想法更多的變化，避免定錨 |
| **Worst Possible Idea** | 團隊卡在「安全牌」想法，需要打破慣性思維 |
| **類比啟發（Analogous Inspiration）** | 想從其他產業/情境借鏡已被驗證的模式 |

**選擇規則**：任何 ideation 產出至少要有 ≥3 個方向性不同的候選概念才算完成發散，只產出 1 個等同於 Fake Divergence。

## Prototype 方法 — 適用 Develop（發散到收斂的橋接）

| 方法 | 何時選用 | 成本/精細度 |
|---|---|---|
| **Paper Sketch / 手繪原型** | 概念驗證階段，重點是快速拿到方向性回饋 | 極低 |
| **Wireframe / 可點擊 Mockup** | 需要測試資訊架構、流程、互動邏輯 | 低—中 |
| **Wizard of Oz / Concierge** | 想在真正建構後端/自動化之前，先驗證使用者是否需要這個服務 | 低（人力代替系統） |
| **Storyboard** | 想溝通一段跨時間/多步驟的體驗，而非單一畫面 | 低 |
| **Service Blueprint** | 方案涉及前台（使用者可見）與後台（內部流程/系統）的協同，需要看清依賴關係 | 中 |
| **Experience Prototyping / Role-play** | 服務類、實體空間類方案，需要「演出來」才能感受體驗 | 中 |
| **Business Model Canvas** | 需要驗證方案的商業/資源可行性（viability），而非只驗證使用者想不想要 | 低（畫布式） |

**選擇規則**：原則是「早、醜、快」——先用最低成本的原型驗證最大的不確定性，通過後才投入更精細的原型。不要為了「做得漂亮」跳過低成本原型直接做高保真成品。

## Validation / User Testing 方法 — 適用 Develop 收斂 ＆ Deliver

| 方法 | 何時選用 |
|---|---|
| **可用性測試（Usability Testing，moderated/unmoderated）** | 驗證使用者能否理解與操作原型/介面 |
| **A/B Testing** | 已有可上線的兩個以上版本，需要用真實流量統計比較效果 |
| **Fake Door Test** | 想低成本驗證需求是否存在，尚不打算真正建構功能 |
| **Beta / Pilot 測試** | 方案已相對成熟，需要在受控的小範圍真實環境驗證 |
| **UAT（User Acceptance Testing）** | Deliver 階段，交付前的最終確認測試 |
| **NPS / CSAT 等滿意度指標** | Deliver 後，需要建立長期的成效追蹤機制 |

**選擇規則**：測試對象必須是真實或高度代表性的使用者，**不能只找內部同事或立場一致的人**（見 [anti-patterns.md](anti-patterns.md#7-測試找同意的人--confirmation-bias-取樣)）。

## Prioritization／決策工具 — 跨階段收斂輔助

| 工具 | 何時選用 |
|---|---|
| **Impact-Effort Matrix** | 需要快速從一堆候選（機會或方案）中挑出「高影響、低成本」的優先項 |
| **RICE / ICE Score** | 需要較量化、可比較的排序方式，且有一定的估算基礎 |
| **MoSCoW（Must/Should/Could/Won't）** | 定義 MVP 範圍時，需要明確區分必要與非必要項目 |
| **加權決策矩陣（Weighted Scoring）** | 選項之間需要依多個不同權重的準則比較 |
| **Dot Voting** | 團隊/工作坊現場快速收斂共識 |

## 常見軟體工具對應（業界實踐，僅供參考，不強制）

| 用途 | 常見工具 |
|---|---|
| Workshop／親和圖／Journey Map 協作 | Miro、Mural、FigJam |
| 高保真原型／介面設計 | Figma、Sketch |
| 遠端使用者測試 | UserTesting、Maze、Lookback |
| 研究資料整理/知識庫 | Dovetail、Airtable、Notion |
| 量化行為數據 | Google Analytics、Mixpanel、Amplitude |
| 問卷 | Typeform、Google Forms |
| 卡片分類/資訊架構測試 | Optimal Workshop |

若專案已有慣用工具鏈，優先沿用；若專案缺乏對應能力且確有需要，才建議新增，並先徵詢使用者（成本、學習曲線、資料隱私都是需要一併確認的資訊）。
