# 如何將打包檔上傳到 GitHub Releases

本專案是 **Windows 桌面程式**，建議使用 **GitHub Releases** 發佈 `.zip` 安裝包。  
（「GitHub Packages」主要給 npm / Docker / NuGet 等套件庫，不適合這類 exe 程式。）

儲存庫：[pullum327/Auto_heal_poe2](https://github.com/pullum327/Auto_heal_poe2)

---

## 一、在本機打包

1. 雙擊專案目錄下的 **`build.bat`**
2. 完成後會得到：
   - `dist\POE2_AutoFlask\POE2_AutoFlask.exe`（整個資料夾都要一起給使用者）
   - `dist\POE2_AutoFlask-Windows.zip`（建議上傳這個）

> 使用者解壓 ZIP 後，雙擊 `POE2_AutoFlask.exe` 即可執行，無需安裝 Python。  
> 第一次執行會在同目錄產生 `config.json`。

---

## 二、在 GitHub 建立 Release（網頁操作）

1. 打開：https://github.com/pullum327/Auto_heal_poe2/releases  
2. 點 **「Draft a new release」**（建立新發佈）  
3. 填寫：
   - **Choose a tag**：輸入版本號，例如 `v1.0.0`，點 **「Create new tag」**
   - **Release title**：例如 `v1.0.0 - 首次發佈`
   - **Describe this release**：寫更新說明（支援 Markdown）
4. 在 **Attach binaries** 區塊，把 `POE2_AutoFlask-Windows.zip` **拖進去**
5. 點 **「Publish release」**

之後使用者可在 Releases 頁面下載 ZIP。

---

## 三、用命令列上傳 Release（進階）

需先安裝 [GitHub CLI](https://cli.github.com/) 並登入：`gh auth login`

```powershell
cd c:\Users\pullumleung\Desktop\test0

# 建立標籤並推送
git tag v1.0.0
git push origin v1.0.0

# 建立 Release 並上傳 zip
gh release create v1.0.0 dist\POE2_AutoFlask-Windows.zip ^
  --title "v1.0.0" ^
  --notes "POE2 自動補血/補魔。需視窗化模式，首次使用請校正球體。"
```

更新版本時，改 tag（如 `v1.0.1`）並重新執行 `build.bat` 後再上傳新 zip。

---

## 四、GitHub Releases vs GitHub Packages

| 功能 | 用途 | 本專案 |
|------|------|--------|
| **Releases** | 附檔下載（exe、zip） | ✅ 推薦 |
| **Packages** | 程式庫/registry（Docker 映像等） | ❌ 不需要 |

---

## 五、建議的 Release 說明範本

```markdown
## 下載
下載 `POE2_AutoFlask-Windows.zip`，解壓後執行 `POE2_AutoFlask.exe`。

## 需求
- Windows 10/11
- POE2 視窗化 / 無邊框視窗化

## 首次使用
1. 右鍵浮層 → 校正生命球：點左下紅球液體中心 → Enter
2. 校正魔力球：點右下藍球液體中心 → Enter
3. 設定補血/補魔按鍵；框大小可在設定調「球體半徑 %」或校正時滾輪微調
4. 開啟補血/補魔開關

## 風險聲明
可能違反遊戲條款，使用風險自負。
```

---

## 六、自動打包（可選）

若已啟用 GitHub Actions，推送標籤 `v*` 會自動打包並上傳 Release。  
見專案內 `.github/workflows/release.yml`。
