"""
DB Query Wrapper - 统一的数据库访问接口
"""

from .core import Database, QueryResult, DatabaseError

__all__ = ["Database", "QueryResult", "DatabaseError"]
__version__ = "1.2.0"