import requests
import utils.ips as iputil


def get(**kwargs):
    proxies = iputil.get_proxy()
    if proxies:
        return requests.get(proxies=proxies, **kwargs)
    else:
        print('这里是自定义的代理型requests.get()，请检查代理池是否运行')
        return requests.get(**kwargs)


def post(**kwargs):
    proxies = iputil.get_proxy()
    if proxies:
        return requests.get(proxies=proxies, **kwargs)
    else:
        print('这里是自定义的代理型requests.post()，请检查代理池是否运行')
        return requests.post(**kwargs)
