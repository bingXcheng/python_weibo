from flask import Flask,session,render_template,redirect,Blueprint,request
from utils.errorResponse import *
import time
from utils.query import querys
from db_config import get_user_table
ub = Blueprint('user',__name__,url_prefix='/user',template_folder='templates')

@ub.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        request.form = dict(request.form)
        username = (request.form.get('username') or '').strip()
        password = (request.form.get('password') or '').strip()
        if not username or not password:
            return errorResponse('输入的密码或账号出现问题')

        # 直接用 WHERE 条件精确查，不依赖 Python in 匹配
        tbl = get_user_table()
        if '"' in tbl:
            sql = f'select * from {tbl} where username = ? and password = ?'
            users = querys(sql, (username, password), 'select')
        else:
            sql = f'select * from {tbl} where username = %s and password = %s'
            users = querys(sql, (username, password), 'select')

        if not users:
            return errorResponse('输入的密码或账号出现问题')

        session['username'] = username
        session['createTime'] = users[0][-1]  # 最后一列是 createTime
        return redirect('/page/home', 301)
    else:
        return render_template('login.html')



@ub.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        request.form = dict(request.form)
        username = (request.form.get('username') or '').strip()
        password = (request.form.get('password') or '').strip()
        password_checked = (request.form.get('passwordCheked') or '').strip()
        if password != password_checked:
            return errorResponse('两次密码不符')
        tbl = get_user_table()
        if '"' in tbl:
            check_sql = f'select id from {tbl} where username = ?'
            users = querys(check_sql, (username,), 'select')
        else:
            check_sql = f'select id from {tbl} where username = %s'
            users = querys(check_sql, (username,), 'select')
        if users:
            return errorResponse('该用户名已被注册')
        time_tuple = time.localtime(time.time())
        time_str = str(time_tuple[0]) + '-' + str(time_tuple[1]) + '-' + str(time_tuple[2])
        if '"' in tbl:
            querys(
                f'insert into {tbl}(username,password,createTime) values(?,?,?)',
                (username, password, time_str),
                'insert'
            )
        else:
            querys(
                f'insert into {tbl}(username,password,createTime) values(%s,%s,%s)',
                (username, password, time_str),
                'insert'
            )
        return errorResponse('注册成功！')
        #return redirect('/user/login', 301)

    else:
        return render_template('register.html')

@ub.route('/logOut',methods=['GET','POST'])
def logOut():
    session.clear()
    return redirect('/user/login')