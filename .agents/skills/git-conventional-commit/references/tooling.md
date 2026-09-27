# 器：工具生態與 Workflow 階段對應

> 這份文件回答「這個工具放在 pipeline 的哪一段？」。本 skill 的三個 Python 腳本
> （`analyze_git_changes.py` / `detect_project_convention.py` / `validate_commit_message.py`）
> 是本地、無依賴的替代品，讓 AI 不需要專案裝好 Node 工具鏈也能先做同等級的檢查。
> 若專案已經有下列工具，**優先尊重專案既有工具的結果**（Project-Aware 原則）。

## 工具在 Workflow 中的位置

```
撰寫程式碼
    │
    ▼
git add (staging)
    │
    ▼
┌─────────────────────┐
│ prepare-commit-msg   │ ← Commitizen（互動式問答產生訊息骨架）
│   git hook           │
└─────────────────────┘
    │
    ▼
git commit（訊息已產生）
    │
    ▼
┌─────────────────────┐
│ commit-msg           │ ← Commitlint（驗證格式，不合規則 reject commit）
│   git hook           │
└─────────────────────┘
    │
    ▼
commit 成功寫入歷史
    │
    ▼
git push → CI 觸發
    │
    ▼
┌─────────────────────┐
│ Semantic Release     │ ← 讀取 commit 歷史 → 決定版本號 → 產生 CHANGELOG → 發 tag/發布
└─────────────────────┘
```

Husky 是「黏著劑」：它負責把上面兩個 git hook（`prepare-commit-msg`、`commit-msg`）
可靠地安裝到每個開發者/CI 環境的 `.git/hooks/`。

---

## 1. Git（基礎層）

本 skill 直接操作的核心指令：

| 指令 | 用途 | 使用時機（對應 SOP 階段） |
|---|---|---|
| `git status --porcelain=v1` | 取得 staged/unstaged/untracked 檔案列表 | Phase 1 證據收集 |
| `git diff` | 未 staged 的變更 | Phase 1 |
| `git diff --staged` / `--cached` | 已 staged、即將被 commit 的變更 | Phase 1（最重要，commit 前必看） |
| `git diff --stat` | 只看變更統計，不看逐行內容（大 diff 先看這個） | Phase 1 |
| `git add <path>` | 精準加入整個檔案 | Phase 8 執行 staging |
| `git apply --cached <patch>` | 只 staged 某個檔案裡的部分 hunk（拆分同檔案內不同關注點時使用） | Phase 3/8 |
| `git commit -F <tempfile>` | 用檔案而非 `-m` 提交多行訊息，避免 shell 轉義/漏空行問題 | Phase 8（見下方「為什麼不用 -m」） |
| `git log -n N --pretty=format:%s` | 取得最近 commit 標題，判斷專案既有慣例 | Phase 0 |
| `git log -1 --stat` / `git show --stat` | Commit 後驗證 | Phase 9 |

### 為什麼不用 `git commit -m "多行訊息"`

多次 `-m` 或在 `-m` 裡塞入 `\n` 很容易漏掉 body 前的空行（規範要求的
`body-leading-blank`），且在 Windows PowerShell 下引號/轉義規則又和 bash 不同，
容易產生看似正確、實際格式錯誤的訊息。**本 skill 一律使用「寫入暫存檔 + `git commit -F <file>`」**
的方式提交，訊息內容完全由檔案內容決定，不受 shell 引號規則影響。

### Windows BOM 陷阱（實測會壞掉，務必注意）

在 Windows PowerShell 用 `Out-File -Encoding utf8` 寫暫存訊息檔，會在檔案開頭
自動加上一個 UTF-8 BOM（`\xEF\xBB\xBF`）。這個 BOM 會被當成訊息內容的第一個
字元,導致 `type`（例如 `feat`）前面多了一個看不見的字元，`git commit -F`
會把它原封不動寫進 commit——結果是一個「看起來正常但 type-enum 實際上比對
失敗」的訊息（`validate_commit_message.py` 會抓到並回報 `byte-order-mark`
warning，但那只是提醒,**實際檔案還是壞的,必須重寫檔案**）。

**正確寫法（依環境選一種,一律不要帶 BOM）**：

```powershell
# PowerShell 5.1（Windows 內建版本，沒有 utf8NoBOM 選項時用這個）
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))

# PowerShell 6+ / pwsh
$content | Out-File -Encoding utf8NoBOM -FilePath $path
```

```python
# Python（跨平台皆適用，本 skill 腳本內部一律這樣寫）
with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
```

```bash
# bash / POSIX shell
printf '%s\n' "$content" > "$path"
```

若使用 Cursor 內建的 `Write` 檔案工具寫暫存訊息檔（而不是透過 shell），一般不會有這個問題，
是更保險的選項。

---

## 2. Commitlint — 驗證層

- **定位**：在 `commit-msg` hook 執行，讀取剛打好的 commit message，依設定檔規則判斷
  是否合規；不合規會讓 `git commit` **直接失敗**（commit 不會被建立）。
- **設定檔**：`commitlint.config.js`（或 `.cjs`/`.mjs`/`.ts`/`.commitlintrc.*`），最常見設定：

```js
module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    // 範例：限制 scope 只能是這些值
    "scope-enum": [2, "always", ["api", "web", "infra", "deps"]],
  },
};
```

