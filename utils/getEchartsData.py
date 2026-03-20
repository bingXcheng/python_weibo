from utils import getPublicData
import os
import hashlib

# 情感分析缓存（解决每次请求都重新计算的问题）
_sentiment_cache = {}

def _compute_sentiment(text):
    """计算单条文本情感，使用缓存"""
    from snownlp import SnowNLP
    if not text:
        return 0.5, '中性'
    text_hash = hash(str(text[:200])) % (10 ** 12)
    if text_hash in _sentiment_cache:
        return _sentiment_cache[text_hash]
    try:
        score = SnowNLP(str(text[:500])).sentiments
    except:
        score = 0.5
    if score > 0.55:
        label = '正面'
    elif score < 0.45:
        label = '负面'
    else:
        label = '中性'
    _sentiment_cache[text_hash] = (score, label)
    return score, label


def getTypeList():
    articleList = getPublicData.getAllData()
    typeList = list(set([x[8] for x in articleList if x[8] is not None]))
    if not typeList:
        typeList = ['热门']
    return typeList

def _safe_int(v, default=0):
    if v is None: return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default

def getArticleCharOneData(defaultType):
    articleList = getPublicData.getAllData()
    xData = []
    rangeNum = 1000
    for item in range(1,15):
        xData.append(str(rangeNum * item)+ '-' + str(rangeNum*(item+1)))
    yData = [0 for x in range(len(xData))]
    for article in articleList:
        if article[8] == defaultType:
            like_num = _safe_int(article[1])
            for item in range(14):
                if like_num < rangeNum*(item+2):
                    yData[item] += 1
                    break
    return xData,yData

def getArticleCharTwoData(defaultType):
    articleList = getPublicData.getAllData()
    xData = []
    rangeNum = 1000
    for item in range(1,15):
        xData.append(str(rangeNum * item)+ '-' + str(rangeNum*(item+1)))
    yData = [0 for x in range(len(xData))]
    for article in articleList:
        if article[8] == defaultType:
            comment_num = _safe_int(article[2])
            for item in range(14):
                if comment_num < rangeNum*(item+2):
                    yData[item] += 1
                    break
    return xData,yData

def getArticleCharThreeData(defaultType):
    articleList = getPublicData.getAllData()
    xData = []
    rangeNum = 50
    for item in range(1, 30):
        xData.append(str(rangeNum * item) + '-' + str(rangeNum * (item + 1)))
    yData = [0 for x in range(len(xData))]
    for article in articleList:
        if article[8] == defaultType:
            repost_num = _safe_int(article[3])
            for item in range(29):
                if repost_num < rangeNum * (item + 2):
                    yData[item] += 1
                    break
    return xData, yData

def getGeoCharDataTwo():
    cityList = getPublicData.cityList
    commentList = getPublicData.getAllCommentsData()
    cityDic = {}
    for comment in commentList:
        region = comment[3] if comment[3] is not None else ''
        if not region or region == '无':
            continue
        region_str = str(region)
        for j in cityList:
            if j['province'].find(region_str) != -1:
                if cityDic.get(j['province'], -1) == -1:
                    cityDic[j['province']] = 1
                else:
                    cityDic[j['province']] += 1

    cityDicList = []
    for key, value in cityDic.items():
        cityDicList.append({
            'name': key,
            'value': value
        })
    return cityDicList


def getGeoCharDataOne():
    cityList = getPublicData.cityList
    articleList = getPublicData.getAllData()

    cityDic = {}
    for article in articleList:
        region = article[4] if article[4] is not None else ''
        if not region or region == '无':
            continue
        region_str = str(region)
        for j in cityList:
                if j['province'].find(region_str) != -1:
                    if cityDic.get(j['province'],-1) == -1:
                        cityDic[j['province']] = 1
                    else:
                        cityDic[j['province']] += 1

    cityDicList = []
    for key, value in cityDic.items():
        cityDicList.append({
            'name': key,
            'value': value
        })
    return cityDicList

