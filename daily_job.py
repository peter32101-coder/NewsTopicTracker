import sys
import os
import logging
from datetime import datetime

# 將這支檔案所在的資料夾加入 Python 搜尋路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, get_current_topic, save_articles, update_last_scraped
from scraper import scrape_cna

logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cron.log'),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def run_daily_job():
    logger.info("開始執行每日爬取任務，開始時間： %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    init_db()
    topic = get_current_topic()
    if not topic:
        logger.info("目前沒有設定追蹤議題，任務結束。")
        return
    articles = scrape_cna(topic["keyword"], headless=True)
    new_count = save_articles(topic["id"], articles)
    update_last_scraped(topic["id"])
    logger.info("每日爬取任務完成，新增筆數：%d", new_count)

    
if __name__ == '__main__':
    run_daily_job()