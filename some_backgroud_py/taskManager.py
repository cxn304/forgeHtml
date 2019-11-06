# -*- coding:UTF-8 -*-
import random, time
from multiprocessing.managers import BaseManager
import multiprocessing as mp

# 发送任务的队列:
task_queue = mp.Queue()
# 接收结果的队列:
result_queue = mp.Queue()

# 从BaseManager继承的QueueManager:
class QueueManager(BaseManager):
    pass

def return_task_queue():
    global task_queue
    return task_queue  # 返回发送任务队列

def return_result_queue ():
    global result_queue
    return result_queue # 返回接收结果队列

def runf():
    QueueManager.register('get_task_queue', callable=return_task_queue)
    QueueManager.register('get_result_queue', callable=return_result_queue)
    #绑定端口5000，设置验证密码'abc',要用byte格式
    manager = QueueManager(address=('192.168.1.16', 6000), authkey=b'abc')
    #Linux下address留空等于本机 Windows下不能留空 127.0.0.0即本机的地址
    #启动Queue
    manager.start()
    #通过网络获取Queue对象
    task = manager.get_task_queue()
    result = manager.get_result_queue()
    #开启示例任务，10代表要放10个任务进队列，每个计算机都可以从队列中取其中一个任务
    for i in range(10):
        n = random.randint(0, 10000)
        print('Put task %d to run...' %n)
        task.put(n)
    #读取任务结果，哪个计算机返回了任务，就立即读取
    print('Try to get results...')
    try:
        for i in range(10):
            a = time.time()
            r = result.get(timeout=10)  # timeout指的是秒，等待10秒--队列中是否有返回的数据
            print('Results: %s' % r + ', time: ' + str(time.time() - a))
        print('no error.')
    except Exception as e:  # 如果没有计算机连接，则会发生错误
        print('error is: ' + str(e))    # 打印不出错误
    manager.shutdown()
    print('master has been shoutDown')


# if __name__ == '__main__':
#     mp.freeze_support()
#     runf()

