from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import init_db, save_topic, get_current_topic, save_articles, get_articles, update_last_scraped
from scraper import scrape_cna

app = Flask(__name__)


@app.route('/')
def index():
    topic = get_current_topic()
    articles = get_articles(topic["id"]) if topic else []
    return render_template("index.html", topic=topic, articles=articles)

@app.route("/set_topic", methods=["POST"])
def new_topic():
    topic_name = request.form.get("keyword","").strip()
    topic_id = save_topic(topic_name)
    articles = scrape_cna(topic_name, headless=True)
    save_articles(topic_id, articles)
    update_last_scraped(topic_id)
    return redirect(url_for('index'))

@app.route("/refresh", methods=[ "POST" ])
def refresh():
    topic = get_current_topic()
    if not topic:
        return jsonify({"error": "目前沒有設定追蹤議題！"}), 400

    articles = scrape_cna(topic["keyword"], headless=True)
    new_count = save_articles(topic["id"], articles)
    update_last_scraped(topic["id"])
    return jsonify({"success": True, "new_count": new_count})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)