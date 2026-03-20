# spider.py
from flask import Blueprint, Response
import threading

# 创建线程安全的进度队列
from queue import Queue
progress_queue = Queue()

from flask import Blueprint

sb= Blueprint(
    'spider',
    __name__,
    url_prefix='/spider',
    template_folder='templates'
)


@sb.route('start', methods=['POST'])
def start_spider():
    # 启动爬虫线程
    threading.Thread(target=spider_worker).start()
    return {'status': 'started'}, 202

@sb.route('progress')
def progress_stream():
    def generate():
        while True:
            progress = progress_queue.get()
            if progress is None:
                break
            yield "data: {}\n\n".format(progress)
    return Response(generate(), mimetype="text/event-stream")


def spider_worker():
    import sys
    import os
    # 获取当前文件(spider.py)所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 添加父目录到Python路径
    sys.path.insert(0, os.path.dirname(current_dir))

    try:
        from spider.main import main
        for progress in main():
            progress_queue.put(progress)
    except Exception as e:
        progress_queue.put("ERROR: {}".format(str(e)))
    finally:
        progress_queue.put(None)