- **本 skill 的對應物**：`scripts/validate_commit_message.py` 實作了
  `@commitlint/config-conventional` 的規則子集（見 `references/spec.md` 第 8 節對照表），
  在專案**沒有裝 Node 工具鏈**時也能先擋掉明顯錯誤。若專案已經裝了真正的 commitlint，
  仍應以 commit 後 hook 的實際結果為最終標準。

## 3. Husky — Git Hook 管理層

- **定位**：不驗證任何東西，只是「把腳本可靠地掛到 git hooks 上」的工具，解決
  `.git/hooks/` 不會被 git clone 帶走、團隊每人要手動裝一次的問題。
- **常見 hook 對應**：
  - `.husky/commit-msg` → 呼叫 `commitlint --edit "$1"`
  - `.husky/prepare-commit-msg` → 呼叫 `cz --hook`（讓 Commitizen 介入）
- **判斷是否存在**：`detect_project_convention.py` 會檢查 `.husky/commit-msg` 是否存在，
  藉此判斷專案是否「強制」而非「建議」conventional commits。

## 4. Commitizen — 互動產生層

- **定位**：在**打字之前**介入，用互動問答（type → scope → subject → body → breaking?
  → issue 關聯）引導使用者組出合規訊息，是 prepare-commit-msg 階段的工具。
- **與本 skill 的關係**：Commitizen 解決的是「人類不知道怎麼組訊息」的問題；
  本 skill 解決的是**同一個問題但由 AI 自動判斷**，等同於「AI 扮演 Commitizen 的問答邏輯」
  ——SKILL.md 的 Decision Tree 本質上就是 Commitizen 互動問答的自動化版本。
- 安裝／設定指令（僅供了解，non-blocking，除非使用者要求才協助設定）：

```bash
npm install --save-dev commitizen @commitlint/cz-commitlint
# package.json
{ "config": { "commitizen": { "path": "@commitlint/cz-commitlint" } } }
npx husky add .husky/prepare-commit-msg 'exec < /dev/tty && npx cz --hook || true'
```

## 5. Semantic Release — 發布自動化層

- **定位**：在 CI 環境（push 到 main/release 分支後）執行，完全在 commit 完成**之後**：
  1. 讀取上次 release 以來的所有 commit。
  2. `@semantic-release/commit-analyzer` 依 type/breaking 判斷版本影響（PATCH/MINOR/MAJOR），
     取所有 commit 中**最高**的等級。
  3. `@semantic-release/release-notes-generator` 依 type 分組產生 CHANGELOG。
  4. 建立 git tag、發布套件、（可選）建立 GitHub Release。
- **與本 skill 的關係**：本 skill 產生的每一個 commit message 都是 semantic-release 的
  「輸入資料」。這是為什麼 SKILL.md 的 Type/Breaking Change 判斷樹格外重視「type 標錯 =
  版本號算錯」——這不是風格問題，是會實際影響到自動化發布結果的正確性問題。
- **預設 release 規則**：`fix`/`perf`/`revert` → patch；`feat` → minor；任何 commit
  帶 Breaking Change → major；其餘（`docs`/`style`/`test`/`build`/`ci`/`chore`）→ 不觸發 release。
- **已知陷阱**（來自 semantic-release 官方 issue 討論）：
  - `BREAKING CHANGE:` 寫在 subject 而不是 footer → 完全不會被偵測到。
  - 自訂 `releaseRules` 若把某個 type（如 `fix`）排在「breaking 規則」前面，該 type 的
    commit 即使帶 BREAKING CHANGE 也只會被判定成 patch——**breaking 規則必須放在自訂
    規則陣列最前面**（`{ breaking: true, release: "major" }`）。

## 6. 其他值得知道但非必裝的工具

| 工具 | 用途 | 何時建議提及 |
|---|---|---|
| `conventional-changelog-cli` | 只產生 changelog，不做完整發布流程 | 使用者只想要 changelog、不想要自動 publish |
| `cocogitto` (Rust) | 全功能的 conventional commits + release 工具，非 Node 生態 | 專案是 Rust/非 JS 專案時 |
| `release-please` (Google) | 用 PR-based 方式做 release（開一個「Release PR」累積 changelog，合併才真正發布） | 團隊偏好 review release 內容而非全自動發布 |
| `git-cliff` | 高度可自訂樣板的 changelog 產生器 | 需要自訂 changelog 格式（非標準 Angular 樣板） |

---

## 建議的最小安裝順序（若使用者要求「幫我在這個專案設定起來」）

1. `commitlint` + `@commitlint/config-conventional`（先有驗證，才有意義做其他事）
2. `husky`（把 commitlint 掛到 `commit-msg` hook，讓驗證真正生效）
3.（可選）`commitizen` + `@commitlint/cz-commitlint`（降低團隊手動記格式的負擔）
4.（可選，且需確認專案有在做版本發布）`semantic-release`

每一步都應該先確認使用者的套件管理工具（npm/yarn/pnpm/bun）與既有 `package.json`
內容，不要覆蓋既有 `scripts`/`husky` 設定——這屬於「高風險操作」，依 SKILL.md 的
Human Confirmation 規則，安裝/修改設定檔前都要先給使用者看diff 再執行。