def getCommetCharDataOne():
    commentList = getPublicData.getAllCommentsData()
    xData = []
    rangeNum = 20
    for item in range(1, 100):
        xData.append(str(rangeNum * item) + '-' + str(rangeNum * (item + 1)))
    yData = [0 for x in range(len(xData))]
    for comment in commentList:
        like_val = _safe_int(comment[2])
        for item in range(99):
            if like_val < rangeNum * (item + 2):
                yData[item] += 1
                break
    return xData, yData

def getCommetCharDataTwo():
    commentList = getPublicData.getAllCommentsData()
    genderDic = {}
    for i in commentList:
        key = i[6] if i[6] is not None else '未知'
        if genderDic.get(key, -1) == -1:
            genderDic[key] = 1
        else:
            genderDic[key] += 1
    resultData = [{'name': x[0], 'value': x[1]} for x in genderDic.items()]
    return resultData

def stopwordslist():
    stopwords = [line.strip() for line in open('./stopWords.txt',encoding='UTF-8').readlines()]
    return stopwords


def getContentCloud():
    import jieba
    from wordcloud import WordCloud

    text = ''.join([article[5] for article in getPublicData.getAllData()])
    stopwords = stopwordslist()
    words = ' '.join([word for word in jieba.cut(text) if word not in stopwords])

    save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'contentCloud.jpg')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    WordCloud(
        width=1600,
        height=1000,
        background_color='white',
        font_path='msyh.ttc',
        colormap='Blues',
        max_words=300,
        max_font_size=220,
        collocations=False,
        prefer_horizontal=0.85,
        relative_scaling=0.4
    ).generate(words).to_file(save_path)


def getCommentContentCloud():
    import jieba
    from wordcloud import WordCloud

    text = ''.join([comment[4] for comment in getPublicData.getAllCommentsData()])
    stopwords = stopwordslist()
    words = ' '.join([word for word in jieba.cut(text) if word not in stopwords])

    save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'commentCloud.jpg')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    WordCloud(
        width=1600,
        height=1000,
        background_color='white',
        font_path='msyh.ttc',
        colormap='Reds',
        max_words=300,
        max_font_size=240,
        collocations=False,
        prefer_horizontal=0.8,
        relative_scaling=0.35
    ).generate(words).to_file(save_path)

def getYuQingCharDataOne():
    hotWordList = getPublicData.getAllCiPingTotal()
    xData = ['正面', '中性', '负面']
    yData = [0,0,0]
    for hotWord in hotWordList:
        _, label = _compute_sentiment(hotWord[0])
        if label == '正面':
            yData[0] += 1
        elif label == '中性':
            yData[1] += 1
        else:
            yData[2] += 1
    bieData = [{'name': '正面', 'value': yData[0]}, {'name': '中性', 'value': yData[1]}, {'name': '负面', 'value': yData[2]}]
    return xData, yData, bieData

def getYuQingCharDataTwo():
    bieData1 = [{'name': '正面', 'value': 0}, {'name': '中性', 'value': 0}, {'name': '负面', 'value': 0}]
    bieData2 = [{'name': '正面', 'value': 0}, {'name': '中性', 'value': 0}, {'name': '负面', 'value': 0}]
    commentList = getPublicData.getAllCommentsData()
    articleList = getPublicData.getAllData()
    # 评论：无 DB 情感字段，用缓存计算
    for comment in commentList:
        _, label = _compute_sentiment(comment[4] if len(comment) > 4 else '')
        if label == '正面': bieData1[0]['value'] += 1
        elif label == '中性': bieData1[1]['value'] += 1
        else: bieData1[2]['value'] += 1
    # 文章：优先用 DB 的 sentiment_label，无则再计算
    for article in articleList:
        if len(article) > 19 and article[19] in ('正面', '中性', '负面'):
            label = article[19]
        else:
            _, label = _compute_sentiment(article[5] if len(article) > 5 else '')
        if label == '正面': bieData2[0]['value'] += 1
        elif label == '中性': bieData2[1]['value'] += 1
        else: bieData2[2]['value'] += 1
    return bieData1, bieData2

def getYuQingCharDataThree():
    hotWordList = getPublicData.getAllCiPingTotal()
    return [x[0] for x in hotWordList],[int(x[1]) for x in hotWordList]


