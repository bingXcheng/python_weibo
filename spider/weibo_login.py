# -*- coding: utf-8 -*-
"""
微博自动登录模块
使用 Selenium 自动扫码登录，获取 Cookie
"""
import os
import time
import json
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

current_dir = os.path.dirname(os.path.abspath(__file__))
cookie_file = os.path.join(current_dir, 'weibo_cookies.pkl')


def get_chrome_driver(visible=False):
    """获取 Chrome 浏览器驱动"""
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    if visible:
        # 可视模式 - 用于扫码登录
        print("[登录] 正在打开可见浏览器（用于扫码）...")
    else:
        # 无头模式 - 客户无感知
        options.add_argument('--headless=new')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-infobars')

    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"[错误] Chrome 驱动初始化失败: {e}")
        return None


def save_cookies(driver, cookies):
    """保存 Cookie 到文件"""
    with open(cookie_file, 'wb') as f:
        pickle.dump(cookies, f)
    print(f"[登录] Cookie 已保存到: {cookie_file}")


def load_cookies():
    """从文件加载 Cookie"""
    if os.path.exists(cookie_file):
        try:
            with open(cookie_file, 'rb') as f:
                return pickle.load(f)
        except:
            return None
    return None


def login_weibo(wait_time=120):
    """
    自动扫码登录微博
    返回: cookies 字典 或 None
    """
    driver = get_chrome_driver(visible=True)
    if driver is None:
        return None

    try:
        print("[登录] 正在打开微博首页...")
        driver.get('https://m.weibo.cn')
        time.sleep(3)

        current_url = driver.current_url
        print(f"[登录] 当前URL: {current_url}")

        # 如果在登录页，需要扫码
        if 'login' in current_url.lower():
            print("[登录] 检测到需要登录，等待扫码...")

            # 保存二维码截图
            try:
                driver.save_screenshot(os.path.join(current_dir, 'qrcode.png'))
                print("[登录] 二维码截图已保存到 qrcode.png")
            except:
                pass

            # 等待登录完成
            start_time = time.time()
            while time.time() - start_time < wait_time:
                time.sleep(1)
                current_url = driver.current_url
                if 'login' not in current_url.lower():
                    print("[登录] 扫码成功！")
                    break
            else:
                print(f"[登录] 等待扫码超时（{wait_time}秒）")
                return None

        # 等待页面完全加载
        time.sleep(3)

        # 尝试访问 API 测试页面获取完整 Cookie
        print("[登录] 尝试获取完整 Cookie...")
        try:
            driver.get('https://m.weibo.cn/api/container/getIndex?containerid=102803&openApp=0')
            time.sleep(2)
        except:
            pass

        # 获取所有 cookies
        all_browser_cookies = driver.get_cookies()
        print(f"[登录] 浏览器共有 {len(all_browser_cookies)} 个 Cookie")

        cookies = {}
        for cookie in all_browser_cookies:
            cookies[cookie['name']] = cookie['value']
            print(f"  - {cookie['name']}: {cookie['value'][:40]}...")

        print(f"[登录] 提取到 {len(cookies)} 个 Cookie")

        # 如果 Cookie 不够，尝试访问微博主页获取
        if len(cookies) < 3:
            print("[登录] Cookie 数量不足，访问微博主页获取更多 Cookie...")
            try:
                driver.get('https://weibo.com')
                time.sleep(3)
                all_browser_cookies = driver.get_cookies()
                for cookie in all_browser_cookies:
                    if cookie['name'] not in cookies:
                        cookies[cookie['name']] = cookie['value']
                print(f"[登录] 补充后共 {len(cookies)} 个 Cookie")
            except Exception as e:
                print(f"[登录] 访问 weibo.com 出错: {e}")

        # 再次访问 m.weibo.cn 确保有移动端 Cookie
        try:
            driver.get('https://m.weibo.cn')
            time.sleep(3)
            all_browser_cookies = driver.get_cookies()
            for cookie in all_browser_cookies:
                cookies[cookie['name']] = cookie['value']
            print(f"[登录] 最终获取 {len(cookies)} 个 Cookie")
        except:
            pass

        # 保存
        if cookies:
            save_cookies(driver, cookies)

        return cookies

    except Exception as e:
        print(f"[登录] 登录过程出错: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        try:
            driver.quit()
        except:
            pass


def get_valid_cookies():
    """
    获取有效的 Cookie
    优先使用保存的 Cookie，如果无效则重新登录
    返回: requests.cookies.RequestsCookieJar 对象
    """
    import requests
    from requests.cookies import RequestsCookieJar

    # 先尝试加载保存的 Cookie
    saved_cookies = load_cookies()

    if saved_cookies:
        print(f"[Cookie] 检测到已保存的 Cookie ({len(saved_cookies)} 个)")

        # 验证 Cookie 是否有效（无头模式，客户无感知）
        driver = get_chrome_driver(visible=False)
        if driver:
            try:
                driver.get('https://m.weibo.cn')
                time.sleep(2)

                # 手动添加保存的 cookies
                for name, value in saved_cookies.items():
                    try:
                        driver.add_cookie({
                            'name': name,
                            'value': value,
                            'domain': '.weibo.cn'
                        })
                    except:
                        pass

                driver.refresh()
                time.sleep(3)

                # 检查 URL 是否还在登录页
                if 'login' not in driver.current_url.lower():
                    print("[Cookie] 已保存的 Cookie 有效")

                    # 获取完整的 cookies 转换为 requests 格式
                    cookie_jar = RequestsCookieJar()
                    for cookie in driver.get_cookies():
                        cookie_jar.set(cookie['name'], cookie['value'], domain=cookie.get('domain', '.weibo.cn'))

                    driver.quit()
                    return cookie_jar
                else:
                    print("[Cookie] 已保存的 Cookie 已失效，将删除并重新登录")
                    driver.quit()
                    # 删除失效的 Cookie 文件
                    if os.path.exists(cookie_file):
                        os.remove(cookie_file)
                        print(f"[Cookie] 已删除失效的 Cookie 文件: {cookie_file}")

            except Exception as e:
                print(f"[Cookie] 验证 Cookie 时出错: {e}")
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass

    # Cookie 无效或不存在，需要重新登录
    print("[Cookie] 正在启动自动登录（请用手机扫码）...")
    cookies = login_weibo()

    if cookies:
        # 转换为 requests 格式
        cookie_jar = RequestsCookieJar()
        for name, value in cookies.items():
            cookie_jar.set(name, value)
        return cookie_jar

    return None


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
