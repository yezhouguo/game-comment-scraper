from typing import List
from src.adapters.base import BaseAppStoreAdapter, CommentData
from src.device.connector import DeviceConnector
from src.models.comment import AppStore


class OppoAppStoreAdapter(BaseAppStoreAdapter):
    """OPPO应用商店适配器

    TODO: 实现具体的爬取逻辑
    """

    APP_PACKAGE = "com.oppo.market"

    def __init__(self, device: DeviceConnector):
        super().__init__(device)
        self.app_store = AppStore.OPPO

    def open_app_store(self) -> None:
        """打开OPPO应用商店"""
        # TODO: 实现打开应用市场的逻辑
        raise NotImplementedError("Oppo adapter not implemented yet")

    def search_game(self, game_name: str) -> None:
        """搜索游戏"""
        # TODO: 实现搜索游戏的逻辑
        raise NotImplementedError("Oppo adapter not implemented yet")

    def open_game_details(self) -> None:
        """打开游戏详情页"""
        # TODO: 实现打开游戏详情页的逻辑
        raise NotImplementedError("Oppo adapter not implemented yet")

    def open_comments_section(self) -> None:
        """打开评论区"""
        # TODO: 实现打开评论区的逻辑
        raise NotImplementedError("Oppo adapter not implemented yet")

    def extract_comments(self, max_count: int = 1000) -> List[CommentData]:
        """提取评论数据"""
        # TODO: 实现提取评论的逻辑
        raise NotImplementedError("Oppo adapter not implemented yet")

    def scroll_to_load_more(self) -> bool:
        """滚动加载更多评论"""
        # TODO: 实现滚动加载更多的逻辑
        raise NotImplementedError("Oppo adapter not implemented yet")
