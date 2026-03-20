from flask import Flask, session, render_template, redirect, Blueprint, request, Response
from utils import getHomeData,getTableData,getEchartsData
from snownlp import SnowNLP


pb = Blueprint('page',__name__,url_prefix='/page',template_folder='templates')
from spider.main import main


@pb.route('/home')
def home():
    username = session.get('username')
    articleLen, maxLikeAuthorName, maxCity, maxLikeCount, cityPostCount = getHomeData.getTagData()
    commentsLen = getHomeData.getCommentLenData()
    xData, yData = getHomeData.getCreatedNumEchartsData()
    userCreatedDicData = getHomeData.getTypeCharData()
    commentUserCreatedDicData = getHomeData.getCommentsUserCratedNumEchartsData()
    # 热点排行数据（首页预览，取TOP10）
    hot_data = getHomeData.getHotKeywordRanking()
    hot_rank_preview = hot_data['hot_rank_list'][:10]
    hot_positive = hot_data['positive_count']
    hot_negative = hot_data['negative_count']
    hot_neutral = hot_data['neutral_count']
    hot_total = hot_data['total_count']
    # 触发词云生成
    try:
        getEchartsData.getCommentContentCloud()
    except:
        pass
    return render_template('index.html',
                           username=username,
                           articleLen=articleLen,
                           commentsLen=commentsLen,
                           maxLikeAuthorName=maxLikeAuthorName,
                           maxLikeCount=maxLikeCount,
                           maxCity=maxCity,
                           cityPostCount=cityPostCount,
                           xData=xData,
                           yData=yData,
                           commentUserCreatedDicData=commentUserCreatedDicData,
                           userCreatedDicData=userCreatedDicData,
                           hot_rank_preview=hot_rank_preview,
                           hot_positive=hot_positive,
                           hot_negative=hot_negative,
                           hot_neutral=hot_neutral,
                           hot_total=hot_total,
                           top_hot_count=hot_rank_preview[0]['count'] if hot_rank_preview else 1,
                           )


@pb.route('/tableData')
def tabelData():
    username = session.get('username')
    hotWordList = getTableData.getTableDataPageData()
    defaultHotWord = hotWordList[0][0]
    if request.args.get('hotWord'):defaultHotWord = request.args.get('hotWord')
    defaultHotWordNum = 0
    for hotWord in hotWordList:
        if defaultHotWord == hotWord[0]:defaultHotWordNum=hotWord[1]
    emotionValue = SnowNLP(defaultHotWord).sentiments
    if emotionValue > 0.5:
        emotionValue = '正面'
    elif emotionValue == 0.5:
        emotionValue = '中性'
    elif emotionValue < 0.5:
        emotionValue = '负面'
    tableList = getTableData.getTableData(defaultHotWord)
    xData,yData = getTableData.getTableDataEchartsData(defaultHotWord)
    x1Data, y1Data = getEchartsData.getYuQingCharDataThree()
    return render_template('tableData.html',
                           username=username,
                           hotWordList=hotWordList,
                           defaultHotWord=defaultHotWord,
                           defaultHotWordNum=defaultHotWordNum,
                           emotionValue=emotionValue,
                           tableList=tableList,
                           xData=xData,
                           yData=yData,
                           x1Data=x1Data[:10],
                           y1Data=y1Data[:10]
                           )

@pb.route('/tableDataArticle')
def tableDataArticle():
    username = session.get('username')
    defaultFlag = False
    if request.args.get('flag'):defaultFlag = request.args.get('flag')
    tableData = getTableData.getTableDataArticle(defaultFlag)
    return render_template('tableDataArticle.html',
                           username=username,
                           defaultFlag=defaultFlag,
                           tableData=tableData
                           )

@pb.route('/articleChar')
def articleChar():
    username = session.get('username')
    typeList = getEchartsData.getTypeList()
    defaultType = typeList[0] if typeList else '热门'
    if request.args.get('type'):
        defaultType = request.args.get('type')
    xData,yData = getEchartsData.getArticleCharOneData(defaultType)
    x1Data,y1Data = getEchartsData.getArticleCharTwoData(defaultType)
    x2Data,y2Data = getEchartsData.getArticleCharThreeData(defaultType)
    return render_template('articleChar.html',
                           username=username,
                           typeList=typeList,
                           defaultType=defaultType,
                           xData=xData,
                           yData=yData,
                           x1Data=x1Data,
                           y1Data=y1Data,
                           x2Data=x2Data,
                           y2Data=y2Data
                           )

@pb.route('/ipChar')
def ipChar():
    username = session.get('username')
    geoDataOne = getEchartsData.getGeoCharDataOne()
    geoDataTwo = getEchartsData.getGeoCharDataTwo()
    articleLen = getHomeData.getTagData()
    commentsLen = getHomeData.getCommentLenData()
    return render_template('ipChar.html',
                           username=username,
                           geoDataOne=geoDataOne,
                           geoDataTwo=geoDataTwo,
                           articleLen=articleLen[0],
                           commentsLen=commentsLen,
                           )


@pb.route('/commentChar')
def commentChar():
    username = session.get('username')
    xData, yData = getEchartsData.getCommetCharDataOne()
    genderDicData = getEchartsData.getCommetCharDataTwo()
    topFiveComments = getHomeData.getHomeTopLikeCommentsData()
    try:
        getEchartsData.getCommentContentCloud()
    except:
        pass
    return render_template('commentChar.html',
                           username=username,
                           xData=xData,
                           yData=yData,
                           topFiveComments=topFiveComments,
                           genderDicData=genderDicData
                           )

@pb.route('/yuqingChar')
def yuqingChar():
    username = session.get('username')
    xData,yData,bieData = getEchartsData.getYuQingCharDataOne()
    bieData1, bieData2 = getEchartsData.getYuQingCharDataTwo()
    return render_template('yuqingChar.html',
                           username=username,
                           xData=xData,
                           yData=yData,
                           bieData=bieData,
                           bieData1=bieData1,
                           bieData2=bieData2,
                           )


@pb.route('/hotRank')
def hotRank():
    username = session.get('username')
    rank_data = getHomeData.getHotKeywordRanking()
    return render_template('hotRank.html',
                           username=username,
                           **rank_data
                           )




