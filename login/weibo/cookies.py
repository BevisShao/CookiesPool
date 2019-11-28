import time
import json
from io import BytesIO
from PIL import Image
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os.path import abspath, dirname
import requests
from lxml import etree
from captcha.chaojiying import Chaojiying_Client
from utils.cookies import utils_cookies
import os

TEMPLATES_FOLDER = dirname(abspath(__file__)) + '/templates/'


class WeiboCookies():

    def __init__(self, username, password, browser):
        self.url = 'https://weibo.com/'
        self.browser = browser
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password
        self.count = 0              # 计数器，协助计算当前main（）方法是因为断网后第几次执行

    def quit_loginin(self):
        cookies = self.browser.get_cookies()
        print('当前的cookies: {}'.format(cookies))
        if cookies:
            cookies = utils_cookies.process_cookies(cookies)
            cookies = json.dumps(cookies)
            cookies = json.loads(cookies)
            reqs = requests.get('https://weibo.com/logout.php?backurl=%2F', cookies=cookies, allow_redirects=True)      # 当前的逻辑是：获得当前账号的cookies发送退出登陆请求，但是按照log显示，这里请求有问题，code打不出来，
                                                                                                                         # 但是整个池已经正常运作，可以依次获得cookies了。
            code = reqs.status_code
            text = reqs.content
            # with open('logout_respons.txt', 'w') as f:
            #     f.write(text)
            print(code)
            return '退出登陆后的状态码：{}'.format(code)
        else:
            return

    # 获得验证码的链接
    def get_yzm_url(self):
        text = self.browser.page_source
        html = etree.HTML(text)
        yzm_url = html.xpath('//img[contains(@action-type, "btn_change_verifycode")]/@src')     # 这个地址每次点击的结果都不一样！
        print('当前验证码的链接为： {}'.format(yzm_url))
        return yzm_url

    # 根据链接获得验证码图片
    def get_yzm(self):
        yzm_url = self.get_yzm_url()
        resqs = requests.get(yzm_url[0], stream=True)
        if resqs.status_code == 200:
            file = BytesIO(resqs.content)
            img = Image.open(file)
            img = img.convert('RGB')
            img.save(r'E:\InstallLocation\PyCharm\Spiders\CookiesPool-master\login\weibo\yzmImages\yzm.jpg')
            print('验证码图片已保存。')
        else:
            print('验证码图片下载异常')
        return img

    # 将图片传给超级鹰的后台：
    def upload_yzm(self):
        self.chaojiying = Chaojiying_Client('your_name', 'your_psw', 'others')  # 用户中心>>软件ID 生成一个替换 96001
        im = open(r'E:\InstallLocation\PyCharm\Spiders\CookiesPool-master\login\weibo\yzmImages\yzm.jpg', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
        imdict = self.chaojiying.PostPic(im, 1902)   # 1902 验证码类型  官方网站>>价格体系 3.4+版 print 后要加()
        print(imdict, '超级鹰后台返回数据')
        imgSummary = imdict.get('pic_str')
        imgID = imdict.get('pic_id')
        print('imgSummary is :{}'.format(imgSummary))
        return {'imgSummary': imgSummary, 'imgID': imgID}

    def open(self):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        # self.quit_loginin()
        self.browser.delete_all_cookies()
        self.browser.get(self.url)
        # self.browser.delete_all_cookies()
        try:
            # time.sleep(10)
            print('等待用户名控件')
            username = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, 'loginname'))
                # EC.presence_of_element_located((By.XPATH, '//div[@class="input_wrap"]/input[@id="loginname" and @class="W_input"]'))
                # EC.visibility_of(self.browser.find_element(By.XPATH, '//div[@class="input_wrap"]/input[@id="loginname" and @class="W_input"]')) # 耗时比上一步多，刚好获取不到控件
            )
            # print('username: {}'.format(username))
            print('等待密码控件')
            password = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.info_list.password .input_wrap .W_input')))
            submit = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[@node-type="normal_form"]//a[contains(@class, "btn_32px")]'))
                # 此处的div元素的class值与短信验证码的元素class值一样，所以一直取不到submit，20190624
            )
            print('submit: {}'.format(submit))
            username.send_keys(self.username)
            password.send_keys(self.password)
            try:
                yzmneed = WebDriverWait(self.browser, 1.5).until(EC.visibility_of(self.browser.find_element(By.CSS_SELECTOR, '.input_wrap.W_fl .W_input')))
                print('yzmneed: {}'.format(yzmneed))
                if yzmneed:
                    cycle = True
                    while (cycle):
                        self.get_yzm()
                        [yzmsummary, yzmID] = self.upload_yzm().values()
                        print('修改后的图片验证码和id： {} ： {}'.format(yzmsummary, yzmID))
                        yzminput = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.input_wrap.W_fl .W_input')))
                        # yzminput.send_keys(yzmsummary + 'sszzz2')
                        yzminput.send_keys(yzmsummary)
                        submit.click()
                        time.sleep(2)
                        cycle = self.yzm_error()
                        if cycle:
                            self.chaojiying.PostPic(yzmID)
                            print('验证码识别错误,图片ID为：{}'.format(yzmID))
                        else:
                            if yzmsummary:
                                os.rename(
                                    r'E:\InstallLocation\PyCharm\Spiders\CookiesPool-master\login\weibo\yzmImages\yzm.jpg',
                                    r'E:\InstallLocation\PyCharm\pictures-weibo\{}.jpg'.format(yzmsummary))
                    self.show_welcome()
                self.count = 0
            except TimeoutException as e:
                print('未出现验证码控件')
                submit.click()
                if self.password_error():
                    print('账号或密码错误')

        except TimeoutException as e:
            self.count += 1
            print('登陆时发生网络等待异常，请检查网络,正在重试：{}；{} '.format(self.count, e.stacktrace))
            self.browser.delete_all_cookies()
            # self.browser.close()
            self.main()

    def yzm_error(self):
        # 判断登陆验证码是否错误
        try:
            return WebDriverWait(self.browser, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.input_wrap.W_fl .W_input'))) or \
                   WebDriverWait(self.browser, 1).until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'main_txt'), '输入的验证码不正确'))     # 这两个条件满足任意一个都可以认为验证码校验错误
        except TimeoutException:
            return False

    def password_error(self):
        """
        判断是否密码错误
        :return:
        """
         # W_ficon ficon_close S_ficon

        try:
            password_error_text = WebDriverWait(self.browser, 1).until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, 'main_txt'), '用户名或密码错误'))
            password_error_cancel = WebDriverWait(self.browser, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.W_ficon.ficon_close.S_ficon'))
            )
            print('password_error_cancel {}'.format(password_error_cancel))
            if password_error_text:
                print('password_error_cancel {}'.format(password_error_cancel))
                self.browser.execute_script('arguments[0].click()', password_error_cancel)      # 普通的点击无效，用这个。
            return password_error_text
        except TimeoutException:
            return False
    
    def login_successfully(self):
        """
        判断是否登录成功
        :return:
        """
        print("成功与否判断")
        usrbt = WebDriverWait(self.browser, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.WB_innerwrap .nameBox')))    # fold_cont clearfix
        print('usrbt: {}'.format(usrbt))
        try:
            return usrbt
        except TimeoutException:
            return False

        # 新号初次登陆，验证码环节通过后，会有个欢迎进入微博的页面
    def show_welcome(self):
        # W_btn_big
        try:
            welcome = WebDriverWait(self.browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, 'W_btn_big')))
            if welcome:
                welcome.click()
                return True
        except TimeoutException:
            return False

    def get_cookies(self):
        """
        获取Cookies
        :return:
        """
        return self.browser.get_cookies()
    
    def main(self):
        """
        破解入口
        :return:
        """
        self.open()
        if self.password_error():
            print('用户名或密码错误')
            self.browser.quit()
            return {
                'status': 2,
                'content': '用户名或密码错误'
            }
        # 如果不需要验证码直接登录成功
        elif self.login_successfully():
            print('登陆成功。')
            cookies = self.get_cookies()
            self.browser.quit()
            return {
                'status': 1,
                'content': cookies
            }
        else:
            return {
                'status': 3,
                'content': '其他错误'
            }
        # else:
        #     # 现在添加了点击按钮 来验证登陆20190521
        #     try:
        #         clickbut = WebDriverWait(self.browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_radar_tip')))
        #         clickbut.click()    # 代码走到这，又跳出来个拖动有验证码。看来极验验证码需要专门针对写套带码了。
        #     except TimeoutException:
        #         print('无登陆后的极验验证码程序，继续登陆流程。')
        #     cookies = self.get_cookies()
        #     print('是不是走到了这。。。')
        #     return {
        #         'status': 2,
        #         'content': '这是错误的。'
        #     }


if __name__ == '__main__':
    driver_path = 'E:\InstallLocation\Chrome\_71_0_3578\chromedriver.exe'
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
    browser.maximize_window()
    result = WeiboCookies(username='username', password='password', browser=browser).main()

    print(result)

