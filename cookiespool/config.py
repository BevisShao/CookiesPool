# Redis数据库地址
# REDIS_HOST = 'localhost'
REDIS_HOST = '192.168.0.112'

# Redis端口
REDIS_PORT = 6379

# Redis密码，如无填None
REDIS_PASSWORD = None

PHANTOMJS_HOST_DOCKER = 'phantomjs'
PHANTOMJS_HOST = '192.168.0.112'

# IPsPool
# IPSPOOL_HOST = '172.17.0.2'
IPSPOOL_HOST_DOCKER = 'ipspool'
IPSPOOL_HOST = '192.168.0.112'
IPSPOOL_PORT = 5555

# 产生器使用的浏览器
BROWSER_TYPE = 'PhantomJS'
# BROWSER_TYPE = 'Chrome'

# 产生器类，如扩展其他站点，请在此配置
GENERATOR_MAP = {
    'weibo': 'WeiboCookiesGenerator'
}

# 测试类，如扩展其他站点，请在此配置
TESTER_MAP = {
    'weibo': 'WeiboValidTester'
}

TEST_URL_MAP = {
    'weibo': 'https://weibo.com/'
}

# 产生器和验证器循环周期
CYCLE_GENERA = 14400
CYCLE_TEST = 14400
CYCLE = 120

# API地址和端口
API_HOST = '0.0.0.0'
API_PORT = 5000

# 产生器开关，模拟登录添加Cookies
GENERATOR_PROCESS = True
# 验证器开关，循环检测数据库中Cookies是否可用，不可用删除
VALID_PROCESS = True
# API接口服务
API_PROCESS = True
