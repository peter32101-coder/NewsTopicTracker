# 📰 新聞議題追蹤器 News Topic Tracker

以 Python 打造的新聞自動追蹤工具，輸入關鍵字後自動爬取中央社（CNA）相關報導，並透過每日排程持續監控新增內容，所有資料集中存入本機資料庫，隨時可在網頁介面瀏覽。

---

## 功能特色

- 🔍 **關鍵字追蹤**：輸入任意關鍵字，立即爬取 CNA 搜尋結果頁上的所有相關報導
- 🗃️ **自動去重**：以文章 URL 為唯一鍵，重複報導自動略過，不重複寫入資料庫
- 🕗 **每日自動更新**：透過系統 cron job 定時爬取，有新報導才寫入
- 🖥️ **網頁操作介面**：以 Flask 建置，支援設定議題、手動更新、瀏覽報導列表
- 🔄 **雙模式爬蟲**：手動觸發時以有視窗模式執行方便觀察，排程時以 Headless 模式靜默運作

---

## 技術架構

| 層級 | 技術 |
|------|------|
| Web 框架 | Flask |
| 資料庫 | SQLite |
| 爬蟲引擎 | Selenium + ChromeDriverManager |
| HTML 解析 | BeautifulSoup4 |
| 排程 | 系統 cron job（Mac / Linux）|
| 前端 | Jinja2 + HTML / CSS |

---

## 專案結構

```
NewsTopicTracker/
├── app.py                # Flask 主程式（路由）
├── scraper.py            # Selenium 爬蟲模組
├── database.py           # 資料庫初始化與 CRUD 操作
├── daily_job.py          # cron job 執行的排程腳本
├── crontab_setup.sh      # 自動設定 cron job 的輔助腳本
├── requirements.txt      # Python 套件清單
├── templates/
│   ├── base.html         # 共用版型
│   └── index.html        # 首頁
└── static/
    └── style.css         # 網頁樣式
```

---

## 安裝與執行

### 1. Clone 專案

```bash
git clone https://github.com/peter32101-coder/NewsTopicTracker.git
cd NewsTopicTracker
```

### 2. 建立並啟動虛擬環境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安裝相依套件

```bash
pip install -r requirements.txt
```

> ChromeDriver 會由 `webdriver-manager` 自動下載，無需手動安裝。

### 4. 啟動應用程式

```bash
python3 app.py
```

開啟瀏覽器前往 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 設定每日自動排程

執行以下指令，自動將 cron job 寫入系統排程（預設每日早上 08:00 執行）：

```bash
chmod +x crontab_setup.sh
./crontab_setup.sh
```

確認設定是否成功：

```bash
crontab -l
```

每次排程執行的結果會記錄在 `cron.log`，可隨時查閱：

```bash
cat cron.log
```

---

## 使用方式

1. 在網頁輸入欲追蹤的關鍵字，點擊「開始追蹤」
2. 系統自動開啟瀏覽器爬取 CNA 搜尋結果，完成後顯示報導列表
3. 點擊「立即更新」可手動重新爬取最新資料
4. 每日排程會自動在背景執行，僅將新增報導寫入資料庫

---

## 注意事項

- 本工具僅供個人學習與研究使用，請遵守 CNA 網站使用條款
- 執行環境需安裝 Google Chrome 瀏覽器
- 目前為單一議題追蹤模式，切換議題時將清除所有既有報導
