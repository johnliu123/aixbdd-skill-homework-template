# 法：四階段規範與決策規則

本檔是判斷「現在該做什麼、能不能進下一階段」的規範核心。做任何非顯而易見的階段判斷前，先讀這份文件對應章節。

## 四階段完整定義表

### 1. Discover（發散 · 問題空間左半）

| 項目 | 內容 |
|---|---|
| **Purpose** | 不假設問題是什麼，實際理解使用者、情境與證據，建立廣泛的知識與洞察庫 |
| **Input** | 初始觸發（需求、抱怨、機會、現象），任何既有資料（analytics、support tickets、既有文件、市場資訊） |
| **Output** | 原始研究資料（訪談逐字稿/筆記、觀察紀錄）、初步 journey map 草稿、insight 清單、候選機會領域清單 |
| **Entry Criteria** | 有一個初始問題/機會敘述（即使模糊）；有可接觸的使用者或資料來源 |
| **Exit Criteria（→ Define）** | ① 研究涵蓋目標使用者、關鍵關係人、使用情境；② 洞察出現重複模式（見下方 Validation Rules 的飽和度指引，依專案規模調整）；③ 已能列出候選機會領域，而非一片空白 |
| **Diverge 原則** | 廣度優先，不篩選、不評判；質化＋量化多來源三角驗證；記錄矛盾證據，不要提早調和成單一結論 |

### 2. Define（收斂 · 問題空間右半）

| 項目 | 內容 |
|---|---|
| **Purpose** | 把 Discover 的大量資訊收斂成明確、可執行、**解法中立（solution-neutral）**的問題定義 |
| **Input** | Discover 全部產出 |
| **Output** | Problem Statement、優先排序的 How Might We（HMW）清單、Design Brief、成功指標/驗收標準草稿、persona 或 Jobs-to-be-Done（如適用） |
| **Entry Criteria** | Discover Exit Criteria 已達成 |
| **Exit Criteria（→ Develop）** | ① 有一句被關係人認可的 solution-neutral problem statement；② 有優先排序的 HMW 清單；③ 有可衡量的成功指標；④ 團隊/關係人對「要解的問題」達成一致（sign-off） |
| **Converge 原則** | 用 affinity mapping／分群消除雜訊；Problem Statement 用「[使用者] 在 [情境] 中，需要 [需求]，但 [障礙/落差]」句型，**禁止在句子裡預埋解法**；主動篩掉低優先機會，不是每個 insight 都要處理 |

### 3. Develop（發散 · 解決方案空間左半）

| 項目 | 內容 |
|---|---|
| **Purpose** | 針對已定義的問題，大量產生並探索多元解法，不急著挑一個 |
| **Input** | Design Brief、Problem Statement、成功指標 |
| **Output** | 多個概念草圖/原型、每個概念的 feasibility（技術可行）/desirability（使用者想要）/viability（商業可行）初評、每輪使用者測試回饋 |
| **Entry Criteria** | Define Exit Criteria 已達成 |
| **Exit Criteria（→ Deliver）** | ① 至少 2 個以上概念做過原型並讓真實使用者測試過（不只是內部評審）；② 證據指向明確的優選方向；③ Feasibility/Viability 檢查通過；④ 主要風險已辨識並有對策；⑤ MVP 範圍與驗收標準明確 |
| **Diverge 原則** | 先求數量、defer judgement、跨領域 co-design；**只做一個原型就收斂視為違規**（見 anti-patterns.md） |

### 4. Deliver（收斂 · 解決方案空間右半）

| 項目 | 內容 |
|---|---|
| **Purpose** | 定案、打磨、上線交付，並建立回饋與衡量機制、把學習回饋給組織 |
| **Input** | 已驗證的優選方案 + MVP 範圍 |
| **Output** | 最終產品/服務、上線計畫、回饋蒐集機制、成效衡量指標、事後學習紀錄 |
| **Entry Criteria** | Develop Exit Criteria 已達成 |
| **Exit Criteria（完成）** | ① 已上線/交付；② 回饋機制已就位；③ 有明確指標在追蹤成效；④ 學習經驗已文件化，回饋給團隊/下一週期 |
| **Converge 原則** | 最終測試與去風險化、明確 sign-off；**上線是回饋循環的開始，不是專案的結束** |

## Decision Rules：判斷你現在在哪個階段

| 現況 | 所在階段 |
|---|---|
| 還沒有任何被認可的 Problem Statement | Discover（若完全沒研究）或 Discover→Define 過渡（若已有研究但未收斂） |
| 已有 solution-neutral 的 Problem Statement，但沒有任何測試過的原型 | Develop |
| 有 ≥1 個測試過的原型，但還沒選定最終方案/沒做 feasibility 檢查 | 仍在 Develop（收斂子階段） |
| 已選定方案、通過 feasibility/viability 檢查，正在準備上線 | Deliver |
| 已上線並在追蹤成效 | 完成，進入下一個迴圈（可能是新的 Discover） |

