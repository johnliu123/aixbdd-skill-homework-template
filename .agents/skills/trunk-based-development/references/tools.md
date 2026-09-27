# 器：工具與 Workflow 階段對應

**通用原則：先偵測、再建議。** Stage 0 盤點時已經看過專案用什麼 Git 主機、CI、測試框架、有沒有 flag 系統。這裡列的是「這一類工具通常放在哪個階段、解決什麼問題」，不是強制推薦特定廠商；只有專案明顯缺乏對應能力、且該能力是完成當前任務的必要條件時，才主動建議並先徵詢使用者同意再引入新依賴。

| Workflow 階段 | 工具類別 | 例子 | 解決什麼問題 |
|---|---|---|---|
| Stage 0 現況盤點 | Git CLI / 主機 API | `git`、`gh`/`glab` CLI | 讀分支、PR、branch protection 現況 |
| Stage 2 分支/PR | Git 主機 | GitHub / GitLab / Bitbucket | 建 short-lived branch、開 PR、套 branch protection |
| Stage 3 開發（解耦） | Feature Flag 平台 | LaunchDarkly、Unleash、Flagsmith、FeatBit，或專案自建的 config-based flag | 把未完成功能安全合併進 trunk；支援漸進 rollout、瞬間關閉 |
| Stage 4 Commit | Commit 規範/檢查 | Conventional Commits 規範、專案內若已有 `git-conventional-commit` skill 就照它 | 讓 commit 訊息可被自動化（版本推導、changelog）解析 |
| Stage 5 同步 / 大型變更 | 無特定工具，是技巧 | Branch by Abstraction（見 [workflow.md](workflow.md#stage-3開發含解耦判斷decision-tree-2)） | 大範圍重構不需要長期分支 |
| Stage 6 Code Review | PR 審查介面 / Stacked PR 工具 | GitHub/GitLab 原生 PR、Graphite（stacked PR 專用） | 讓大功能拆成一串小 PR，各自可獨立快速審查 |
| Stage 7 Test/CI Gate | CI/CD Pipeline | GitHub Actions、GitLab CI、CircleCI、Jenkins | 每次變更自動建置＋測試，把關 trunk 品質 |
| Stage 8 Merge | Merge Queue / Merge Train | GitHub Merge Queue、GitLab Merge Train、Bitbucket Merge Queue、Graphite Merge Queue（stack-aware） | 團隊規模大、合併頻繁時，避免「各自測試都過、合在一起才壞」的語意衝突；用最新 trunk 狀態重新驗證後才真正合併 |
| Stage 9 Release | 版本/發布自動化 | Conventional Commits + `semantic-release` / `release-please` | 依 commit 類型自動推導語意化版本、產生 changelog，避免人工猜版號 |
| Stage 10 收尾 | Flag 生命週期管理 | 多數 Feature Flag 平台內建的「stale flag」偵測與告警 | 避免 flag 累積成技術債 |

## 選型判斷原則

- **團隊規模與合併頻率越高，越需要 Merge Queue**：個位數人數、一天合併幾次，靠 branch protection + CI 足夠；規模擴大到會出現「兩個 PR 各自綠燈但合併後紅燈」時，才需要導入 Merge Queue。
- **Feature Flag 平台 vs 自建**：短期、單一專案、flag 數量少 → 自建一個簡單的 config/環境變數判斷即可，不必馬上導入第三方平台；需要漸進 rollout、跨服務一致性、或多團隊共用時，才值得評估專用平台。
- **Stacked PR 工具是加分項，不是必需品**：GitHub/GitLab 原生已支援串接式 PR（下一個 PR 的 base 指向上一個 PR）；只有頻繁需要拆分大功能、且團隊已經很熟悉 TBD 節奏時，才需要 Graphite 之類的專用工具。
- **不要因為「這是業界標準做法」就引入新工具**：每引入一個新工具都是新的學習成本與維運負擔，違反 Minimal Assumption；先確認現有工具鏈能不能透過設定達成目的（例如 GitHub 原生 branch protection + required status checks，往往已經能滿足大部分 TBD 的把關需求）。
