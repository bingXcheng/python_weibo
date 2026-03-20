import os
import csv
import requests
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
comments_path = os.path.join(current_dir, 'commentsData.csv')
article_data_path = os.path.join(current_dir, 'articleData.csv')


def init():
    if not os.path.exists(comments_path):
        with open(comments_path, 'w', encoding='utf8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'articleId', 'created_at', 'like_counts', 'region',
                'content', 'authorName', 'authorGender', 'authorAddress', 'authorAvatar'
            ])


def writer_row(row):
    with open(comments_path, 'a', encoding='utf8', newline='') as f:
        csv.writer(f).writerow(row)


def try_get_cookies():
    """获取 Cookie - 先尝试不带 Cookie，不行再用自动登录"""
    # 先尝试不带 Cookie
    try:
        print("[Cookie] 尝试不带 Cookie 请求...")
        test_url = 'https://m.weibo.cn/api/container/getIndex'
        test_params = {'containerid': '102803', 'openApp': '0'}
        resp = requests.get(test_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://m.weibo.cn/',
            'X-Requested-With': 'XMLHttpRequest',
        }, params=test_params, timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            if data.get('ok') == 1:
                print("[Cookie] 不带 Cookie 请求成功！")
                return resp.cookies.get_dict()
            else:
                print(f"[Cookie] 不带 Cookie 返回无效数据")
        else:
            print(f"[Cookie] 不带 Cookie 请求失败: {resp.status_code}")
    except Exception as e:
        print(f"[Cookie] 尝试失败: {e}")

    # 失败后尝试自动登录
    try:
        from weibo_login import get_valid_cookies
        print("[Cookie] 正在启动自动登录...")
        return get_valid_cookies()
    except Exception as e:
        print(f"[Cookie] 自动登录失败: {e}")

    return None


def get_comments_json(article_id, max_id=None, cookies=None):
    url = 'https://m.weibo.cn/comments/hotflow'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': f'https://m.weibo.cn/detail/{article_id}',
        'X-Requested-With': 'XMLHttpRequest',
    }
    params = {
        'id': article_id,
        'mid': article_id,
        'max_id_type': 0,
    }
    if max_id is not None:
        params['max_id'] = max_id

    try:
        resp = requests.get(url, headers=headers, params=params, cookies=cookies, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print("请求评论失败: {}".format(e))
    return None


def parse_comments(response, article_id):
    count = 0
    data_list = response.get('data', {}).get('data', [])
    for comment in data_list:
        user = comment.get('user', {})
        created_str = comment.get('created_at', '')
        try:
            if '+0800' in created_str:
                dt = datetime.strptime(created_str, '%a %b %d %H:%M:%S +0800 %Y')
            else:
                dt = datetime.strptime(created_str, '%a %b %d %H:%M:%S %z %Y')
            created_at = dt.strftime('%Y-%m-%d')
        except:
            created_at = datetime.now().strftime('%Y-%m-%d')

        region = comment.get('source', '无')
        if region and '来自' in region:
            region = region.replace('来自', '').strip()
        elif region == '无':
            region = '无'

        text = comment.get('text', '')
        # 微博 API 返回 like_count，兼容旧字段 like_counts
        like_count = comment.get('like_count', comment.get('like_counts', 0))

        writer_row([
            article_id,
            created_at,
            like_count,
            region,
            text,
            user.get('screen_name', ''),
            user.get('gender', ''),
            user.get('location', '').split(' ')[0] if user.get('location') else '未知',
            user.get('profile_image_url', '')
        ])
        count += 1
    return count


def start():
    init()
    yield "正在初始化评论爬取..."

    cookies = try_get_cookies()
    if cookies:
        print(f"[调试] 已获取 Cookie，共 {len(cookies)} 个")
    else:
        print("[警告] 无法获取 Cookie，可能无法获取评论数据")

    with open(article_data_path, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        next(reader)
        article_ids = [row[0] for row in reader]

    total = len(article_ids)
    for idx, article_id in enumerate(article_ids):
        yield "[{}/{}] 正在处理文章 {} 的评论".format(idx + 1, total, article_id)

        page_count = 0
        max_id = None
        max_id_type = 0

        while True:
            data = get_comments_json(article_id, max_id, cookies)
            if not data or data.get('ok') != 1:
                break

            page_count += parse_comments(data, article_id)

            max_id = data.get('data', {}).get('max_id')
            max_id_type = data.get('data', {}).get('max_id_type', 0)

            if max_id == 0 or max_id is None or max_id_type == 1:
                break

        yield "  -> 获取到 {} 条评论".format(page_count)


if __name__ == '__main__':
    for p in start():
        print(p)
