"""启动脚本：预热 matplotlib 字体缓存后启动 gunicorn"""
import matplotlib
import matplotlib.font_manager
import os

# 确保字体缓存写到 /tmp（内存友好）
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_cache")

# 预热字体缓存（同步执行，避免 gunicorn worker 中首次请求时构建）
print("[Startup] 正在预热 matplotlib 字体缓存...")
try:
    fm = matplotlib.font_manager.fontManager
    _ = fm.findfont("DejaVu Sans")  # 触发字体缓存构建
    print("[Startup] matplotlib 字体缓存预热完成")
except Exception as e:
    print(f"[Startup] matplotlib 预热警告（非致命）: {e}")

# 启动 gunicorn
import sys
sys.exit(os.system(
    'gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 1 --timeout 30'
))
