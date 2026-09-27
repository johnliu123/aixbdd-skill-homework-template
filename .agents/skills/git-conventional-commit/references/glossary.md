# 關鍵字 / 術語速查表

集中列出本 Skill 會用到的核心術語一句話定義，方便快速查閱。完整規範細節見 [spec.md](spec.md)；本檔只做定義，不重複判斷樹。

## Commit 結構

| 術語 | 一句話定義 |
|---|---|
| **type** | Commit 訊息開頭的分類詞（`feat`/`fix`/`docs`...），MUST 存在，決定 semver 影響與 changelog 分組 |
| **scope** | 括號內描述受影響程式碼區塊的名詞，OPTIONAL，格式為小寫 kebab-case |
| **description** | `: ` 後的簡短摘要，祈使句、不加句號、不含 "and" |
| **body** | 說明 what/why（不寫 how）的自由格式段落，與 description 之間須空一行 |
| **footer** | body 之後的 `word-token: value` 結構化資訊（`BREAKING CHANGE`、`Refs`、`Co-authored-by`...） |
| **Breaking Change** | 消費者需修改自己程式碼/設定才能維持原行為的變更；用 `!` 和/或 `BREAKING CHANGE:` footer 標示 |

## 11 種 Type（Angular / commitlint 預設）

| Type | 一句話定義 |
|---|---|
| **feat** | 新增使用者可感知的功能，SemVer MINOR |
| **fix** | 修復不符合預期的行為，SemVer PATCH |
| **docs** | 只改文件（README、註解、docs/） |
| **style** | 純格式變更，邏輯完全不變 |
| **refactor** | 改變程式碼結構但外部行為不變、也不是修 bug |
| **perf** | 純粹提升效能，行為不變，SemVer PATCH |
| **test** | 新增/修改測試，不動產品程式碼 |
| **build** | 建置工具/打包設定/npm scripts |
| **ci** | CI/CD 設定（GitHub Actions、GitLab CI...） |
| **chore** | 不影響 src/test 的雜務 |
| **revert** | 撤銷先前的 commit |

## 判斷原則與生態系統

| 術語 | 一句話定義 |
|---|---|
| **Atomic Commit** | 每個 commit 應代表一個清楚、獨立、可還原的變更目的 |
| **RFC 2119 關鍵字** | 規範文件中 MUST/SHOULD/MAY 的強制程度用語，Conventional Commits 用它定義規則等級 |
| **SemVer（MAJOR/MINOR/PATCH）** | 語意化版本號；`fix`→PATCH、`feat`→MINOR、Breaking Change→MAJOR |
| **commitlint** | 檢查 commit 訊息是否符合規則（type-enum、subject-case...）的 lint 工具 |
| **semantic-release** | 依 commit type/breaking change 自動判斷版本號、產生 changelog、發布的工具 |
| **Conventional Commits** | 本 Skill 依循的規範本身（v1.0.0），只強制定義 `feat`/`fix`，其餘 type 為業界擴充慣例 |

## 何時該讀哪份文件

| 需求 | 讀這份 |
|---|---|
| 想快速查一個術語的定義 | 本檔（glossary.md） |
| 想逐字核對規範細節、type 定義表、commitlint 規則數值 | [spec.md](spec.md) |
| 想了解工具生態與 workflow 定位 | [tooling.md](tooling.md) |
| 想看常見誤用案例 | [anti-patterns.md](anti-patterns.md) |
| 想看完整實戰範例 | [examples.md](examples.md) |
