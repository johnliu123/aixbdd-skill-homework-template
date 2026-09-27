# 法：Conventional Commits 完整規範參考

> 這份文件是「規則書」。SKILL.md 已包含日常判斷所需的精簡版；當你需要逐字核對規範細節、
> 完整 type 定義表、或 commitlint 預設規則的確切數值時，才讀這份文件。

## 1. 官方格式（Conventional Commits v1.0.0）

```
<type>[(scope)][!]: <description>

[optional body]

[optional footer(s)]
```

來源：https://www.conventionalcommits.org/en/v1.0.0/

### 規範條文摘要（RFC 2119 關鍵字：MUST / SHOULD / MAY）

1. Commit **MUST** 以 type 開頭，後面接 OPTIONAL scope、OPTIONAL `!`、REQUIRED 的 `: `。
2. 新增功能 **MUST** 用 `feat`。
3. Bug 修復 **MUST** 用 `fix`。
4. Scope **MAY** 提供，**MUST** 是描述程式碼區塊的名詞，包在括號內，例如 `fix(parser):`。
5. Description **MUST** 緊接在 `: ` 之後，是變更的簡短摘要。
6. Body **MAY** 提供，**MUST** 與 description 之間空一行。
7. Body 為自由格式，**MAY** 有多個段落。
8. Footer **MAY** 有一個或多個，與 body 之間空一行；每個 footer **MUST** 是「word-token」+ `: ` 或 ` #` + 值（類似 git trailer 格式）。
9. Footer token **MUST** 用 `-` 取代空白（例如 `Acked-by`），例外是 `BREAKING CHANGE` 可以保留空格。
10. Footer 的值 **MAY** 包含空格與換行，直到下一個合法 footer token 出現才算結束。
11. Breaking change **MUST** 用 `!` 標示在 type/scope 後，或是以 footer 呈現。
12. 若用 footer 呈現，**MUST** 是大寫的 `BREAKING CHANGE:`，後面接空格與描述。
13. 若用 `!` 標示，`BREAKING CHANGE:` footer **MAY** 省略，此時 description 本身就要說明是什麼 breaking change。
14. `feat`、`fix` 以外的 type **MAY** 使用（例如 `docs:`）。
15. 除了 `BREAKING CHANGE` 必須大寫外，其他部分**不區分大小寫**（但實務上仍建議全部小寫，見下方 commitlint 規則）。
16. `BREAKING-CHANGE`（用連字號）與 `BREAKING CHANGE`（用空格）視為同義。

### 官方 FAQ 重點判斷原則

- **一個 commit 符合多種 type 時怎麼辦？** → 拆成多個 commit，不要硬選一個（這是 Atomic Commit 原則的官方依據）。
- **初期開發階段也要遵守嗎？** → 是，假設已經有人在用你的軟體。
- **Revert 怎麼處理？** → 規範不強制格式，建議：`revert: <說明>` + footer `Refs: <被還原的 commit SHA>`。
- **不是所有貢獻者都需要懂這個規範** → 可以用 squash merge，由維護者在合併時補上正確訊息。

---

## 2. Type 完整定義表（Angular Convention / commitlint 預設 11 種）

Conventional Commits 規範本身只定義 `feat` 和 `fix`；以下 11 種是業界最廣泛採用的
`@commitlint/config-conventional`（基於 Angular commit convention）擴充列表：

