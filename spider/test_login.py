# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from weibo_login import get_valid_cookies

if __name__ == '__main__':
    print("=" * 50)
    print("微博自动登录工具")
    print("=" * 50)

    cookies = get_valid_cookies()

    if cookies:
        print("\n登录成功！Cookie 信息：")
        for name, value in list(cookies.items())[:5]:
            print(f"  {name}: {value[:30]}...")
    else:
        print("\n登录失败，请重试")
