# 法：核心規範與判斷標準

本文件是執行層的規則書。每一節都給「判斷標準」而不是死板規定，因為 Project-Aware 原則要求先看證據再套用。所有規則預設 trunk 已在 Stage 0 確認為 `main` 或 `master`（以實際偵測結果為準，不要假設）。

## Branch 策略判斷規則

**預設立場**：trunk 是唯一的整合中心；長期分支（`develop`、長期 `feature/*`）是例外，不是常態。

判斷用哪種模式，依證據決定：

| 證據 | 建議策略 |
|---|---|
| 團隊極小（1–2 人）、目前 commit 歷史顯示常態直推 trunk、無強制 PR 規則 | 允許直推 trunk，但每次 push 前本地測試必須綠燈 |
| 團隊中等以上、或存在 branch protection、或歷史顯示都走 PR | Short-Lived Branch + PR，PR 只是「審查用的臨時分支」，不是開發用的長期空間 |
| Git log 顯示已存在 `develop`/`release/*`/`hotfix/*` 且有規律使用 | 專案目前是 Gitflow 風格。**不要單方面強制搬遷**；先評估遷移成本與必要性（見 [anti-patterns.md](anti-patterns.md)），提出漸進式方案並徵詢使用者，而不是自行大改 |
| 找不到任何慣例線索（新專案/首次協作） | 詢問使用者發布節奏與團隊規模，再套用上方對應策略 |

**硬性原則，不因專案風格而例外**：
- 一條 short-lived branch 只服務一個人（或一對配對）；不要把它當團隊共用的長期功能空間。
- 分支只用來做 review 和 CI gate，不要在分支上做 artifact 建置/發布——那是 trunk 或 release branch 的責任。
- 不要把「部分完成」的分支合併到另一個開發者的分支，也不要把它合併到除了 trunk 之外的任何地方；唯一合法的合併方向是「trunk → 分支（同步用）」與「分支 → trunk（收尾用）」。

## Short-Lived Branch 判斷標準

- **軟目標**：數小時內完成並合併。
- **硬上限**：2 天。超過 2 天要視為風險訊號，不是「還可以接受」。
- 用 Stage 0 的 `git branch -a --sort=-committerdate` 搭配 `git log <branch> --since=...` 或分支第一個 commit 的時間戳，計算分支年齡。
- **超時後的處理選項**（依現況選一個，不要只是繼續等）：
  1. 拆成更小的 PR（單一 PR diff 建議 < ~400 行，超過就考慮拆分或 stacked PR）。
  2. 今天內配對/專注完成，把干擾任務先擋掉。
  3. 用 Feature Flag 把已完成、安全的部分先合併回 trunk，未完成部分留在新的、範圍更小的分支繼續。
  4. 如果是大範圍重構造成的，改用 Branch by Abstraction 在 trunk 上分小步進行，取消原本的長期分支。
- 整個 repo 的**活躍分支數**（不含 trunk）以 ≤ 3 為健康基準（DORA 高效能團隊門檻）；明顯超過時，在 Validation / 健康度檢查中提出。

## Commit 規則

- 小、原子化、能獨立建置的 commit；避免「一次性巨大 commit」。
- Commit 前本機先跑快速測試/lint，確保不會把明知會壞的狀態放進歷史。
- 訊息格式：先看專案是否已有慣例（是否用 Conventional Commits、是否安裝了 `git-conventional-commit` 這類 skill）；有就照專案慣例，沒有就建議 Conventional Commits（`feat:`/`fix:`/`chore:`...），因為它可以直接驅動語意化版本與 changelog 自動化（見 [tools.md](tools.md)），但不要在使用者沒同意前就強制變更既有慣例。
- 允許本機階段有多個小 commit 之後再 squash——但**squash 的時機是合併進 trunk 那一刻**，不要在推送到共享分支後再對已被他人看到的歷史做互動式 rebase（見 Git 操作規則的風險清單）。

## Integration（合併回 Trunk）規則

- **至少每天一次**把工作合併回 trunk，這是 DORA 定義 TBD 的核心量化指標，不是軟性建議。
- 合併前，先把最新 trunk 同步進分支（`fetch` + `merge`/`rebase`），確保不是在測試一個已經過時的基準；這一步失敗或衝突多，本身就是「分支太老」的訊號。
- **不要有 code freeze 或整合階段**；如果團隊習慣「衝刺尾端才整合」，那就是要在 Validation / Anti-pattern 中點出的反模式。
- 合併策略怎麼選：
  - **Squash merge**：預設選項，小 PR、想保持 trunk 歷史乾淨時用。
  - **Merge commit**：分支內本身就是有意義的多個原子 commit、想保留脈絡時用。
  - **Rebase merge**：想要線性歷史又保留每個 commit 細節時用，但只對「自己、未被他人 fork」的分支做 rebase。
  - 不論哪種，都不要對 trunk 本身做 rebase 改寫歷史。
