# -*- coding: utf-8 -*-
import pickle
import os
import requests

# 使用与 weibo_login.py 相同的路径
pkl = os.path.join(os.path.dirname(__file__), 'weibo_cookies.pkl')
print(f"Loading cookies from: {pkl}")
print(f"File exists: {os.path.exists(pkl)}")

if os.path.exists(pkl):
    cookies = pickle.load(open(pkl, 'rb'))
    print(f'Cookies loaded: {len(cookies)} items')
    for k in cookies:
        print(f'  {k}: {cookies[k][:40]}...')

    print('\nTesting API...')
    resp = requests.get(
        'https://m.weibo.cn/api/container/getIndex',
        params={'containerid': '102803', 'openApp': '0'},
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://m.weibo.cn/',
            'X-Requested-With': 'XMLHttpRequest',
            'mweibo-pwa': '1',
        },
        cookies=cookies,
        timeout=10
    )
    print('Status:', resp.status_code)
    data = resp.json()
    print('OK:', data.get('ok'))
    print('Response preview:', str(data)[:500])
else:
    print('No cookie file found')
