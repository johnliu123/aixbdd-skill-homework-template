# 常見錯誤與 Anti-patterns（含真實案例）

> SKILL.md 只列了濃縮版清單。這裡是每一條的完整案例、為什麼有害、以及正確寫法。
> `validate_commit_message.py` 已經能自動抓出大部分「格式類」問題；這份文件補上
> 格式正確但「語義/判斷」仍然錯誤的案例，這些是驗證腳本抓不到、只能靠判斷力避免的。

## 1. 格式合規，但完全沒資訊量（「空洞的合規」）

```
❌ feat: update stuff
❌ fix: bug fix
❌ chore: changes
```

這些**通過** commitlint 的所有規則檢查（type 合法、大小寫對、沒句號），但對讀者
（包括六個月後的你自己）沒有任何價值。診斷技巧：把 description 讀成
「If applied, this commit will ___」，如果讀完還是不知道改了什麼 → 重寫。

```
✅ fix(auth): reject expired refresh tokens instead of silently renewing them
✅ chore(deps): bump lodash from 4.17.15 to 4.17.21 to patch CVE-2021-23337
```

## 2. 把 Breaking Change 偽裝成 chore（**最危險**的一類）

```
❌ chore: upgrade auth library to v2.0.0
```

實際上這個升級改變了 config key 名稱，是不折不扣的 breaking change。問題：
`chore` 不在 semantic-release 預設會觸發 release 的 type 列表中——**即使**你在
footer 寫了 `BREAKING CHANGE:`，很多預設規則設定下這個 commit 仍然「安靜地」
不觸發 MAJOR release，下游使用者升級後直接爆炸，且沒有 changelog 警告。

```
✅ feat(auth)!: upgrade auth library to v2.0.0

BREAKING CHANGE: config key `authSecret` renamed to `auth.secret`.
Update your config files before upgrading.
```

`validate_commit_message.py` 會對「`chore`/`style`/`docs`/`test`/`build`/`ci` +
BREAKING CHANGE」組合發出 warning，但最終判斷仍需要人/AI 確認這個 type 選擇是否正確。

## 3. `BREAKING CHANGE` 位置放錯

```
❌ git commit -m "BREAKING CHANGE: removed the old endpoint"
```

這整段只有一行，`BREAKING CHANGE:` 被當成 subject/description 的一部分，不是
footer——大多數工具（包括 semantic-release）**完全偵測不到**，因為規範要求它
必須在 body 之後、以空行分隔的 footer 區塊。

```
✅ feat!: remove the deprecated /v1/login endpoint

BREAKING CHANGE: removed the old endpoint. Use /v2/login instead.
```

## 4. 用 "and" 掩蓋了應該拆分的 commit

```
❌ feat: add user authentication and fix logging format
```

一句話出現 "and" 幾乎必然代表混入了兩個不相關的關注點。拆開後兩個 commit
各自可以獨立 revert、獨立 review：

```
✅ feat(auth): add JWT-based user authentication
✅ fix(logging): correct timestamp format in log output
```

## 5. `refactor` 藏 bug fix

```
❌ refactor: clean up user validation logic
```

如果這次「清理」順便修掉了一個「email 格式檢查漏了某種情況」的 bug，這就是
`fix`，不是 `refactor`。把 bug fix 藏在 refactor 裡，會讓該有的 PATCH 版本消失，
也誤導了 changelog 讀者「這只是內部整理，不影響行為」。

```
✅ fix(validation): reject emails missing the domain part
```
（如果同一組改動裡**也**包含了純粹的、不影響行為的結構調整，考慮是否該拆成
`refactor` + `fix` 兩個 commit——見 SKILL.md 的 Atomic Commit 判斷樹。）

## 6. 過度分割的 scope

```
❌ fix(src/utils/helpers/string/trim): fix typo
```

Scope 深入到檔案路徑層級，不是「描述程式碼區塊」而是「複製檔案路徑」，噪音大於
資訊量。應該用專案的模組層級詞彙：

```
✅ fix(utils): trim leading whitespace in slug generator
```

## 7. Scope 詞彙不一致

同一個「登入」相關模組，有些 commit 用 `auth`，有些用 `authentication`，有些用
`login`——結果是 changelog 分組失效，`git log --grep 'auth'` 也抓不全。**一致性
比選哪個詞更重要**：一旦專案（或 `detect_project_convention.py` 偵測到的歷史）
已經確立某個詞彙，後續一律沿用同一個詞，不要自創新詞。

## 8. 用 `git commit -m` 塞多行訊息漏掉空行

```bash
❌ git commit -m "feat: add x
BREAKING CHANGE: y"
```

這樣寫出來的訊息在 body/footer 之前**沒有空行**，會違反
`body-leading-blank`/`footer-leading-blank`，某些 parser 甚至會把整段吃成一行
description。**本 skill 一律用暫存檔 + `git commit -F <file>` 提交**，見
`references/tooling.md` 第 1 節。

## 9. 盲目 `git add -A` / `git add .`

不是 Conventional Commits 規範本身的規則，但直接違反 Atomic Commit 原則：如果
工作區裡同時有「這次要 commit 的變更」和「還在進行中、不該入庫的變更」，盲目
`add -A` 會把兩者混進同一個 commit，之後也無法用格式判斷回頭補救。應該精準
`git add <path>` 或用 hunk-level 的 `git apply --cached` 只加入目標範圍。

## 10. 把 dependency lockfile 更新拆成獨立 commit

```
❌ commit 1: feat: add pagination
❌ commit 2: chore: update package-lock.json
```

Lockfile 的變化是「新增 pagination 需要的依賴」造成的**直接結果**，兩者是同一個
邏輯改動,拆開後 commit 2 若被單獨 revert，commit 1 會處於依賴不一致的壞狀態。

```
✅ feat(pagination): add cursor-based pagination to /orders endpoint
   （package.json + package-lock.json 一起入這個 commit）
```

## 11. 用 revert 卻不附被還原的 SHA

```
❌ revert: undo previous change
```

規範沒有強制 revert 的格式，但業界慣例（也是唯一讓 `git log` 可追溯的方式）是：

```
✅ revert: let us never again speak of the noodle incident

Refs: 676104e, a215868
```

## 12. Merge commit 硬套 Conventional Commits 格式

Merge commit（`git merge` 自動產生的訊息，如 `Merge branch 'feature/x' into main`）
不需要、也不應該被強行改寫成 `<type>: ...` 格式——這類訊息由 git 自動管理，
語意本身就是「合併」，不代表某個 type 的變更。若專案的合併策略允許人工訊息，
才需要判斷是否要遵循 Conventional Commits；預設情況下維持原樣。

## 13. WIP / 佔位 commit 進主線

```
❌ wip
❌ checkpoint before lunch
```

這類訊息完全不符合任何 type，且暗示這不是一個「完整、可獨立存在」的變更。
如果使用者要求現在就 commit 一個尚未完成的中間狀態，應該誠實反映：可以用
`chore: WIP snapshot of <topic> (not production ready)` 之類的說明，但更好的做法
是提醒使用者（Human Confirmation 原則）——這種 commit 通常應該留在本機分支，
之後用 `git commit --amend` 或互動式 rebase 整理成正式的 atomic commit，而不是
直接進入共享歷史。
