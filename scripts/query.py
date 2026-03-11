#!/usr/bin/env python3
"""查询已采集的评论数据"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.comment import Base, Game, Comment, AppStore


def query_stats(db_path: str = "data/comments.db"):
    """查询统计信息"""
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    print("=== Database Statistics ===\n")

    # 游戏数量
    game_count = session.query(Game).count()
    print(f"Total games: {game_count}\n")

    # 按应用市场统计
    print("Games by app store:")
    for store in AppStore:
        count = session.query(Game).filter_by(app_store=store).count()
        if count > 0:
            print(f"  {store.value}: {count}")

    print()

    # 评论数量
    comment_count = session.query(Comment).count()
    print(f"Total comments: {comment_count}\n")

    # 按游戏统计评论数
    if game_count > 0:
        print("Comments by game:")
        games = session.query(Game).all()
        for game in games:
            count = session.query(Comment).filter_by(game_id=game.id).count()
            print(f"  {game.name} ({game.app_store.value}): {count} comments")

    session.close()


if __name__ == "__main__":
    query_stats()