- 團隊規模大、合併頻繁時，用 Merge Queue / Merge Train（見 [tools.md](tools.md)）避免「兩個 PR 各自測試都過，但合在一起就壞」的語意衝突（merge skew）。

## Code Review 規則

- 目標是**同步或近同步審查**：PR 開出後，審查應該在同一個工作日、甚至幾小時內完成，不要丟進非同步佇列後就去做別的事——DORA 明確指出，審查延遲是「小批次工作」最常見的殺手，審查越慢，團隊越傾向累積大批次。
- 自動化檢查（測試、lint、coverage）先過，才進入人工審查；人工審查應該專注在邏輯、設計、可維護性，而不是重複自動化已經能抓到的問題。
- PR 大小：抓 ~400 行 diff 當作警戒線，超過就建議拆分或改用 stacked PR（下一個 PR 疊在這個 PR 上面，各自可獨立審查）。
- 若團隊本來就採 pair programming，代表 code 已經被「即時審查」過一次，可視專案慣例決定是否還需要額外審查——但這屬於團隊規範判斷，不確定時要問。

## Testing / CI Gate 規則

- Trunk 上每個 commit 都必須通過自動化測試才算合格；用 branch protection（要求 CI 綠燈才能合併）把這件事變成強制，而不是靠人記得。
- 快速測試（unit/fast integration）目標在 review/merge 前就跑完並回饋，理想上幾分鐘內出結果；太慢（例如 2 小時）會逼工程師「先合併再說」或讓分支變相變長，TBD 就名存實亡。
- **Trunk 變紅（build broken）是最高優先事件**：不能放著不管。處理順序：立刻修（fix-forward）> 立刻 revert 造成問題的 commit（若是自己的 commit 可直接做；若是別人的，先確認，見 Git 操作規則）> 絕對不是「等一下有空再看」。
- Flaky test 要被隔離（quarantine）並排入修復或移除，不能長期忽略——長期忽略會侵蝕整個團隊對 CI 結果的信任，最終導致大家又開始靠人工把關、走回長期分支。

## Feature Flag / 解耦技術判斷框架

先判斷需求屬於哪一種，再選對應技術，不要每件事都無差別套 Feature Flag：

| 情境特徵 | 建議技術 |
|---|---|
| 開發會跨過 short-lived branch 的合理期限（>1 天），且會動到使用者可觸及的介面/行為 | **Feature Flag（Release Toggle）**：合併時 flag 關閉，功能對使用者不可見，完成後再開 |
| 大範圍內部重構/替換一個模組或函式庫，呼叫端很多，使用者無感 | **Branch by Abstraction**：先引入抽象介面，逐步把呼叫端導到介面，新實作在介面後面小步建置，最後一次性切換，完成後刪掉舊實作與抽象層 |
| 後端演算法/資料源替換，需要拿正式流量驗證但不想影響使用者 | **Dark Launch / 並行執行（Parallel Run）**：新路徑在背景跑，比對結果但不影響回應 |
| 變更範圍小、能在 short-lived branch 期限內做完並直接整合 | 不需要任何解耦技術，直接走一般 Integration 流程 |

**Feature Flag 治理規則（避免變成技術債）**：
- 幫每個 flag 標明**類型**：Release Toggle（短命，功能上線後就該刪）vs. Experiment/Ops/Permission Toggle（可能長期存在）。混用會導致該刪的 flag 永遠留著。
- 每個 flag 要有**名稱慣例**（例如 `FF_NEW_CHECKOUT`）、**owner**、**預期存活期限**；設一個「過期警戒天數」（常見基準 40 天），超過就該提出清理。
- 「移除 flag」要算進這個功能的 Definition of Done，不是上線後就算完成——上線只是完成一半。
- 測試要覆蓋 flag 開/關兩條路徑，不能只測其中一條。
- 資料庫層變更若跟 flag 綁在一起要特別小心：flag 關閉能不能真的安全回滾，取決於資料是否相容；不相容時要用 Exception Handling 中的 Expand/Contract 模式分階段處理，不能假設「flag 關掉=完全復原」。

## Release 規則

| 情境 | 建議策略 |
|---|---|
| 持續部署、能在幾分鐘內 fix-forward 或回滾 | **直接從 trunk 發布**。出問題就修好再往前推，不做回退式 rollback |
| 需要同時維護多個正式版本、行動 App 上架審核週期、法規要求的 hardening 驗證 | **就地切一條 release branch**（可以不是 trunk 最新的那個 commit，而是回溯到一個「已知良好」的 commit 點）。release branch **絕不合併回 trunk**；修 bug 一律先進 trunk，再 cherry-pick 到 release branch |
| 已用 Feature Flag 管理功能可見性 | 「發布」＝逐步調高 flag 的 rollout 比例，不是重新部署一次程式碼；部署與發布徹底解耦 |

版本號建議：若專案顯示對 changelog/版本自動化有需求（存在 `CHANGELOG.md`、`package.json` 之類），建議搭配 Conventional Commits + `semantic-release`/`release-please` 之類工具自動推導版本，而不是人工猜版號；但引入新工具前先確認使用者同意（見 Minimal Assumption）。

