from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from src.device.connector import DeviceConnector
from src.models.comment import AppStore


@dataclass
class CommentData:
    """评论数据结构"""
    content: str
    user_id: str
    rating: Optional[int] = None
    comment_date: Optional[str] = None


class BaseAppStoreAdapter(ABC):
    """应用市场适配器基类"""

    def __init__(self, device: DeviceConnector):
        self.device = device
        self.app_store: AppStore = None

    @abstractmethod
    def open_app_store(self) -> None:
        """打开应用市场"""
        pass

    @abstractmethod
    def search_game(self, game_name: str) -> None:
        """搜索游戏"""
        pass

    @abstractmethod
    def open_game_details(self) -> None:
        """打开游戏详情页"""
        pass

    @abstractmethod
    def open_comments_section(self) -> None:
        """打开评论区"""
        pass

    @abstractmethod
    def extract_comments(self, max_count: int = 1000) -> List[CommentData]:
        """提取评论数据"""
        pass

    @abstractmethod
    def scroll_to_load_more(self) -> bool:
        """滚动加载更多评论，返回是否还有更多"""
        pass

    def scrape_game_comments(
        self,
        game_name: str,
        package_name: str,
        max_count: int = 1000
    ) -> List[CommentData]:
        """
        完整的评论采集流程
        """
        self.open_app_store()
        self.search_game(game_name)
        self.open_game_details()
        self.open_comments_section()

        all_comments = []
        while len(all_comments) < max_count:
            comments = self.extract_comments(max_count - len(all_comments))
            # TODO: 实现去重逻辑
            all_comments.extend(comments)

            if len(all_comments) >= max_count:
                break

            if not self.scroll_to_load_more():
                break

        return all_comments[:max_count]
