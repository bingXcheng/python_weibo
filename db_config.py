# -*- coding: utf-8 -*-
"""
统一数据库配置模块
支持 MySQL 主数据库 + SQLite 备选数据库
优先尝试 MySQL，连接失败时自动降级到 SQLite
"""
import os
import sys

# 当前项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────
# 数据库配置
# ─────────────────────────────────────────────

# MySQL 配置（主数据库）
MYSQL_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'root1'),
    'database': os.environ.get('DB_NAME', 'weiboarticle'),
}

# SQLite 配置（备选数据库，文件位于项目根目录）
SQLITE_PATH = os.path.join(BASE_DIR, 'db.sqlite3')

# 备用数据库表前缀（用于区分同一 SQLite 文件中的表，避免与原 MySQL 表名冲突）
# 目前 article、comments、user、sentiment_cache 四个表
SQLITE_TABLES = ['article', 'comments', 'user', 'sentiment_cache']

# ─────────────────────────────────────────────
# 数据库引擎（由 init_database() 初始化）
# ─────────────────────────────────────────────
_engine = None
_current_db = None  # 'mysql' 或 'sqlite'


def _create_sqlite_engine():
    """创建 SQLite 引擎"""
    try:
        from sqlalchemy import create_engine
        # sqlite:////absolute/path 或 sqlite:///relative/path
        abs_path = os.path.abspath(SQLITE_PATH)
        engine = create_engine(
            f'sqlite:///{abs_path}',
            connect_args={'check_same_thread': False}
        )
        # 初始化 SQLite 表结构
        _init_sqlite_tables(engine)
        return engine
    except Exception as e:
        print(f"[DB] SQLite 引擎创建失败: {e}")
        return None


def _init_sqlite_tables(engine):
    """初始化 SQLite 表结构（自动创建不存在的表）"""
    from sqlalchemy import text, inspect
    inspector = inspect(engine)

    # article 表
    if 'article' not in inspector.get_table_names():
        with engine.begin() as conn:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS article (
                    id INTEGER PRIMARY KEY,
                    likeNum INTEGER,
                    commentsLen INTEGER,
                    reposts_count INTEGER,
                    region TEXT,
                    content TEXT,
                    contentLen INTEGER,
                    created_at TEXT,
                    type TEXT,
                    detailUrl TEXT,
                    authorAvatar TEXT,
                    authorName TEXT,
                    authorDetail TEXT,
                    isVip INTEGER,
                    user_id INTEGER,
                    screen_name TEXT,
                    followers_count TEXT,
                    verified INTEGER DEFAULT 0,
                    sentiment REAL,
                    sentiment_label TEXT
                )
            '''))

    # comments 表
    if 'comments' not in inspector.get_table_names():
        with engine.begin() as conn:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS comments (
                    articleId TEXT,
                    created_at TEXT,
                    like_counts TEXT,
                    region TEXT,
                    content TEXT,
                    authorName TEXT,
                    authorGender TEXT,
                    authorAddress TEXT,
                    authorAvatar TEXT
                )
            '''))

    # user 表
    if 'user' not in inspector.get_table_names():
        with engine.begin() as conn:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS "user" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT,
                    createTime TEXT
                )
            '''))

    # sentiment_cache 表
    if 'sentiment_cache' not in inspector.get_table_names():
        with engine.begin() as conn:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS sentiment_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text_hash INTEGER UNIQUE,
                    text TEXT,
                    sentiment REAL,
                    sentiment_label TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))


def _create_mysql_engine():
    """创建 MySQL 引擎，失败时返回 None"""
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import OperationalError
        cfg = MYSQL_CONFIG
        conn_str = (
            f"mysql+pymysql://{cfg['user']}:{cfg['password']}"
            f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
            f"?charset=utf8mb4"
        )
        engine = create_engine(conn_str, pool_pre_ping=True)
        # 测试连接
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        print(f"[DB] MySQL 连接失败: {e}，将使用 SQLite 备选数据库")
        return None


def init_database():
    """
    初始化数据库引擎
    优先使用 MySQL，连接失败时自动降级到 SQLite
    """
    global _engine, _current_db

    # 1. 优先尝试 MySQL
    print("[DB] 正在连接 MySQL...")
    _engine = _create_mysql_engine()
    if _engine is not None:
        _current_db = 'mysql'
        print(f"[DB] ✅ MySQL 连接成功 ({MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']})")
        return _engine

    # 2. MySQL 失败，降级到 SQLite
    print("[DB] MySQL 连接失败，切换到 SQLite 备选数据库...")
    _engine = _create_sqlite_engine()
    if _engine is not None:
        _current_db = 'sqlite'
        print(f"[DB] ✅ SQLite 连接成功 ({SQLITE_PATH})")
        return _engine

    # 3. 全部失败
    _current_db = None
    print("[DB] ❌ 数据库全部连接失败！")
    return None


def get_engine():
    """获取当前数据库引擎（懒加载）"""
    global _engine
    if _engine is None:
        init_database()
    return _engine


def get_current_db():
    """获取当前使用的数据库类型"""
    global _current_db
    if _current_db is None:
        init_database()
    return _current_db


def is_mysql():
    return get_current_db() == 'mysql'


def is_sqlite():
    return get_current_db() == 'sqlite'


def querys(sql, params=None, type_='select'):
    """
    统一的数据库查询函数
    兼容 MySQL 和 SQLite，自动选择正确的数据库引擎
    """
    params = params or ()
    params = tuple(params)
    engine = get_engine()
    if engine is None:
        raise RuntimeError("数据库连接失败，所有数据库均不可用")

    from sqlalchemy import text
    with engine.connect() as conn:
        if type_.lower() != 'select':
            # INSERT / UPDATE / DELETE
            with engine.begin() as txn:
                txn.execute(text(sql), params)
            return '数据库语句执行成功'
        else:
            # SELECT
            result = conn.execute(text(sql), params)
            rows = result.fetchall()
            return rows


# 提前初始化（应用启动时）
init_database()