## Validation Rules（TBD 健康度檢查）

隨時可執行，也建議在每次 Stage 0 盤點時順便跑一次，用證據打分而不是印象：

| 檢查項 | 健康基準（DORA） | 怎麼量 |
|---|---|---|
| 活躍分支數 | ≤ 3 | `git branch -a` 排除已合併/已刪除的 |
| 分支存活時間 | 全部 < 1–2 天 | 各分支起始 commit 時間 vs 現在 |
| 每日整合率 | 每個活躍分支每天至少合併回 trunk 一次 | 比對分支最後一次合併回 trunk 的時間 |
| Code freeze / 整合階段 | 不存在 | 查是否有「凍結期」「stabilization sprint」之類慣例或文件 |
| CI 綠燈率 | trunk 上的 build 大多數時間是綠的 | 看 CI 歷史（若可取得） |
| Feature Flag 衛生 | 每個 flag 有 owner、有到期預期、沒有明顯超期未清理的 | 掃描程式碼中的 flag 判斷點與其存在時間 |

任一項明顯不合格，對應到 [anti-patterns.md](anti-patterns.md) 找具體改善建議，而不是只回報「不合格」。

## Exception Handling（例外處理）

| 例外情境 | 允許的偏離 | 護欄 |
|---|---|---|
| 生產環境緊急 Hotfix | 可以從既有 release tag/branch 切出修復，不走一般 short-lived branch 流程 | 修復完成後必須把同一個修復也送回 trunk（cherry-pick 或重新實作），不能只存在於 release branch |
| 大型資料庫 schema 變更 | 可以分成多個 PR/多個階段落地 | 一律用 **Expand → Migrate → Contract**：先新增相容欄位/結構、雙寫或雙讀驗證、確認穩定後才移除舊結構；禁止一次性 big-bang 變更，也禁止假設 Feature Flag 關閉能無痛復原資料 |
| 法規/合約強制的長週期 release train | 可以維持 release branch 例行存在 | Release branch 依然遵守「絕不合併回 trunk、修復先進 trunk 再 cherry-pick」的單向規則，避免退化成 Gitflow 式雙向汙染 |
| Trunk 短暫變紅、正在修 | 允許短暫不可發布狀態 | 必須有明確的「Build Cop / 負責人」與時間界線，且团队要能看到目前 trunk 是紅的（可見性），不能悄悄放著；修好前不接受新的合併堆疊上去 |
| 完全沒有測試/CI 安全網的既有專案 | 可以先不要求高頻直推 trunk | 先協助補齊最小可信的自動化測試與 CI，再逐步提高整合頻率；提前導入高頻合併只會更快把壞狀態擴散出去 |

## User Interaction Rules（何時問、何時做）

**必須先問，不能假設**：release 節奏與部署環境未知、是否已有 feature flag 系統未知、變更牽涉其他人正在進行中的工作且所有權不明確、變更涉及資料庫/金流/權限等高風險且沒有既有規範、專案已有 Gitflow 慣例但使用者要求「改用 TBD」卻沒說明遷移範圍與時程容忍度。

**可以直接做**：所有唯讀盤點指令、依既有慣例建立短命分支、本機小步 commit 與測試、push 自己的新分支、開 PR、依偵測到的慣例產生 commit 訊息。

**做之前必須明確確認一次（列在 Git 操作規則）**：任何會改寫共享歷史、刪除他人工作、跳過驗證關卡、或影響 production 使用者可見性的操作。

## Git 操作規則

**分類原則**：唯讀/可逆/範圍僅限自己剛建立的本機狀態 → 可自動執行；會影響共享狀態、他人工作、production 可見性、或不可逆 → 一律先說明風險並取得確認，即使技術上完全可行。

**可自動執行**：
```bash
git status / git diff / git log / git branch -a
git fetch && git pull            # 同步 trunk
git checkout -b <new-short-lived-branch>   # 從最新 trunk 切出
git add / git commit             # 本機小步提交
git push origin <own-new-branch> # 推送自己新建的分支
```

**執行前必須先確認**：
```bash
git push --force / --force-with-lease   # 尤其在共享分支上
git push <trunk>                         # 略過 PR/CI 直接推 trunk（若專案要求走 PR）
git rebase -i                            # 對已推送、他人可能已看到的分支做互動式改寫
git branch -D <branch>                   # 分支上有未合併的獨有 commit 時
git reset --hard                         # 用在非「剛建立且只存在本機」的分支上
git revert <commit>                      # 若是別人的 commit（自己的 commit 可自動 revert）
```
以及任何：合併未過 CI 或被跳過檢查的 PR、刪除/切換 production 的 feature flag、切出或刪除 release branch、解決衝突時動到超出當前任務範圍的程式碼。

**理由**：這些操作的共同點是「一旦做了，別人會直接受影響，而且不容易悄悄復原」——完全符合 Evidence First + Minimal Assumption 的精神：技術上能做，不代表現在該自己決定做。
