# CookiesPool

可扩展的Cookies池，目前对接了新浪微博，[weibo.com](https://www.weibo.com)，可自行扩展其他站点


## 基础配置 

### 接口基本配置

```python
# Redis数据库地址
REDIS_HOST = 'localhost'

# Redis端口
REDIS_PORT = 6379

# Redis密码，如无填None
REDIS_PASSWORD = 'foobared'

# 产生器使用的浏览器
BROWSER_TYPE = 'Chrome'

# 产生器类，如扩展其他站点，请在此配置
GENERATOR_MAP = {
    'weibo': 'WeiboCookiesGenerator'
}

# 测试类，如扩展其他站点，请在此配置
TESTER_MAP = {
    'weibo': 'WeiboValidTester'
}

# 检测器检测接口
TEST_URL_MAP = {
    'weibo': 'https://weibo.com/'
}

# 产生器和验证器循环周期
CYCLE = 120

# API地址和端口
API_HOST = '0.0.0.0'
API_PORT = 5000

```

### 进程开关

在config.py修改

```python
# 产生器开关，模拟登录添加Cookies
GENERATOR_PROCESS = True
# 验证器开关，循环检测数据库中Cookies是否可用，不可用删除
VALID_PROCESS = True
# API接口服务
API_PROCESS = True
```


## 导入账号
```

在accunts.txt文件里按照如下格式列出账号密码对：
18412345678----abcdef3647

账号 18412345678 密码 abcdef3647
录入成功

```


## 运行

请先导入一部分账号之后再运行，运行命令：

```
python3 run.py
```

## 运行效果

三个进程全部开启：


```
API接口开始运行
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
Cookies生成进程开始运行
Cookies检测进程开始运行
```