| Type | 何時使用 | SemVer 影響（semantic-release 預設） | 常見誤用 |
|---|---|---|---|
| `feat` | 新增使用者可感知的功能/能力 | **MINOR** | 把內部工具函式新增誤標成 feat |
| `fix` | 修復錯誤行為 | **PATCH** | 把「順手改進」也算成 fix |
| `docs` | 只改文件（README、註解、API 文件） | 無 | 文件變更混在程式碼 commit 裡 |
| `style` | 純格式（空白、分號、排版），**不影響邏輯** | 無 | 格式修改混雜邏輯改動 |
| `refactor` | 重構程式碼結構，**外部行為不變**、也不是修 bug | 無 | 把順便修的 bug 也歸類成 refactor（見下方判斷標準） |
| `perf` | 提升效能，行為不變 | **PATCH** | 效能改動同時改了邏輯卻沒說明 |
| `test` | 新增/修改測試，不改動產品程式碼 | 無 | — |
| `build` | 建置系統、打包工具、依賴管理設定（webpack、npm scripts） | 無 | 與 `ci` 混用 |
| `ci` | CI/CD 設定（GitHub Actions、GitLab CI、Jenkinsfile） | 無 | 與 `build` 混用 |
| `chore` | 不影響 src 或 test 的雜務（repo housekeeping） | 無 | **危險**：把有破壞性的依賴升級標成 chore，會讓 semantic-release 完全不發版（見 anti-patterns.md） |
| `revert` | 撤銷先前的 commit | 依情況（見下） | 沒有附上被撤銷的 SHA |

> 規範允許你自訂 type（例如 `hotfix`、`security`），但務必寫進 `CONTRIBUTING.md` 並設定
> commitlint 的 `type-enum`，否則工具會直接判定失敗或忽略。

### `fix` vs `refactor` 判斷標準（業界最容易搞混的一組）

> 判斷依據：**這個改動是否修正了「不符合預期的行為」？**
> - 是 → `fix`（即使你是在重構過程中「順便」修好的，也要老實標 `fix`）。
> - 否，純粹改變程式碼結構、命名、拆分函式，外部可觀察行為完全不變 → `refactor`。

把 bug fix 藏在 `refactor` 裡會讓 changelog 誤導使用者，也會讓該修的 PATCH 版本消失。

### `feat` vs `fix` 判斷標準

> 判斷依據：**這個能力/行為，在此之前「本來就該存在但缺失/錯誤」，還是「全新引入」？**
> - 缺失的預期行為被補上 → `fix`。
> - 從未存在過的新能力 → `feat`。

---

## 3. Scope 判斷標準

- Scope **MUST** 是名詞，描述受影響的程式碼區塊，格式建議 `kebab-case`（`@commitlint/config-conventional`
  預設 `scope-case: lower-case`，帶空格或大寫會被 lint 打掉）。
- **何時該加 scope**：變更集中在單一元件/模組時。
- **何時該省略 scope**：
  - 專案本身很小、沒有明顯的模組劃分。
  - 變更是跨領域、影響多個不相關模組（此時應優先考慮「是否該拆分 commit」而不是硬套一個 scope）。
  - `build`、`ci`、`chore(release)` 等專案層級的雜務，scope 常常是多餘的噪音。
- **一致性比種類更重要**：一旦專案決定 `auth` 代表登入相關模組，就不要再用 `authentication` 或 `login`
  表示同一件事——不一致的 scope 會讓 changelog 分組失效、`git log --grep` 也抓不到。
- Scope 字典應該對應到專案的目錄/模組結構（例如 `modes/` 目錄 → scope `modes`）。

---

## 4. Description（描述）規則

- **MUST** 緊接 `: ` 後，簡短摘要變更內容。
- 語氣：**祈使句/命令式**（imperative mood）——`add`、`fix`、`remove`，而不是 `added`、`fixes`、`removing`。
  判斷技巧：讀起來要能接在「If applied, this commit will ___」後面。
- 大小寫：commitlint 預設禁止 `sentence-case`、`start-case`、`PascalCase`、`UPPERCASE`，允許
  `lower-case` 或 `camelCase`。
- 結尾：**不加句號**。
- 長度：commitlint 預設 header 總長度（含 type/scope/`!`/description）上限 **100 字元**；
  傳統 git 工具建議上限是 **72 字元**（超過在 `git log --oneline` 等地方會被截斷）。
- **禁止空泛描述**：`fixed bug`、`update`、`wip`、`changes`、`stuff` 這類詞完全沒有資訊量，
  diff 本身就能告訴讀者「有改動」，description 該說明的是「改動的意義」。
