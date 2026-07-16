# 📰 新聞議題追蹤器 News Topic Tracker

以 Python 打造的新聞自動追蹤工具，輸入關鍵字後自動爬取中央社（CNA）相關報導，並透過每日排程持續監控新增內容，所有資料集中存入本機資料庫，隨時可在網頁介面瀏覽。

> 🔧 本分支（`sqlalchemy`）將資料存取層由原生 `sqlite3` 重構為 **SQLAlchemy ORM**，並完成 **Docker 容器化**，支援資料持久化與跨環境部署。

---

## 功能特色

- 🔍 **關鍵字追蹤**：輸入任意關鍵字，立即爬取 CNA 搜尋結果頁上的所有相關報導
- 🗃️ **自動去重**：以文章 URL 為唯一鍵，重複報導自動略過，不重複寫入資料庫
- 🕗 **每日自動更新**：透過系統 cron job 定時爬取，有新報導才寫入
- 🖥️ **網頁操作介面**：以 Flask 建置，支援設定議題、手動更新、瀏覽報導列表
- 🔄 **雙模式爬蟲**：手動觸發時以有視窗模式執行方便觀察，排程時以 Headless 模式靜默運作
- 🧩 **ORM 資料模型**：以 SQLAlchemy 定義 `Topic` / `Article` 模型與外鍵關聯，取代手寫 SQL 語法
- 🐳 **容器化部署**：以 Docker 封裝完整執行環境（含 Chromium 瀏覽器），支援一鍵啟動與資料持久化

---

## 技術架構

| 層級 | 技術 |
|------|------|
| Web 框架 | Flask |
| ORM | SQLAlchemy（Flask-SQLAlchemy） |
| 資料庫 | SQLite |
| 爬蟲引擎 | Selenium + Chromium（容器內）／ChromeDriverManager（本機） |
| HTML 解析 | BeautifulSoup4 |
| 排程 | 系統 cron job（Mac / Linux）|
| 前端 | Jinja2 + HTML / CSS |
| 容器化 | Docker |

---

## 資料庫結構

改用 SQLAlchemy ORM 定義以下兩個模型：

**Topic（追蹤議題）**
| 欄位 | 型別 | 說明 |
|---|---|---|
| id | Integer | 主鍵 |
| keyword | Text | 追蹤關鍵字 |
| created_at | DateTime | 建立時間 |
| last_scraped_at | DateTime | 最後爬取時間 |

**Article（新聞報導）**
| 欄位 | 型別 | 說明 |
|---|---|---|
| id | Integer | 主鍵 |
| topic_id | Integer | 外鍵，對應 Topic.id |
| title | Text | 報導標題 |
| url | Text | 報導連結（唯一值） |
| published_at | DateTime | 發布時間 |
| scraped_at | DateTime | 爬取時間 |

兩者為一對多關聯（一個 Topic 對應多筆 Article），並設定 `cascade='all, delete-orphan'`。

> ⚠️ 注意：SQLAlchemy 的 `cascade` 設定僅在透過 ORM 物件層級刪除時生效，`Topic.query.delete()` 這類批次刪除語法不會觸發 cascade。因此換題邏輯（`save_topic()`）改為先手動清空 `Article`，再刪除 `Topic`，避免產生孤兒資料或 SQLite id 重複使用導致資料錯亂的問題。

---

## 專案結構

```
NewsTopicTracker/
├── app.py                # Flask 主程式（路由）
├── scraper.py            # Selenium 爬蟲模組
├── database.py           # SQLAlchemy 資料模型與 CRUD 操作
├── daily_job.py           # cron job 執行的排程腳本
├── crontab_setup.sh       # 自動設定 cron job 的輔助腳本
├── dockerfile             # Docker 容器建置設定
├── .dockerignore          # Docker 建置時排除的檔案
├── requirements.txt       # Python 套件清單
├── templates/
│   ├── base.html          # 共用版型
│   └── index.html         # 首頁
└── static/
    └── style.css           # 網頁樣式
```

---

## 安裝與執行（本機開發環境）

### 1. Clone 專案

```bash
git clone https://github.com/peter32101-coder/NewsTopicTracker.git
cd NewsTopicTracker
git checkout sqlalchemy
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

## 使用 Docker 執行

專案已完成容器化，內建 Chromium 瀏覽器，不需要在主機另外安裝 Chrome 或設定 Selenium 環境。

### 1. 建置映像檔

```bash
docker build -t news-tracker .
```

### 2. 執行容器（含資料持久化）

```bash
docker run -p 5001:5000 -v $(pwd)/data:/app/data news-tracker
```

- `-p 5001:5000`：將容器內的 5000 port 對應到主機的 5001 port（可依需求調整）
- `-v $(pwd)/data:/app/data`：將資料庫檔案掛載到主機的 `./data` 資料夾，確保容器重啟或重建後資料不遺失

開啟瀏覽器前往 [http://localhost:5001](http://localhost:5001)

### 容器化過程的技術重點

- **CPU 架構相容性**：Google Chrome 官方 `.deb` 套件僅提供 amd64 版本，在 Apple Silicon（arm64）環境建置會因系統函式庫架構不符而失敗。改用 Debian 官方 repo 提供的 **Chromium**（`chromium` + `chromium-driver`），可同時支援 amd64 / arm64，避免額外處理套件簽章與架構問題。
- **環境自動判斷**：`scraper.py` 以 `os.path.exists()` 偵測容器內建的 Chromium 路徑是否存在，存在則直接指定 `binary_location` 使用容器內建瀏覽器，不存在則沿用本機的 `webdriver-manager` 自動下載機制，同一份程式碼可同時支援本機開發與容器環境。
- **對外監聽設定**：Flask 預設僅監聽 `127.0.0.1`，在容器內代表只接受容器內部的連線請求，需明確設定 `host='0.0.0.0'` 才能讓主機端透過 port mapping 存取。
- **資料持久化**：容器檔案系統預設為暫時性，容器重建後資料會遺失。透過環境變數 `DB_DIR` 讓資料庫路徑可彈性指定，並搭配 Docker volume 掛載，讓資料庫檔案實際存放於主機端。

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

> 📌 目前排程設定適用於本機直接執行的情境，容器內的排程機制規劃中。

---

## 使用方式

1. 在網頁輸入欲追蹤的關鍵字，點擊「開始追蹤」
2. 系統自動開啟瀏覽器爬取 CNA 搜尋結果，完成後顯示報導列表
3. 點擊「立即更新」可手動重新爬取最新資料
4. 每日排程會自動在背景執行，僅將新增報導寫入資料庫

---

## 開發紀錄：原生 SQL → SQLAlchemy ORM 重構

本分支將 `database.py` 由原生 `sqlite3` 語法改寫為 SQLAlchemy ORM，主要異動包含：

- 以 `db.Model` 定義 `Topic`、`Article` 資料模型，取代手寫 `CREATE TABLE`
- 以 `db.session` 管理連線生命週期，取代手動 `connect()` / `close()`
- 以 ORM 查詢語法（`Model.query.filter_by(...)`）取代原生 SQL 字串拼接

重構過程中排除的問題包含資料表外鍵對應、ORM 物件存取語法、日期型別轉換、換題時的批次刪除與 cascade 失效等，詳細除錯紀錄可參考專案內的除錯筆記（如尚未加入 repo，可視需要補充）。

---

## 注意事項

- 本工具僅供個人學習與研究使用，請遵守 CNA 網站使用條款
- 本機執行環境需安裝 Google Chrome 瀏覽器；Docker 環境已內建 Chromium，無需另外安裝
- 目前為單一議題追蹤模式，切換議題時將清除所有既有報導
