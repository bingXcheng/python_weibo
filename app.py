import os
import warnings
import re

# matplotlib 字体缓存写入 /tmp，避免占用进程内存
os.environ["MPLCONFIGDIR"] = "/tmp/mpl_cache"

# 抑制第三方包的 SyntaxWarning（jieba、pyparsing 等）
warnings.filterwarnings("ignore", category=SyntaxWarning)

from flask import Flask, session, render_template, redirect, request

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'This is a app.secret_Key , You Know ?')

from views.page import page
from views.user import user
from spider import spider
app.register_blueprint(page.pb)
app.register_blueprint(spider.sb)
app.register_blueprint(user.ub)


@app.route('/')
def index():
    return redirect('/user/login')


@app.before_request
def before_request():
    pat = re.compile(r'^/static')
    if re.search(pat, request.path):
        return
    if request.path == '/user/login':
        return
    if request.path == '/user/register':
        return
    uname = session.get('username')
    if uname:
        return None

    return redirect('/user/login')


@app.route('/<path:path>')
def catch_all(path):
    return render_template('404.html')


@app.route('/health')
def health():
    return '', 200


if __name__ == '__main__':
    # HTTPS 支持（通过环境变量控制）
    # 设置 HTTPS_MODE=1 启用 HTTPS，或通过 gunicorn/waitress 等生产服务器部署
    use_https = os.environ.get('HTTPS_MODE', '0') == '1'
    ssl_cert = os.environ.get('SSL_CERT', 'deploy/ssl/server.crt')
    ssl_key = os.environ.get('SSL_KEY', 'deploy/ssl/server.key')

    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', os.environ.get('FLASK_PORT', 5000)))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'

    if use_https and os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        print(f"[APP] 启动 HTTPS 服务 ({ssl_cert})")
        app.run(host=host, port=port, debug=debug, ssl_context=(ssl_cert, ssl_key))
    else:
        if use_https:
            print("[APP] ⚠️  SSL 证书文件不存在，切换为 HTTP 模式")
        print(f"[APP] 启动 HTTP 服务 (http://{host}:{port})")
        app.run(host=host, port=port, debug=debug)
