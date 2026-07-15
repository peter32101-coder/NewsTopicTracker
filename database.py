from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'news_tracker.db')

db = SQLAlchemy()

class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime)
    last_scraped_at = db.Column(db.DateTime)

    articles = db.relationship('Article', backref='topics', cascade='all, delete-orphan')

class Article(db.Model):
    __tablename__ = "articles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)
    title = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, unique=True, nullable=False)
    published_at = db.Column(db.DateTime)
    scraped_at = db.Column(db.DateTime)


#儲存新的主題關鍵字，並清除舊的主題和文章資料(目前每次只能追蹤一個主題)
def save_topic(keyword):
    Topic.query.delete()
    new_topic = Topic(keyword=keyword, created_at=datetime.now())
    db.session.add(new_topic)
    db.session.commit()
    print(f"已儲存新主題: {keyword} (ID: {new_topic.id})")
    return new_topic.id

#取得目前追蹤的主題資訊
def get_current_topic():
    return Topic.query.order_by(Topic.id.desc()).first()

#儲存報導列表，並回傳新增筆數
def save_articles(topic_id,articles):
    new_count = 0
    for v in articles:
        try:
            published_at = v['published_at']
            if isinstance(published_at, str):
                published_at = datetime.strptime(v['published_at'], '%Y-%m-%d %H:%M:%S')

            article = Article(
                topic_id=topic_id,
                title=v['title'],
                url=v['url'],
                published_at=published_at,
                scraped_at=datetime.now()
            )
            db.session.add(article)
            db.session.commit()
            new_count += 1
        except Exception as e:
            db.session.rollback()
            print(f"儲存報導失敗: {v['title']}，原因: {e}")
    return new_count

#更新議題最後爬取時間
def update_last_scraped(topic_id):
    topic = Topic.query.get(topic_id)
    if topic:
        topic.last_scraped_at = datetime.now()
        db.session.commit()
        print(f"已更新議題 {topic.keyword} 的最後爬取時間")
    else:
        print(f"找不到議題 ID: {topic_id}")

#取得目前主題的所有報導
def get_articles(topic_id):
    return Article.query.filter_by(topic_id=topic_id).order_by(Article.published_at.desc()).all()



# 測試程式
# if __name__ == '__main__':
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