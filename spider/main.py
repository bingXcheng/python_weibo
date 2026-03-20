# -*- coding: utf-8 -*-
import os
import sys
import pandas as pd
from sqlalchemy import text
from snownlp import SnowNLP
import hashlib

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from spiderContent import start as contentStart
from spiderComments import start as commentsStart

# 导入配置
from config import PAGE_COUNT, SLEEP_SECONDS
# 统一数据库配置（MySQL 优先 + SQLite 备选）
import db_config

article_path = os.path.join(current_dir, 'articleData.csv')
comments_path = os.path.join(current_dir, 'commentsData.csv')

# 使用统一的数据库引擎（自动选择 MySQL 或 SQLite）
engine = db_config.get_engine()


def compute_sentiment(text):
    """计算单条文本情感值"""
    try:
        s = SnowNLP(str(text)[:500])
        score = s.sentiments
        if score > 0.55:
            label = '正面'
        elif score < 0.45:
            label = '负面'
        else:
            label = '中性'
        return score, label
    except Exception:
        return 0.5, '中性'


def get_text_hash(text):
    h = hashlib.md5(str(text)[:200].encode('utf-8'))
    return int(h.hexdigest(), 16) % (10 ** 18)


def save_to_sql():
    try:
        article_new = pd.read_csv(article_path)
        comments_new = pd.read_csv(comments_path)

        # 为文章预计算情感
        sentiment_cache = {}
        with engine.connect() as conn:
            result = conn.execute(text("SELECT text_hash, sentiment, sentiment_label FROM sentiment_cache"))
            for row in result:
                sentiment_cache[row[0]] = (row[1], row[2])

        def get_cached_sentiment(text_input):
            h = get_text_hash(text_input)
            if h in sentiment_cache:
                return sentiment_cache[h]
            score, label = compute_sentiment(text_input)
            sentiment_cache[h] = (score, label)
            return score, label

        article_new['sentiment'] = article_new['content'].apply(lambda x: get_cached_sentiment(x)[0])
        article_new['sentiment_label'] = article_new['content'].apply(lambda x: get_cached_sentiment(x)[1])

        # 保存情感缓存（兼容 MySQL INSERT IGNORE 和 SQLite INSERT OR IGNORE）
        insert_sql = "INSERT OR IGNORE INTO sentiment_cache (text_hash, text, sentiment, sentiment_label) VALUES (:h, :text, :score, :label)"
        if db_config.is_mysql():
            insert_sql = "INSERT IGNORE INTO sentiment_cache (text_hash, text, sentiment, sentiment_label) VALUES (:h, :text, :score, :label)"
        with engine.begin() as conn:
            for h, (score, label) in sentiment_cache.items():
                conn.execute(text(insert_sql), {"h": h, "text": "", "score": score, "label": label})

        article_old = pd.read_sql(text('SELECT * FROM article'), engine)
        article_cols = set(article_new.columns)
        for col in ['sentiment', 'sentiment_label']:
            if col not in article_old.columns:
                article_old[col] = None
        combined_articles = pd.concat([article_new, article_old]).drop_duplicates('id', keep='last')

        comments_old = pd.read_sql(text('SELECT * FROM comments'), engine)
        combined_comments = pd.concat([comments_new, comments_old]).drop_duplicates('content', keep='last')

        combined_articles.to_sql('article', engine, if_exists='replace', index=False)
        combined_comments.to_sql('comments', engine, if_exists='replace', index=False)

        if os.path.exists(article_path):
            os.remove(article_path)
        if os.path.exists(comments_path):
            os.remove(comments_path)
    except Exception as e:
        raise RuntimeError("数据存储失败: {}".format(str(e)))


def main():
    try:
        yield "正在初始化爬虫..."
        for item in contentStart(10, PAGE_COUNT):
            yield item

        yield "开始抓取评论..."
        for item in commentsStart():
            yield item

        yield "数据存储中（包含情感分析）..."
        save_to_sql()
        yield "completed"
    except Exception as e:
        yield "ERR: {}".format(str(e))


if __name__ == '__main__':
    for progress in main():
        print(progress)
