from utils.getPublicData import *
from datetime import datetime
from snownlp import SnowNLP
def getTableDataPageData():
    return getAllCiPingTotal()

def getTableData(hotWord):
    commentList = getAllCommentsData()
    tableData = []
    hotWord_str = str(hotWord) if hotWord else ''
    for comment in commentList:
        c4 = comment[4] if comment[4] is not None else ''
        if hotWord_str and hotWord_str in str(c4):
            tableData.append(comment)
    return tableData

def getTableDataEchartsData(hotWord):
    tableList = getTableData(hotWord)
    xData = [x[1] for x in tableList if x[1] is not None]
    xData = list(set(xData))
    try:
        xData = list(sorted(xData, key=lambda x: datetime.strptime(str(x), '%Y-%m-%d').timestamp(), reverse=True))
    except:
        pass
    yData = [0 for x in range(len(xData))]
    for comment in tableList:
        for index, x in enumerate(xData):
            if str(comment[1]) == str(x):
                yData[index] += 1
    return xData, yData

def getTableDataArticle(flag):
    if flag:
        tableListOld = getAllData()
        tableList = []
        for item in tableListOld:
            item = list(item)
            emotionValue = SnowNLP(item[5]).sentiments
            if emotionValue > 0.5:
                emotionValue = '正面'
            elif emotionValue == 0.5:
                emotionValue = '中性'
            elif emotionValue < 0.5:
                emotionValue = '负面'
            item.append(emotionValue)
            tableList.append(item)
    else:
        tableList = getAllData()
    return tableList