- **禁止列檔名**：`update user.rb and helper.js` 這種寫法是重複 `git show` 已經給的資訊。
- **描述中出現 "and"** 幾乎都是「該拆成兩個 commit」的訊號。

---

## 5. Body 規則

- **MUST** 與 description 之間空一行（`body-leading-blank`）。
- 內容應說明 **what（做了什麼）和 why（為什麼）**，不是 **how（怎麼做）**——how 應該從程式碼本身看得出來。
- **何時可以省略 body**：變更本身自我解釋、瑣碎（例如 `chore(deps): bump lodash to 4.17.21`、
  單純 typo 修正的 `docs`）。
- **何時必須有 body**：
  - 修的是不明顯的 bug（為什麼會發生、為什麼這樣修）。
  - `feat` 涉及非顯而易見的設計決策。
  - `refactor` 改變了核心結構。
  - 任何 Breaking Change（見下）。
- commitlint 預設 `body-max-line-length`：每行 **100 字元**，但**包含 URL 的行不受此限**。

---

## 6. Footer 規則

- **MUST** 與 body 之間空一行（`footer-leading-blank`）。
- Footer token **MUST** 用 `word-token: value` 或 `word-token #value` 格式，token 內以 `-`
  取代空白（例外：`BREAKING CHANGE`）。
- 常見 footer：
  - `BREAKING CHANGE: <description>` 或 `BREAKING-CHANGE: <description>`
  - `Closes #123` / `Fixes #123` / `Refs #123`（issue/PR 關聯）
  - `Co-authored-by: Name <email>`（多人協作署名）
  - `Reviewed-by: Name`
  - `DEPRECATED: <description>`（非官方但廣泛採用，用於預告即將移除的 API，格式同 BREAKING CHANGE）
- 每行上限同樣是 **100 字元**（URL 例外）。

---

## 7. Breaking Change 判斷標準與雙重標示

### 何謂 Breaking Change？

> **判斷依據**：使用這段程式碼/服務/設定的「消費者」（可能是別的團隊、別的程式、你自己半年後的自己）
> 是否需要**修改他們的程式碼、設定或呼叫方式**才能維持原本的行為？

具體訊號：
- 公開 API 的函式簽名、回傳型別、HTTP contract 改變。
- 移除或改名任何 export/公開符號、CLI 參數、設定鍵值。
- 改變預設值、預設行為。
- 資料庫 schema 變更且需要既有資料做遷移才能相容。
- 依賴套件的 major 版本下限提升（例如「不再支援 Node 16」）。

### 雙重標示規則（規範第 11–13 條）

| 標示方式 | 何時用 | 範例 |
|---|---|---|
| 只用 `!` | 描述本身已經足以說明是什麼 breaking change | `feat!: drop support for Node 16` |
| 只用 footer | 需要較長篇幅解釋遷移方式 | `feat: switch to native fetch`<br>`BREAKING CHANGE: Node 16 no longer supported. Upgrade to 18.` |
| 兩者都用 | Breaking change 需要進一步解釋，且想在標題就標明 | `feat(api)!: drop support for Node 16`<br><br>`BREAKING CHANGE: use fetch features unavailable in Node 16.` |

**重要**：
- `BREAKING CHANGE:` **必須在 footer**，不是 subject 或單獨一行放在最上面——放錯位置，
  semantic-release 等工具**完全偵測不到**，不會觸發 MAJOR release（這是實務上最常見的工具誤用陷阱）。
- Token 必須**完全大寫**（`BREAKING CHANGE`），`Breaking change` 或 `breaking change` 都不會被工具識別。
- **任何 type 都可能是 breaking change**，不是只有 `feat`。但如果 type 是 `chore`/`style`/`docs`/
  `test`/`build`/`ci`，semantic-release 預設規則仍會判斷「這個 type 不觸發 release」，即使有
  BREAKING CHANGE footer 也可能被忽略（除非專案自訂了 releaseRules 讓 breaking 規則優先）——
  這是 anti-patterns.md 中「把破壞性依賴升級標成 chore」案例的根本原因。
