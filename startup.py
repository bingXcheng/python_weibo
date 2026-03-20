"""启动脚本：gunicorn 生产服务器，端口由 Render 环境变量 $PORT 提供"""
import os
import sys

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_cache")

# 静默压制第三方包的 SyntaxWarning（jieba / pyparsing 等，Python 3.14 兼容性）
import warnings as _warnings
_warnings.filterwarnings("ignore", category=SyntaxWarning)

# 启动 gunicorn（1 worker 保证低内存，/tmp 用于字体缓存）
sys.exit(os.system(
    "gunicorn app:app --bind 0.0.0.0:$PORT "
    "--workers 1 --threads 1 --timeout 30"
))
