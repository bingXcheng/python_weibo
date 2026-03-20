# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from weibo_login import get_valid_cookies

if __name__ == '__main__':
    print("Testing invisible cookie validation...")
    print("(You should NOT see any browser window)")
    cookies = get_valid_cookies()
    if cookies:
        print(f"Success: {len(cookies)} cookies loaded")
    else:
        print("Failed to get cookies")
