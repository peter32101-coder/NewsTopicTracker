import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'news_tracker.db')

#與資料庫連線
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        print("成功連接到資料庫！")
        return conn
    except sqlite3.Error as e:
        print(f"連接資料庫時發生錯誤: {e}")
        return None

#建立資料庫表格
def init_db():
    conn = get_db_connection()
    if not conn:
        return
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS topics
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    created_at DATETIME,
                    last_scraped_at DATETIME)''')
    print("topics 表格建立完成！")

    c.execute('''CREATE TABLE IF NOT EXISTS articles
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    published_at DATETIME,
                    scraped_at DATETIME)''')
    print("articles 表格建立完成！")

    conn.commit()
    conn.close()

#儲存新的主題關鍵字，並清除舊的主題和文章資料(目前每次只能追蹤一個主題)
def save_topic(keyword):
    conn = get_db_connection()
    if not conn:
        return
    c = conn.cursor()
    c.execute('''DELETE FROM topics''')
    c.execute('''DELETE FROM articles''')
    c.execute('''INSERT INTO topics (keyword, created_at) VALUES (?, ?)''',
                (keyword, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    topic_id = c.lastrowid

    conn.commit()
    conn.close()
    print(f"已儲存新主題: {keyword} (ID: {topic_id})")
    return topic_id

#取得目前追蹤的主題資訊
def get_current_topic():
    conn = get_db_connection()
    if not conn:
        return None
    c = conn.cursor()
    c.execute('''SELECT * FROM topics ORDER BY id DESC LIMIT 1''')
    current_topic = c.fetchone()
    conn.close()
    return current_topic

#儲存報導列表，並回傳新增筆數
def save_articles(topic_id,articles):
    conn = get_db_connection()
    if not conn:
        return None
    new_count = 0
    c = conn.cursor() 
    for v in articles:
        try:
            c.execute('''INSERT INTO articles (topic_id, title, url, published_at, scraped_at) VALUES (?, ?, ?, ?, ?)''',
                      (topic_id, v['title'], v['url'], v['published_at'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            new_count += 1
        except:
            pass

    conn.commit()
    conn.close()
    return new_count

#更新議題最後爬取時間
def update_last_scraped(topic_id):
    conn = get_db_connection()
    if not conn:
        return None
    c = conn.cursor()
    c.execute('''UPDATE topics SET last_scraped_at = ? WHERE id = ?''',(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),topic_id))

    conn.commit()
    conn.close()

#取得目前主題的所有報導
def get_articles(topic_id):
    conn = get_db_connection()
    if not conn:
        return None
    c = conn.cursor()
    c.execute('''SELECT * FROM articles WHERE topic_id = ? ORDER BY published_at DESC''', (topic_id,))
    articles = c.fetchall()

    conn.close()
    return articles




# 測試程式
if __name__ == '__main__':
    init_db()
    print("資料庫初始化完成")

    topic_id = save_topic("人工智慧")
    print(f"議題已建立，id = {topic_id}")

    fake_articles = [
        {'title': '測試報導一', 'url': 'https://example.com/1', 'published_at': datetime.now()},
        {'title': '測試報導二', 'url': 'https://example.com/2', 'published_at': datetime.now()},
        {'title': '測試報導一', 'url': 'https://example.com/1', 'published_at': datetime.now()},  # 重複
    ]
    count = save_articles(topic_id, fake_articles)
    print(f"新增 {count} 筆（應為 2）")

    articles = get_articles(topic_id)
    print(f"查詢到 {len(articles)} 筆報導")

    update_last_scraped(topic_id)
    topic = get_current_topic()
    print(f"目前議題：{topic['keyword']}，最後爬取：{topic['last_scraped_at']}")