- 建議：**一個 commit 只描述一個 breaking change**，多個 breaking change 應拆成多個 commit，
  保持 changelog 清晰。

---

## 8. commitlint `@commitlint/config-conventional` 完整預設規則表

這是業界最常用的 lint 設定（多數 CI pipeline 用它擋不合規的 commit）：

| 規則 | 等級 | 內容 |
|---|---|---|
| `type-enum` | error | 限定 11 種 type（見上表） |
| `type-case` | error | type 必須小寫 |
| `type-empty` | error | type 不可為空 |
| `subject-empty` | error | description 不可為空 |
| `subject-full-stop` | error | description 結尾不可有 `.` |
| `subject-case` | error | 禁止 `sentence-case`、`start-case`、`pascal-case`、`upper-case` |
| `header-max-length` | error | header 總長 ≤ 100 |
| `header-trim` | error | header 不可有前後空白 |
| `body-leading-blank` | warning | body 前必須空一行 |
| `body-max-line-length` | error | body 每行 ≤ 100（URL 例外） |
| `footer-leading-blank` | warning | footer 前必須空一行 |
| `footer-max-line-length` | error | footer 每行 ≤ 100（URL 例外） |
| `scope-enum` | 未預設值（空陣列 = 不限制） | 若專案設定了允許清單，scope 必須在清單中；沒設定則不檢查 |
| `scope-case` | — | 未在預設清單但社群慣例是 `lower-case` |

> 完整規則參考：https://commitlint.js.org/reference/rules

`validate_commit_message.py` 已經把上述規則（加上幾條本 skill 專屬的語義檢查）用純 Python
regex 實作，不需要安裝 Node/commitlint 就能先做一次本地驗證。

---

## 9. 道：與 SemVer / Changelog / Release / CI-CD 的關係

理解「為什麼」比死記規則更重要，這是判斷力的根本：

```
commit type/breaking  ──►  commit-analyzer 判斷版本影響  ──►  下一個版本號 (SemVer)
        │                                                        │
        ▼                                                        ▼
release-notes-generator 依 type 分組  ──►  CHANGELOG.md      git tag vX.Y.Z ──► CI/CD 觸發發布
```

- **SemVer 對應**：`fix`/`perf` → PATCH；`feat` → MINOR；任何帶 Breaking Change 的 commit → MAJOR。
  這個對應不是巧合，是 Conventional Commits 存在的**核心理由**——commit type 本質上就是在
  「即時聲明這次變更對消費者的相容性影響」。
- **Changelog 自動生成**：因為 type 和 scope 是結構化資料，工具（`conventional-changelog`、
  `release-notes-generator`）可以直接依 type 分組（Features / Bug Fixes / Breaking Changes...），
  不需要人工在 release 前手動回顧所有 commit。
- **Release 自動化**：`semantic-release` 讀取自上次 release 以來的所有 commit，取「影響最大」的
  那個等級（MAJOR > MINOR > PATCH）作為下一版本號，全自動 tag + publish，**完全移除「這次該發
  几.几.几」的人工判斷與爭論**。
- **CI/CD 串接**：commit message 本身變成一種「機器可讀的意圖宣告」，可以觸發不同的 pipeline
  行為（例如 `docs:` commit 跳過完整測試矩陣、`feat:`/`fix:` 才觸發部署）。
- **最終價值**：Conventional Commits 不是為了「格式規範」本身，而是把「這次修改的本質」這件
  本來只存在工程師腦中的資訊，**外部化成結構化、可自動化處理的資料**。一旦你把 commit
  message 當成「給機器和未來的自己的 API」，很多判斷標準（該不該加 body、該不該拆 commit、
  該標哪個 type）就會變得直覺——問自己：「如果只有這行 header 被拿去自動生成 changelog，
  讀者會不會誤解、或錯過重要資訊？」
