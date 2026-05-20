# POE2 自動補血/補魔
<img width="288" height="292" alt="image" src="https://github.com/user-attachments/assets/1e9c6b95-56f8-41dd-91e2-faefde8a8185" />

透過螢幕擷取分析生命球與魔力球的填充比例，低於門檻時自動按下你設定的藥水按鍵。附半透明遊戲浮層與全域熱鍵。

目前偵測採用「黑圈空區比例」：偵測球體液面以上的暗黑/透明黑背景，並以 `fill% = 100 - empty%` 估算剩餘量。建議在遊戲亮度、濾鏡與 UI 色調相對固定時使用，穩定度更高。

## 風險聲明

此工具會**自動模擬鍵盤按鍵**，可能違反 [Grinding Gear Games 使用者條款](https://www.pathofexile.com/legal) 對第三方自動化程式的限制，**帳號有被封禁風險**。本程式僅使用螢幕像素分析，不讀取遊戲記憶體，但無法保證安全。使用風險自負。

## 下載（一般使用者）

到 [GitHub Releases](https://github.com/pullum327/Auto_heal_poe2/releases) 下載 **`POE2_AutoFlask-Windows.zip`**，解壓後執行 `POE2_AutoFlask.exe`，無需安裝 Python。

## 環境需求

- Windows 10/11
- POE2 **視窗化**或**無邊框視窗化**（不支援獨占全螢幕）

## 開發者：從原始碼執行

- Python 3.11+

## 安裝（開發用）

```bash
cd test0
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 啟動

**請使用專案虛擬環境**（勿直接用系統 `python`，否則會出現 `No module named 'PyQt6'`）。

方式一（建議）：雙擊 [`run.bat`](run.bat)

方式二：命令列

```powershell
cd test0
.venv\Scripts\activate
python main.py
```

若尚未安裝依賴：

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

## 首次使用

1. 啟動 POE2（視窗化），進入遊戲畫面。
2. 執行本程式，會出現半透明浮層。
3. **右鍵浮層** →「校正生命球」：螢幕變暗後，**點一下左下紅色生命球的液體中心**，滾輪可微調框大小，按 Enter 確認。
4. 同樣方式「校正魔力球」：點右下**藍色魔力球**中心。
5. 請點在**液體圓內**，不要點金屬外框或雕像；建議**滿血/滿魔**時校正。
6. 右鍵 →「設定」：設定補血/補魔按鍵、觸發門檻、藥水冷卻、球體半徑 %。
7. 開啟浮層上的「補血 · ON」/「補魔 · ON」，確認生命/魔力百分比會隨受傷/耗魔變化。

## 熱鍵（預設，可在設定中修改）

| 熱鍵 | 功能 |
|------|------|
| F6 | 切換補血開關 |
| F7 | 切換補魔開關 |
| F8 | 全域暫停 / 恢復（無浮層按鈕） |

## 建議測試流程

1. 在城鎮將門檻調高（如 90%），確認會自動按鍵。
2. 調回實戰值（約 35–50%）。
3. Alt+Tab 離開遊戲，確認顯示「偵測異常」且**不會**連續按鍵。

## 疑難排解

| 問題 | 處理方式 |
|------|----------|
| 百分比不變 | 重新點擊球心校正；確認點在液體圓內、球體未被 UI 遮住 |
| 框太大/太小 | 設定中調整「球體半徑 %」，或校正時用滾輪微調 |
| 百分比跳動大 | 調高藥水冷卻；確認 Gamma/亮度正常 |
| 遊戲內沒反應 | 確認藥水按鍵與遊戲設定一致；POE2 需為視窗化 |
| 改解析度後失效 | 重新校正生命球與魔力球 |

## 設定檔

執行後會產生 `config.json`，包含球體座標、按鍵、門檻、熱鍵等。

## 打包成 exe（開發者）

雙擊 **`build.bat`**，完成後在 `dist\` 取得：

- `POE2_AutoFlask\POE2_AutoFlask.exe`
- `POE2_AutoFlask-Windows.zip`（可上傳 GitHub）

詳細發佈步驟見 [docs/GITHUB_RELEASE.md](docs/GITHUB_RELEASE.md)。

## 專案結構

```
main.py              # 進入點
config.py            # 設定讀寫
build.bat            # 一鍵打包
core/                # 擷取、偵測、按鍵邏輯
ui/                  # 浮層、設定、校正
services/            # 背景 worker、熱鍵
docs/                # GitHub Releases 教學
```
