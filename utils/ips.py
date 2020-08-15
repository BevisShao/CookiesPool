import requests
from lxml import etree
from cookiespool.config import IPSPOOL_HOST, IPSPOOL_PORT

# 通过IP池对外接口获得可用IP地址
def get_IP():
    url = 'http://{}:{}/random'.format(IPSPOOL_HOST, IPSPOOL_PORT)
    print('代理池接口地址：', url)
    reqs = requests.get(url=url)
    code = reqs.status_code
    print('代理池界面响应码：', code)
    if code == 200:
        # html = etree.HTML(reqs.text)
        # print(reqs.content)
        # print(html)
        # ip_text = html.xpath('/body[1]/text()')
        print('随机到的ip_text: {}'.format(reqs.text))
        return reqs.text
    else:
        print('未获取到IP地址，请检查IP池是否已开启。')
        return

def get_proxy():
    proxy = str(get_IP())
    if proxy:
        proxies = {
            'http': 'http://' + proxy,
            'https': 'https://' + proxy,
        }
        return proxies
    else:
        return

