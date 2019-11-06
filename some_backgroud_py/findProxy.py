# -*- coding:UTF-8 -*-
import requests, os, re, time, random
from threading import Thread


class findProxy:  # 采用多线程方式判断爬到的proxy是否可以用
    def __init__(self):
        self.canUseProxy = []
        self.USER_AGENTS = [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
            "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
        ]

    def getProxy(self):  # 获取整个网页
        head = {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Host': 'www.xicidaili.com',
            'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
            'Accept-Encoding': 'gzip,deflate',
            'Connection': 'keep-alive'
        }  # Host用来伪装
        r = requests.get('http://www.xicidaili.com/nn/', headers=head)
        return r.text

    @staticmethod
    def proxy_dict(html):
        proxyIp = re.findall(r'\d+\.\d+\.\d+\.\d+', html)  # findall适用于文本类型的数据  # 匹配ip地址
        proxyPort = re.findall(r'<td>\d+</td>', html)  # 匹配端口
        pTemp = ''.join(proxyPort)  # join的作用是把列表中的各个值连接起来成一个大字符串
        proxyDict = {}
        proxyDict.setdefault('http', [])
        proxyDict.setdefault('https', [])

        for i in range(len(proxyIp)):
            proxyPort = re.findall(r'\d+', pTemp)  # 从有<td>标签的proxyPort中把端口纯数字提取出来覆盖到proxyPort当中
            proxyUrl = 'http://{0}:{1}'.format(proxyIp[i],
                                               proxyPort[i])  # 传给requests的字典，不论http还是https，这里都是'http://{0}:{1}'
            proxyDict['http'].append(proxyUrl)  # 给字典循环赋值
            proxyDict.setdefault('http', [])  # 循环赋值中一定加上这句, setdefault确保了http键存在与字典中
            proxyDict['https'].append(proxyUrl)  # 给字典循环赋值 https
            proxyDict.setdefault('https', [])  # 循环赋值中一定加上这句

        return proxyDict

    def openProxy(self, Dict, i):
        try:
            head = {
                "User-Agent": random.choice(self.USER_AGENTS),
                "Referer": "http://ip.tool.chinaz.com/",
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'Connection': 'keep-alive'
            }
            proxy = Dict['http'][i]
            proxies = {'http': proxy,
                       'https': proxy}
            content = requests.get('http://ip.tool.chinaz.com/' + proxy, headers=head, proxies=proxies, timeout=50)
            # get函数的是返回Response格式的东西
            # content.encode()
            print(proxy)
            self.canUseProxy.append(proxy)
        except Exception as e:
            1

    def rightProxy(self):
        html = self.getProxy()
        myDict = self.proxy_dict(html)
        nLoops = len(myDict['http'])
        threads = []
        sTime = time.time()
        # 开启多线程
        for j in range(nLoops):
            t = Thread(target=self.openProxy, args=(myDict, j,))
            threads.append(t)
        for j in range(nLoops):
            # 此处有一个坑，即如果同时有N个子线程join(timeout），那么实际上主线程会等待的
            # 超时时间最长为 N ＊ timeout， 因为每个子线程的超时开始时刻是上一个子线程超时结束的时刻。
            threads[j].setDaemon(True)
            threads[j].start()
        # for j in range(nLoops):     # 等所有线程运行完毕
        #     threads[j].join()

        time.sleep(5)  # 5秒就结束所有子线程
        print('use ' + str(time.time() - sTime) + ' seconds')
        return self.canUseProxy

# fProxies = findProxy().rightProxy()
