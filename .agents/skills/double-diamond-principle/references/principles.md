# 道：核心理念、目的、價值

## Double Diamond 是什麼

Double Diamond 是英國 [Design Council](https://www.designcouncil.org.uk/resources/the-double-diamond/) 於 2004 年提出、2019 年更新為「Framework for Innovation」的設計與創新流程模型。它把任何設計/創新專案拆成 **Discover → Define → Develop → Deliver** 四個階段，畫成兩顆鑽石：每顆鑽石都是先「發散（Diverge）」再「收斂（Converge）」。

- **第一顆鑽石（Discover + Define）= 問題空間（Problem Space）**：目的是找到「對」的問題。
- **第二顆鑽石（Develop + Deliver）= 解決方案空間（Solution Space）**：目的是找到「對」的解法。

```
   ╱╲                    ╱╲
  ╱  ╲                  ╱  ╲
 ╱    ╲________________╱    ╲________________
 ╲    ╱                ╲    ╱
  ╲  ╱                  ╲  ╱
   ╲╱                    ╲╱
DISCOVER   DEFINE      DEVELOP   DELIVER
 (發散)      (收斂)       (發散)     (收斂)

└────── 問題空間 Problem Space ──────┘└────── 解決方案空間 Solution Space ──────┘
```

Design Council 官方原文：「The first diamond helps people **understand, rather than simply assume**, what the problem is.」——這是整個模型存在的理由：多數失敗專案不是「方案做得不好」，而是「解錯了問題」。

2019 版（Framework for Innovation）把原本看起來線性的兩顆鑽石，改成**允許非線性、可迴圈**的版本：任何階段做研究/原型/測試時得到的新資訊，都可能把專案送回前面的階段重新探索。這是本 Skill「Iterative／可回頭」原則的官方依據，不是本 Skill 自創的彈性。

## 為什麼這樣做——核心價值

1. **Problem First**：先確認問題本身值得解，再談怎麼解。跳過問題空間直接進解決方案空間，是這個模型最常被違反、也最常導致專案失敗的地方。
2. **Diverge before Converge**：人（包括 AI）天生有第一個想法定錨（anchoring）的傾向。強制在收斂前先發散，是對抗「只想到一個方案就開始做」的機制設計，不是走流程的形式。
3. **證據優於假設**：兩個鑽石的每一次收斂，都必須有 Discover/Develop 階段蒐集到的證據支撐，不是團隊內部討論出來的共識或 AI 自己的推測。
4. **視覺化溝通**：Design Council 選擇用「兩顆鑽石」而非文字流程圖，是刻意讓沒有設計背景的人（stakeholder、工程師、業務）也能一眼理解「現在該發散還是收斂」。這也是本 Skill 要求 AI 產出結構化/視覺化資訊（表格、journey map、決策樹），而不是純敘述長文的原因。

## 四個核心設計原則（Design Council 2019, Framework for Innovation）

| 原則 | 官方定義 | 對 AI 執行的意涵 |
|---|---|---|
| **Put people first**（以人為本） | 從理解使用者的需求、能力與期望開始，不從內部假設開始 | 沒有使用者資料/回饋佐證前，不得憑空生成 persona、需求或「使用者應該想要」的判斷；缺資料就問，不猜（見 Minimal Assumption） |
| **Communicate visually & inclusively**（視覺化與包容性溝通） | 用視覺化方式幫助不同角色對問題與想法建立共同理解 | AI 的產出優先用表格、journey map、決策樹、結構化清單呈現，而非長篇散文；讓不懂 Double Diamond 的使用者也能看懂結論 |
| **Collaborate & co-create**（協作共創） | 與他人一起工作，並從其他人的做法中獲得啟發 | 關鍵決策點（Problem Statement 定案、方案取捨、是否進入下一階段）要邀請使用者/關係人確認，不由 AI 單方面拍板 |
| **Iterate, iterate, iterate**（持續迭代） | 儘早反覆測試想法，藉此抓錯誤、降風險、建立信心 | 沒有「一次做對」這件事；驗證結果推翻假設時，退回前一階段重新探索是正常流程，不是失敗（詳見 [rules.md](rules.md#exception-handling)） |

## User → Problem → Solution：三層焦點與順序

這是本 Skill 判斷「使用者是不是在解對問題」的核心心智模型，順序不可跳：

1. **User（使用者/情境）**：這個問題的當事人是誰？他們的情境、目標、限制是什麼？
2. **Problem（問題）**：使用者遇到的落差/痛點是什麼？有沒有證據支持這個落差真實存在、值得解？
3. **Solution（方案）**：在 1、2 都有答案之後，才輪到「怎麼解」。

任何時候使用者要求「直接給我方案」而 1、2 尚未確認，AI 要依 [anti-patterns.md](anti-patterns.md#1-solution-first--跳過問題直接做方案) 的規則處理：提示風險、給出最小限度的問題框架建議，但尊重使用者最終決定並記錄風險，不強迫使用者走完整流程。

## Project-Aware：專案規模決定嚴謹度，不是流程決定專案

Double Diamond 是「框架」不是「公式」；Design Council 自己也強調方法要依任務調整深度。本 Skill 依專案風險/不確定性分三級校準嚴謹度，避免「為流程而流程」：

| 規模 | 特徵 | Discover/Define 嚴謹度 | 範例 |
|---|---|---|---|
| **輕量** | 範疇明確、風險低、規格已知 | 幾乎跳過正式研究；用一句話確認 problem statement 即可進 Develop | 修一個明確的 bug、調整既有規格的文案 |
| **標準** | 單一功能/流程改善、有一定不確定性 | 輕量 Discover（既有資料 + 3–5 次訪談或支援單分析）+ 快速 Define | 新增一個功能、優化一個既有流程 |
| **完整** | 新產品/新服務/策略層級、高度不確定 | 完整四階段、多輪迭代、正式研究樣本 | 新產品方向、跨部門流程重設計、進入新市場 |

**如何判斷級別**：見 [workflow.md](workflow.md#stage-0-啟動---理解問題與專案背景) 的 Stage 0。判斷依據永遠是「這個決策錯了的代價有多大、現在的不確定性有多高」，不是「這個專案聽起來多重要」。
