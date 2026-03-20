from utils import getPublicData
from datetime import datetime
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import numpy as np
import jieba
import os
import re
from snownlp import SnowNLP

def getHomeTopLikeCommentsData():
    commentsList = getPublicData.getAllCommentsData()
    def safe_int(comment):
        try:
            return int(comment[2]) if comment[2] is not None else 0
        except:
            return 0
    commentsListSorted = list(sorted(commentsList, key=safe_int, reverse=True))[:5]
    return commentsListSorted



def getTagData():
    articleData = getPublicData.getAllData()
    maxLikeNum = 0
    maxLikeAuthorName = ''
    cityDic = {}

    for article in articleData:
        # 统计获赞最多作者
        if int(article[1]) > maxLikeNum:
            maxLikeNum = int(article[1])
            maxLikeAuthorName = article[11]

        # 统计城市发布量（排除'无'值）
        city = article[4]
        if city == '无':
            continue
        cityDic[city] = cityDic.get(city, 0) + 1

    # 获取发布最多的城市及其数量
    if cityDic:
        sorted_cities = sorted(cityDic.items(), key=lambda x: x[1], reverse=True)
        maxCity, cityPostCount = sorted_cities[0]  # 解包获取城市和数量
    else:
        maxCity = '无'
        cityPostCount = 0

    return len(articleData), maxLikeAuthorName, maxCity, maxLikeNum, cityPostCount

def getCommentLenData():
    comments = getPublicData.getAllCommentsData()
    return len(comments)

def getCreatedNumEchartsData():
    articleData = getPublicData.getAllData()
    xData = list(set([x[7] for x in articleData]))
    xData = list(sorted(xData,key=lambda x:datetime.strptime(x,'%Y-%m-%d').timestamp(),reverse=True))
    yData = [0 for x in range(len(xData))]
    for i in articleData:
        for index,j in enumerate(xData):
            if i[7] == j:
                yData[index] += 1

    return xData,yData

def getTypeCharData():
    allData = getPublicData.getAllData()
    typeDic = {}
    for i in allData:
        if typeDic.get(i[8], -1) == -1:
            typeDic[i[8]] = 1
        else:
            typeDic[i[8]] += 1
    resultData = []
    for key, value in typeDic.items():
        resultData.append({
            'name': key,
            'value': value,
        })
    return resultData

def getCommentsUserCratedNumEchartsData():
    userData = getPublicData.getAllCommentsData()
    createdDic = {}
    for i in userData:
        if createdDic.get(i[1],-1) == -1:
            createdDic[i[1]] =1
        else:
            createdDic[i[1]] +=1
    resultData = []
    for key,value in createdDic.items():
        resultData.append({
            'name':key,
            'value':value,
        })
    return resultData

def stopwordslist():
    stopwords = [line.strip() for line in open('./stopWords.txt',encoding='UTF-8').readlines()]
    return stopwords


def getUserNameWordCloud():
    comments = getPublicData.getAllCommentsData()
    text = ''.join(comment[5] for comment in comments)
    stopwords = stopwordslist()

    words = ' '.join([word for word in jieba.cut(text) if word not in stopwords])

    save_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'static',
        'authorNameCloud.jpg'
    )
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    WordCloud(
        width=1600,
        height=1000,
        background_color='white',
        font_path='msyh.ttc',
        colormap='viridis',
        max_words=300,
        max_font_size=220,
        collocations=False,
        prefer_horizontal=0.82,
        relative_scaling=0.4
    ).generate(words).to_file(save_path)


def _extract_keywords_from_text(text):
    """从文本中提取微博话题关键词"""
    # 提取 #话题# 格式
    topics = re.findall(r'#([^#]{2,20})#', str(text))
    # 过滤纯数字和无意义词
    keywords = []
    stop = set(['微博','视频','图片','网页','链接','全文','展开','评论','转发','分享','收藏','赞','举报'])
    for t in topics:
        t = t.strip()
        if len(t) >= 2 and t not in stop:
            keywords.append(t)
    return keywords


def getHotKeywordRanking():
    """从微博文章内容中提取热点关键词并排行"""
    articles = getPublicData.getAllData()
    keyword_count = {}

    for article in articles:
        content = article[5] if len(article) > 5 else ''
        keywords = _extract_keywords_from_text(content)
        for kw in keywords:
            keyword_count[kw] = keyword_count.get(kw, 0) + 1

    # 按频次排序，取TOP50
    sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:50]

    # 计算情感标签
    hot_rank_list = []
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    top_count = sorted_keywords[0][1] if sorted_keywords else 1

    for keyword, count in sorted_keywords:
        try:
            sentiment = SnowNLP(keyword).sentiments
        except:
            sentiment = 0.5
        if sentiment > 0.55:
            label = '正面'
            positive_count += 1
        elif sentiment < 0.45:
            label = '负面'
            negative_count += 1
        else:
            label = '中性'
            neutral_count += 1
        hot_rank_list.append({
            'keyword': keyword,
            'count': count,
            'sentiment': round(sentiment, 3),
            'sentiment_label': label
        })

    return {
        'hot_rank_list': hot_rank_list,
        'rank_keywords': [x['keyword'] for x in hot_rank_list],
        'rank_counts': [x['count'] for x in hot_rank_list],
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'total_count': len(sorted_keywords),
        'top_count': top_count
    }


