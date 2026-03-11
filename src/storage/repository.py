from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.comment import Game, Comment, AppStore


class CommentRepository:
    """评论数据仓库"""

    def __init__(self, session: Session):
        self.session = session

    def save_game(self, game: Game) -> Game:
        """保存游戏信息"""
        self.session.add(game)
        self.session.commit()
        self.session.refresh(game)
        return game

    def get_game_by_package(self, package_name: str, app_store: AppStore) -> Optional[Game]:
        """根据包名获取游戏"""
        return self.session.query(Game).filter_by(
            package_name=package_name,
            app_store=app_store
        ).first()

    def get_or_create_game(self, name: str, package_name: str, app_store: AppStore) -> Game:
        """获取或创建游戏"""
        game = self.get_game_by_package(package_name, app_store)
        if not game:
            game = Game(name=name, package_name=package_name, app_store=app_store)
            game = self.save_game(game)
        return game

    def save_comment(self, comment: Comment) -> Comment:
        """保存评论"""
        self.session.add(comment)
        self.session.commit()
        self.session.refresh(comment)
        return comment

    def save_comments_batch(self, comments: List[Comment]) -> List[Comment]:
        """批量保存评论"""
        self.session.add_all(comments)
        self.session.commit()
        return comments

    def get_comments_by_game(self, game_id: int, limit: Optional[int] = None) -> List[Comment]:
        """获取游戏的所有评论"""
        query = self.session.query(Comment).filter_by(game_id=game_id)
        if limit:
            query = query.limit(limit)
        return query.all()

    def count_comments_by_game(self, game_id: int) -> int:
        """统计游戏评论数量"""
        return self.session.query(Comment).filter_by(game_id=game_id).count()

    def get_recent_comments(self, game_id: int, months: int = 6) -> List[Comment]:
        """获取最近N个月的评论"""
        comments = self.get_comments_by_game(game_id)
        return [c for c in comments if c.is_within_months(months)]
