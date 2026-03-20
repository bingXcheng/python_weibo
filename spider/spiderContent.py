import os
import sys
import time
import csv
import requests
from datetime import datetime
from requests.cookies import RequestsCookieJar

current_dir = os.path.dirname(os.path.abspath(__file__))
article_path = os.path.join(current_dir, 'articleData.csv')

# 导入配置
sys.path.insert(0, current_dir)
try:
    from config import SLEEP_SECONDS
except ImportError:
    SLEEP_SECONDS = 2


def init():
    if not os.path.exists(article_path):
        with open(article_path, 'w', encoding='utf8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'likeNum', 'commentsLen', 'reposts_count', 'region',
                'content', 'contentLen', 'created_at', 'type', 'detailUrl',
                'authorAvatar', 'authorName', 'authorDetail', 'isVip',
                'user_id', 'screen_name', 'followers_count', 'verified'
            ])


def writer_row(row):
    with open(article_path, 'a', encoding='utf8', newline='') as f:
        csv.writer(f).writerow(row)


def clean_text(text):
    """从微博text字段中提取纯文本，去除HTML标签"""
    import re
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_json(url, params, cookies=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://m.weibo.cn/',
        'X-Requested-With': 'XMLHttpRequest',
        'mweibo-pwa': '1',
    }

    # 如果有 XSRF-TOKEN，添加到 headers
    if cookies and 'XSRF-TOKEN' in cookies:
        headers['x-xsrf-token'] = cookies['XSRF-TOKEN']

    try:
        print(f"[调试] 请求URL: {url}")
        print(f"[调试] 请求参数: {params}")
        resp = requests.get(url, headers=headers, params=params, cookies=cookies, timeout=10)
        print(f"[调试] 响应状态码: {resp.status_code}")
        print(f"[调试] 响应内容前500字符: {resp.text[:500]}")
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print("请求失败: {}".format(e))
    return None


def try_get_cookies():
    """获取 Cookie - 先尝不带 Cookie，行则直接用，不行再自动登录"""
    # 1. 先尝不带 Cookie 访问
    try:
        print("[Cookie] 尝试不带 Cookie 请求...")
        test_url = 'https://m.weibo.cn/api/container/getIndex'
        test_params = {'containerid': '102803', 'openApp': '0'}
        test_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://m.weibo.cn/',
            'X-Requested-With': 'XMLHttpRequest',
            'mweibo-pwa': '1',
        }
        resp = requests.get(test_url, headers=test_headers, params=test_params, timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            if data.get('ok') == 1:
                print("[Cookie] 不带 Cookie 请求成功！")
                return {}  # 返回空字典，不需要 Cookie
        # 状态码非 200 或 ok!=1，都说明需要 Cookie，继续走自动登录
        print(f"[Cookie] 不带 Cookie 返回无效数据 (ok={data.get('ok') if resp.status_code==200 else resp.status_code})，将启动自动登录")
    except Exception as e:
        print(f"[Cookie] 尝不带 Cookie 请求失败: {e}，将启动自动登录")

    # 2. 尝试自动登录
    try:
        from weibo_login import get_valid_cookies
        print("[Cookie] 正在启动自动登录...")
        return get_valid_cookies()
    except Exception as e:
        print(f"[Cookie] 自动登录失败: {e}")

    return None


def parse_cards(cards, article_type='热门'):
    for card in cards:
        mblog = card.get('mblog')
        if not mblog:
            continue
        user = mblog.get('user', {})
        text = clean_text(mblog.get('text', ''))

        region = mblog.get('region_name', '无')
        if region and region != '无':
            region = region.replace('发布于 ', '').strip()
        else:
            region = '无'

        created_str = mblog.get('created_at', '')
        try:
            if '+0800' in created_str:
                dt = datetime.strptime(created_str, '%a %b %d %H:%M:%S +0800 %Y')
            else:
                dt = datetime.strptime(created_str, '%a %b %d %H:%M:%S %z %Y')
            created_at = dt.strftime('%Y-%m-%d')
        except:
            created_at = datetime.now().strftime('%Y-%m-%d')

        is_vip = 1 if user.get('svip') or user.get('mbtype') in [2, 3, 12] else 0

        writer_row([
            mblog.get('id', ''),
            mblog.get('attitudes_count', 0),
            mblog.get('comments_count', 0),
            mblog.get('reposts_count', 0),
            region,
            text,
            len(text),
            created_at,
            article_type,
            "https://m.weibo.cn/detail/{}".format(mblog.get('id', '')),
            user.get('avatar_hd', user.get('profile_image_url', '')),
            user.get('screen_name', ''),
            "https://m.weibo.cn/u/{}".format(user.get('id', '')),
            is_vip,
            user.get('id', ''),
            user.get('screen_name', ''),
            user.get('followers_count', ''),
            1 if user.get('verified') else 0,
        ])


def start(type_num=10, page_num=2):
    init()
    since_id = None
    cookies = try_get_cookies()

    if cookies:
        print(f"[调试] 已获取 Cookie")
    else:
        print("[警告] 无法获取 Cookie，可能无法获取完整数据")

    for page in range(page_num):
        yield "正在抓取热门微博第 {}/{} 页".format(page + 1, page_num)
        time.sleep(SLEEP_SECONDS)

        params = {
            'containerid': '102803',
            'openApp': '0',
            'since_id': since_id if since_id else '',
        }

        data = get_json('https://m.weibo.cn/api/container/getIndex', params, cookies)

        print(f"[调试] 返回数据 ok={data.get('ok') if data else 'None'}")
        if data:
            print(f"[调试] 返回数据 keys: {list(data.keys())}")
            print(f"[调试] data字段类型: {type(data.get('data'))}")
            if isinstance(data.get('data'), dict):
                print(f"[调试] data内keys: {list(data.get('data', {}).keys())}")
            print(f"[调试] cards数量: {len(data.get('data', {}).get('cards', []))}")

        if not data or data.get('ok') != 1:
            yield "第 {} 页获取失败".format(page + 1)
            continue

        cards = data.get('data', {}).get('cardlistInfo', {})
        since_id = cards.get('since_id', '')

        all_cards = data.get('data', {}).get('cards', [])
        parse_cards(all_cards, '热门')

        if not since_id:
            yield "已抓取所有热门微博"
            break

    yield "文章数据抓取完成"


if __name__ == '__main__':
    for p in start(1, 3):
        print(p)
