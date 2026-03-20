import requests
import csv
import os
import numpy as np
from numpy.ma.core import get_data


def init():
    if not os.path.exists('navData.csv'):
        with open('navData.csv','w',encoding='utf8',newline='') as csvfile:
            wirter = csv.writer(csvfile)
            wirter.writerow([
                'typeName',
                'gid',
                'containerid'
            ])

def wirterRow(row):
        with open('navData.csv','a',encoding='utf8',newline='') as csvfile:
            wirter = csv.writer(csvfile)
            wirter.writerow(row)

def get_html(url):
    headers  = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Cookie': 'SCF=Alv4s9kDoCFyijLjKOe5znSXAXGi7L2YXJOM4TQTslfYnKtZ7WpbLoiJ7BWBtB8QQh7oE7pNXMUfjdeKmlbA9Rc.; SUB=_2A25K2hezDeRhGeFN41sT-CzPzjiIHXVplhV7rDV8PUNbmtANLW3BkW9NQ9SFj3VRn5EhB1_9wI2GymuJnOLFL-IA; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFkX2qWYlQQ-R-YagO8L.NY5JpX5KzhUgL.FoM01h.E1hz0SKB2dJLoI0MLxK-LB-BLBKqLxKqLBK5LBK2LxKMLB-eLB-eLxKBLBonL1h5LxKqL1KnLB-qLxKqL1hnL1K8k; ALF=02_1745220835; PC_TOKEN=d59871b174; XSRF-TOKEN=CS3zL1fobnbl_7MfaXuUjMjG; WBPSESS=4ARBQ_XtZWWBs3-KYnu7goutacvz9btAbWDkjlgEonT2gesb-4BX8cBlpOZ345rUd9JhMMPCtuKccWrrNwZoKIk35KQEkSvxQ8lCOQh00est-FCqTesYcdnY2owkylMkGWcxLA59VwoIfXyMb31lpw=='
    }
    params = {
        'is_new_segment':1,
        'fetch_hot':1
    }
    response = requests.get(url,headers=headers,params=params)
    #print(response.json())
    if response.status_code == 200:
        return response.json()
    else:
        return None

def parse_json(response):
    navList = np.append(response['groups'][3]['group'],response['groups'][4]['group'])
    for nav in navList:
        navName = nav['title']
        gid = nav['gid']
        containerid = nav['containerid']
        wirterRow([
            navName,
            gid,
            containerid,
        ])

if __name__ == '__main__':
    url = 'https://weibo.com/ajax/feed/allGroups'
    init()
    response = get_html(url)
    parse_json(response)