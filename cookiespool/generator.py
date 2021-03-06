import json
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from cookiespool.config import *
from cookiespool.db import RedisClient
from login.weibo.cookies import WeiboCookies
import time
import os
from cookiespool.config import PHANTOMJS_HOST


class CookiesGenerator(object):
    def __init__(self, website='default'):
        """
        父类, 初始化一些对象
        :param website: 名称
        :param browser: 浏览器, 若不使用浏览器则可设置为 None
        """
        self.website = website
        self.cookies_db = RedisClient('cookies', self.website)
        self.accounts_db = RedisClient('accounts', self.website)
        self.init_browser()

    def __del__(self):
        self.close()
    
    def init_browser(self):
        """
        通过browser参数初始化全局浏览器供模拟登录使用
        :return:
        """
        self.host = os.environ.get('ISDOCKER')
        print('host = ', self.host)
        self.caps = DesiredCapabilities.PHANTOMJS
        self.caps["phantomjs.page.settings.userAgent"] = \
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        if BROWSER_TYPE == 'PhantomJS':
            if self.host:
                # self.browser = webdriver.Remote(
                    # command_executor='http://{}:8910'.format(PHANTOMJS_HOST), desired_capabilities=self.caps)
                self.browser = webdriver.PhantomJS(desired_capabilities=self.caps)

            else:
                self.browser = webdriver.PhantomJS(desired_capabilities=self.caps)
            # self.browser.set_window_size(1400, 500)
            self.browser.maximize_window()
        elif BROWSER_TYPE == 'Chrome':
            # driver_path = 'E:\InstallLocation\Chrome\_71_0_3578\chromedriver.exe'
            chrome_options = Options()
            # chrome_options.add_argument('--headless')
            chrome_options.add_argument('disable-infobars')     # 去除‘自动化测试’字样
            chrome_options.add_argument('window-size=1920,1080')
            # chrome_options.add_argument('--disable-gpu')
            self.browser = webdriver.Chrome(chrome_options=chrome_options)
            self.browser.maximize_window()
            # self.browser.fullscreen_window()

    def new_cookies(self, username, password):
        """
        新生成Cookies，子类需要重写
        :param username: 用户名
        :param password: 密码
        :return:
        """
        raise NotImplementedError
    
    def process_cookies(self, cookies):
        """
        处理Cookies
        :param cookies:
        :return:
        """
        dict = {}
        for cookie in cookies:
            dict[cookie['name']] = cookie['value']
        return dict
    
    def run(self):
        """
        运行, 得到所有账户, 然后顺次模拟登录
        :return:
        """
        accounts_usernames = self.accounts_db.usernames()
        cookies_usernames = self.cookies_db.usernames()
        
        for username in accounts_usernames:
            if not username in cookies_usernames:
                password = self.accounts_db.get(username)
                print('正在生成Cookies', '账号', username, '密码', password)
                result = self.new_cookies(username, password)
                # 成功获取
                if result.get('status') == 1:
                    cookies = self.process_cookies(result.get('content'))
                    print('成功获取到Cookies', cookies)
                    if self.cookies_db.set(username, json.dumps(cookies)):
                        print('成功保存Cookies')
                        # self.browser.delete_all_cookies()   # 原程序没有这句，运行后在第二个账号密码对登陆时是没有登陆框的。20190624
                        time.sleep(0.5)
                        # handles = self.browser.current_window_handle
                        # self.browser.close()
                        self.close()

                # 密码错误，移除账号
                elif result.get('status') == 2:
                    print(result.get('content'))
                    self.close()
                    if self.accounts_db.delete(username):
                        print('成功删除账号')
                else:
                    with open('wangluo_error.html', 'w') as f:
                        f.write(self.browser.page_source)
                    self.close()
                    print('关闭浏览器后：', result.get('content'))
        else:
            print('所有账号都已经成功获取Cookies')
    
    def close(self):
        """
        关闭
        :return:
        """
        try:
            print('Closing Browser')
            if self.__dict__.get('browser'):
                self.browser.close()
                self.browser.quit()
                del self.browser
        except TypeError:
            print('Browser not opened')


class WeiboCookiesGenerator(CookiesGenerator):
    def __init__(self, website='weibo'):
        """
        初始化操作
        :param website: 站点名称
        :param browser: 使用的浏览器
        """
        CookiesGenerator.__init__(self, website)
        self.website = website
    
    def new_cookies(self, username, password):
        """
        生成Cookies
        :param username: 用户名
        :param password: 密码
        :return: 用户名和Cookies
        """
        return WeiboCookies(username, password, self.browser).main()


if __name__ == '__main__':
    generator = WeiboCookiesGenerator()
    generator.run()
