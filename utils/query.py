# -*- coding: utf-8 -*-
"""
数据库查询模块
统一使用 db_config.py 中的双数据库支持（MySQL 优先 + SQLite 备选）
"""
from db_config import querys

__all__ = ['querys']