完整的階段判斷流程與 Diverge/Converge 判斷流程圖見 [workflow.md](workflow.md#phase-detection-decision-tree)。

## Validation Rules：證據「夠不夠」的判斷標準

飽和度/樣本量依 [principles.md](principles.md#project-aware專案規模決定嚴謹度不是流程決定專案) 的專案規模分級調整，不是固定數字：

| 專案規模 | Discover 階段的「夠了」標準 |
|---|---|
| 輕量 | 有明確規格或既有資料佐證即可，可不做正式訪談 |
| 標準 | 3–5 次訪談或等量支援單/使用行為資料，且開始出現**重複模式** |
| 完整 | 涵蓋主要 segment，質化樣本達到飽和（新訪談不再出現新主題，常見經驗值約 12–20 次，依領域調整），並有量化資料交叉驗證 |

**Develop→Deliver 的驗證門檻（不分規模，都必須滿足）**：
- 至少對挑選出的方案做過 **1 輪真實使用者測試**（不能只靠內部評審或 AI 自己的判斷）
- Feasibility 由懂技術/營運的人或既有技術限制文件確認過
- Viability（資源、商業意義）已被確認，不是「做得出來但沒人要用/沒有價值」

**證據強度不足時怎麼辦**：不強行宣稱「已驗證」，改為明確標註「證據等級：弱／中／強」與「尚待驗證的假設」，讓使用者知情決定是否承擔風險前進。

## Exception Handling：例外情況處理

| 情境 | 處理方式 |
|---|---|
| 使用者一開始就要求「跳過探索，直接做方案」 | 依 [anti-patterns.md](anti-patterns.md#1-solution-first--跳過問題直接做方案) 提示 Solution-First 風險，但若使用者明確知情並堅持，尊重決定；仍建議至少產出一句輕量 Problem Statement 作為方案的錨點，並在後續文件標註「未經完整 Discover/Define」 |
| 時間/預算極度有限，無法做正式研究 | 採用「輕量 Discover」：桌面研究 + 既有資料 + 少量快速訪談或專家判斷；明確標註證據等級較弱，並記錄尚未驗證的假設供日後補驗證 |
| 使用者測試結果**推翻了問題假設本身**（例如發現使用者根本沒有這個痛點） | 退回 **Discover/Define** 重新定義問題，不要在錯誤的問題定義上硬做方案 |
| 使用者測試結果**否定選定方案**，但問題定義仍成立 | 退回 **Develop** 重新發想其他候選方案，不需重跑 Discover |
| 多個關係人對 Problem Statement 或優先順序意見不一致 | AI 不擅自拍板；列出分歧點與各自的證據支持，用 facilitator 角色協助收斂選項，最終裁決權交還使用者/關係人 |
| 使用者只給出極度模糊的請求（例如「幫我做個東西」） | 視為 Discover 起點，先問清楚「問題是什麼、使用者是誰」，不要自行假設專案類型 |
| 專案中途發現原本以為的「使用者」其實不是真正決策/使用主體 | 退回確認 User 層（見 principles.md 的 User→Problem→Solution），可能需要重新蒐集該真正使用者的證據 |

## User Interaction Rules：何時該問，何時可以直接做

**可直接執行（低風險、Evidence First 支撐，不需先問）：**
- 整理/盤點使用者已提供的資訊，指出資訊缺口
- 用既有資訊草擬 Journey Map、Persona、Problem Statement、HMW 清單的**草稿**（明確標註為草稿待確認，不當作定案）
- 產出 ideation 候選清單、方法選擇建議、驗證方案建議
- 執行只讀性質的資料盤點（讀專案內既有文件、規格、issue、程式碼以推斷情境）

**必須先問，不能假設（Minimal Assumption 的常見觸發點）：**
- 目標使用者是誰、他們的情境與目標
- 專案的成功定義/KPI 是什麼
- 資源與時間限制（能不能做正式研究、能做幾輪原型）
- 是否已有既有研究資料可用，避免重複蒐集
- 風險承受度：是否可以跳過某階段、用較弱證據前進
- 誰有最終決策權（Problem Statement、方案取捨的 sign-off owner）
- 使用者要求跳階段時，是否已知情並同意承擔風險

**提問方式的規則**：
- 用情境化提問，不要求使用者先懂 Double Diamond 術語才能回答（❌「你現在在 Discover 還是 Define？」 ✅「這個問題目前有沒有跟實際使用者聊過，或有沒有支援單/數據可以參考？」）
- 一次把同一決策所需的關鍵缺口問完，不要每問一句就中斷一次
- 若使用者不知道答案（例如不確定 KPI），協助提出合理選項讓使用者選，而不是無限追問或代替決定
