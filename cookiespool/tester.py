import json
import requests
from requests.exceptions import ConnectionError
from cookiespool.db import *
from utils import ips as iputil
from utils import proxies_requests as  pr


class ValidTester(object):
    def __init__(self, website='default'):
        self.website = website
        self.cookies_db = RedisClient('cookies', self.website)
        self.accounts_db = RedisClient('accounts', self.website)
    
    def test(self, username, cookies):
        raise NotImplementedError
    
    def run(self):
        cookies_groups = self.cookies_db.all()
        if cookies_groups:
            for username, cookies in cookies_groups.items():
                self.test(username, cookies)
        else:
            # Scheduler.generate_cookie(cycle=CYCLE_GENERA)
            print("cookies枯竭...")


class WeiboValidTester(ValidTester):
    def __init__(self, website='weibo'):
        ValidTester.__init__(self, website)
    
    def test(self, username, cookies):
        print('正在测试Cookies', '用户名', username)
        try:
            cookies = json.loads(cookies)
        except TypeError:
            print('Cookies不合法', username)
            self.cookies_db.delete(username)
            print('删除Cookies', username)
            return
        try:
            test_url = TEST_URL_MAP[self.website]
            headers = {
                'Host': 'weibo.com',
                # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
                # "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
                # 'x-requested-with': 'XMLHttpRequest',  # ajxa
                'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/81.0.4044.138 Chrome/81.0.4044.138 Safari/537.36'
                'scheme': 'https',
                # 'X-Forwarded-For': '-',
                'Connection': 'keep-alive',
                # 'TE': 'Trailers',
                'Upgrade-Insecure-Requests': 1,
                'authority': 'weibo.com',
                'method': 'GET',
                'path': '/'

            }
            proxies = iputil.get_proxy()
            print('获得的代理IP： {}'.format(proxies))
            # response1 = requests.get('http://httpbin.org/get', proxies=proxies, )
            # print('httpbin的报文：{}'.format(response1.text))
            s = requests.session()
            requests.DEFAULT_RETRIES = 5
            s.keep_alive = False
            response = s.get(test_url, cookies=cookies, timeout=5, allow_redirects=True)
            # response = pr.get(url=test_url, cookies=cookies, timeout=5, allow_redirects=True)
            current_url = response.url
            print('此时的网页url为：{}'.format(current_url))
            if test_url in current_url:
                # 重定向后的url包含testurl，说明，当前cookies有效
                print('Cookies有效', username)
            else:
                self.cookies_db.delete(username)
                print('删除Cookies', username)
            # status_code = response.status_code
            # if status_code == 200:
            #     print('Cookies有效', username)
            # elif status_code == 302:
            #     print(response.status_code, response.headers)
            #     print('当前{}用户的cookies发生302重定向，定向后的url：{}'.format(username, response.url))
            # else:
            #     # self.cookies_db.delete(username)
            #     print('删除Cookies', username)
        except ConnectionError as e:
            print('发生异常', e.args)


if __name__ == '__main__':
    WeiboValidTester().run()
