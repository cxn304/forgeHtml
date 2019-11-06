# -*- coding:utf-8 -*-
"""
by:cxn
此文件放根目录下
ctrl+alt+l 格式化代码
"""
import requests, random, time, os
from findProxy import findProxy
import multiprocessing as mp

https = []
http = []


def registerT():
    fProxy = findProxy().rightProxy()
    for i in range(len(fProxy)):
        b = fProxy[i].split('//')[1]
        t = {'https': b}
        r = {'http': b}
        https.append(t)
        http.append(r)
    registerHead = {  # 请求头要补全
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        'Origin': 'http://113.59.104.129:8055',
        'Referer': 'http://113.59.104.129:8055/SvrCenter/Accounts/Sync/Register',
        "Connection": "keep-alive",
        "charset": "UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    }
    registerData = {
        'Phone': str(int(random.random() * 10e11)),
        'Password': "'while(true);//",
        'Account': 'zhouyansima',
        'name': 'zhouyansima'
    }
    rurl = 'http://113.59.104.129:8055/SvrCenter/Accounts/Sync/Register'
    if rurl.split(':')[0] == 'https':
        page_all = requests.post(url=rurl, headers=registerHead, data=registerData, proxies=random.choice(https))
    else:
        page_all = requests.post(url=rurl, headers=registerHead, data=registerData, proxies=random.choice(http))
    return page_all


def loginT():
    fProxy = findProxy().rightProxy()
    for i in range(len(fProxy)):
        b = fProxy[i].split('//')[1]
        t = {'https': b}
        r = {'http': b}
        https.append(t)
        http.append(r)
    lurl = 'http://113.59.104.129:8075/api/base/login'
    loginData = {
        'Account': "933565705942",
        'Token': "14B7DDE5AF94FC910AE0BEA0BC2F8BA607E1EF85",
        'ID': "aabf00ad-a140-4581-b54c-ef43d1f9dc99",
        'name': "'while(true);//"
    }
    loginHead = {  # 请求头要补全
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        'Origin': 'http://113.59.104.129:8075',
        'Referer': 'http://113.59.104.129:8075/api/base/login',
        "Connection": "keep-alive",
        "charset": "UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    }
    if lurl.split(':')[0] == 'https':
        page_all = requests.post(url=lurl, headers=loginHead, data=loginData, proxies=random.choice(https))
    else:
        page_all = requests.post(url=lurl, headers=loginHead, data=loginData, proxies=random.choice(http))
    return page_all


def job(lastingTime):  # 测试多进程
    a = time.time()
    while True:
        if time.time() - a > lastingTime:
            return time.time() - a


'''
在Windows上要想使用进程模块，就必须把有关进程的代码写在当前.py文件的if __name__ == ‘__main__' :语句的下面，
才能正常使用Windows下的进程模块。Unix/Linux下则不需要。
进程池和线程池都是好东西
'''
if __name__ == '__main__':
    mp.freeze_support()
    useCount = mp.cpu_count() - 3
    pool = mp.Pool(useCount)
    lastTime = [10] * (useCount + 2)  # 如果执行任务的数量超过池子容量，则等池子容量里的东西运行完后才执行剩下的任务
    result = pool.map(job, lastTime)
    pool.close()  # 调用join之前，先调用close函数，否则会出错。
    pool.join()

# Finally = loginT()
