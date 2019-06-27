# -*- coding:utf-8 -*-
"""
by:cxn
此文件放根目录下
"""

from flask import Flask, request, render_template, send_from_directory, session, flash, redirect, url_for, g
import os, sqlite3, threading, time
import forgePost, settings    # 自己写的放在同一个文件夹下即可

app = Flask(__name__)   # 创建该类的实例
app.config.from_object(settings)   # 使用模块的名字引入config


@app.route('/hello/<i_d>')   # app.route装饰器映射URL和执行的函数。这个设置将/hello URL映射到了hello_world函数上
def hello_world(i_d):        # 这个函数的名字也在生成 URL 时被特定的函数采用
    return 'Hello World: %s' % i_d  # URL传参


@app.route('/', methods=['POST', 'GET'])    # app.route是一个装饰器函数，被它修饰的函数最终都会被替换成decorator函数
def forge_post():
    return render_template('BasicApplication.html'), 404     # 在根目录下面的文件


root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "html")   # static/html是个文件夹
@app.route('/htmltest')
def home():
    return send_from_directory(root, "BasicApplication.html")   # BasicApplication.html在static/html文件夹下


# 使用render_template 函数渲染模板。注意：只需要填写模板的名字，不需要填写templates这个文件夹的路径
@app.errorhandler(404)      # 重定向，若找不到页面，则重定向至'./BasicApplication.html'
def not_found(error):
    return render_template('BasicApplication.html'), 404


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = '用户名错误'
        elif request.form['password'] != app.config['PASSWORD']:
            error = '密码错误'
        else:
            session['logged_in'] = True
            flash('登录成功')
            return redirect(url_for('login'))    # 通过函数名构造url，如/login/,还可以加载静态文件
    return render_template('login.html', error=error)   # 若用户名不对，则返回登录界面


def connect_db():
    """Connects to the specific database.DATABASE这个数据库放在哪里"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    with app.app_context():     # 建立应用环境，with语句--数据库连接在提交后断开。 g对象会与app关联
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:    # 打开应用提供的资源
            db.cursor().executescript(f.read())
        db.commit()


"""
g：global 
1. g对象是专门用来保存用户的数据的。 
2. g对象在一次请求中的所有的代码的地方，都是可以使用的。
"""
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):     # 判断g对象中是否存在name属性
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """每次应用环境销毁时断开连接"""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def start_forge_post():
    while 1:
        forgePost.main_code()
        time.sleep(50 * 60)


"""
其中 if __name__ == '__main__': 确保服务器只会在该脚本被Python解释器直接执行的时候才会运行，而不是作为模块导入的时候。
"""
if __name__ == '__main__':
    tokenGet = threading.Thread(target=start_forge_post)    # 开启另一个线程
    tokenGet.setDaemon(True)    # 主线程结束以后，子线程还没有来得及执行，整个程序就退出，setDaemon要在start前
    tokenGet.start()
    app.run(host='0.0.0.0')     # 这会让操作系统监听所有公网 IP
    # tokenGet.join()   # join方法意义是：主线程一直等待全部的子线程结束之后，主线程自身才结束，程序退出
