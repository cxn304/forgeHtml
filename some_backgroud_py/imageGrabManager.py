# -*- coding:utf-8 -*-
"""
by:cxn
"""

import time, socket, threading, os
from multiprocessing.managers import BaseManager
from multiprocessing import freeze_support
from math import floor
from PIL import Image
import numpy as np


# 创建类似的QueueManager:
class QueueManager(BaseManager):
    pass


class SearchPort:
    def __init__(self):
        self.routers = []
        self.lock = threading.Lock()
        self.port_list = [6448]

    def search_routers(self):
        # 获取本地ip地址列表
        local_ip = socket.gethostbyname(socket.gethostname())
        all_threads = []  # 线程池

        for i in range(1, 255):
            array = local_ip.split('.')
            # 获取分割后的第四位数字，生成该网段所有可用IP地址
            array[3] = str(i)
            # 把分割后的每一可用地址列表，用"."连接起来，生成新的ip
            new_ip = '.'.join(array)
            # 遍历需要扫描的端口号列表
            for port in self.port_list:
                dst_port = int(port)
                # 循环创建线程去链接该地址
                t = threading.Thread(target=self.check_ip, args=(new_ip, dst_port))
                t.start()
                # 把新建的线程放到线程池
                all_threads.append(t)
        # 循环阻塞主线程，等待每一字子线程执行完，程序再退出
        for t in all_threads:
            t.join()

    def check_ip(self, new_ip, port):
        try:
            # 创建TCP套接字，链接新的ip列表
            scan_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 设置链接超时时间
            scan_link.settimeout(2)
            # 链接地址(通过指定我们 构造的主机地址，和扫描指定端口)
            result = scan_link.connect_ex((new_ip, port))
            scan_link.close()
            # 判断链接结果
            if result == 0:
                self.lock.acquire()
                print(new_ip, '\t\t端口号%s开放' % port)
                self.routers.append((new_ip, port))
                self.lock.release()
        except Exception as errs:
            print(errs)

    def returnAimIp(self):
        self.search_routers()
        for ipMessage in self.routers:
            host = socket.gethostbyaddr(ipMessage[0])
            hostName = host[0]
            if hostName == 'kotin':
                print('找到目标机')
                return ipMessage[0]


def SaveImg():
    QueueManager.register('get_task_queue')  # 由于这个QueueManager只从网络上获取Queue，所以注册时只提供名字:
    server_addr = SearchPort().returnAimIp()  # 连接到服务器，也就是运行exe的机器
    # server_addr = '192.168.1.18'
    print('Connect to server %s...' % server_addr)
    m = QueueManager(address=(server_addr, 6448), authkey=b'abc')  # 端口和验证码注意保持与exe设置的完全一致
    m.connect()  # 从网络连接:
    task = m.get_task_queue()  # 获取Queue的对象
    savePath = os.path.abspath(os.path.dirname(__file__))
    while True:
        try:
            if not task.empty():
                n = task.get(timeout=10)
                arr = np.array(n)
                im = Image.fromarray(arr)
                imageName = str(floor(time.time())) + '.jpg'
                im.save(savePath + '\\' + imageName, quality=95)
                print(imageName + ' is saved.')
                time.sleep(1)
            else:
                time.sleep(10)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    freeze_support()
    SaveImg()

