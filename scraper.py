from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
import os

CNA_SEARCH_URL = 'https://www.cna.com.tw/search/hysearchws.aspx?q={keyword}'

# 容器內 Chromium 的預設安裝路徑（Debian/Ubuntu 環境）
CHROMIUM_BINARY = '/usr/bin/chromium'
CHROMIUM_DRIVER = '/usr/bin/chromedriver'

# 取得 Selenium WebDriver
def get_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')

    # 判斷是否在容器環境（有內建 Chromium）
    if os.path.exists(CHROMIUM_BINARY) and os.path.exists(CHROMIUM_DRIVER):
        options.binary_location = CHROMIUM_BINARY
        service = Service(CHROMIUM_DRIVER)
    else:
        # 本機開發環境（Mac），沿用原本的 webdriver-manager 自動下載機制
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)
    return driver

# 解析CNA日期字串格式
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y/%m/%d %H:%M')
    except ValueError:
        return None
    
def scrape_cna(keyword, headless=True):
    url = CNA_SEARCH_URL.format(keyword=keyword)
    driver = get_driver(headless=headless)
    articles = []
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'jsMainList')))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.select("#jsMainList li")

        for i in items:
            try:
                title = i.select_one("h2").text.strip()
                url = "https://www.cna.com.tw" + i.select_one("a")['href']
                date_str = i.select_one("time").text.strip()
                published_at = parse_date(date_str)

                if title and url :
                    articles.append({
                        'title': title,
                        'url': url,
                        'published_at': published_at.strftime('%Y-%m-%d %H:%M:%S') if published_at else None})
            except Exception as e:
                print(f"解析報導失敗: {e}")
                continue

    
    except Exception as e:
        print(f"爬取失敗: {e}")
    finally:
        driver.quit()

    print(f'共爬取 {len(articles)} 筆報導')
    return articles


if __name__ == '__main__':
    results = scrape_cna('台北鼠患', headless=False)  # 先用有視窗模式觀察
    for r in results:
        print(r['published_at'], r['title'], r['url'])