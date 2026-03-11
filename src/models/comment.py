from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AppStore(Enum):
    """应用市场枚举"""
    HUAWEI = "huawei"
    XIAOMI = "xiaomi"
    OPPO = "oppo"
    VIVO = "vivo"


class Game(Base):
    """游戏模型"""
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    package_name = Column(String(200), unique=True, nullable=False)
    app_store = Column(SQLEnum(AppStore), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Game(id={self.id}, name='{self.name}', store={self.app_store})>"


class Comment(Base):
    """评论模型"""
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(String(200), nullable=False)
    app_store = Column(SQLEnum(AppStore), nullable=False)
    rating = Column(Integer)  # 评分，可选
    comment_date = Column(DateTime)  # 评论时间，可选
    scraped_at = Column(DateTime, default=datetime.now, nullable=False)

    def is_within_months(self, months: int = 6) -> bool:
        """检查评论是否在指定月数内"""
        if not self.comment_date:
            return True  # 无日期则保留
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        return self.comment_date >= cutoff_date

    def __repr__(self):
        return f"<Comment(id={self.id}, user_id='{self.user_id}', content='{self.content[:20]}...')>"
