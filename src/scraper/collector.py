from typing import List, Dict
from datetime import datetime
from src.device.connector import DeviceConnector
from src.adapters.base import BaseAppStoreAdapter, CommentData
from src.adapters.huawei import HuaweiAppStoreAdapter
from src.adapters.xiaomi import XiaomiAppStoreAdapter
from src.adapters.oppo import OppoAppStoreAdapter
from src.adapters.vivo import VivoAppStoreAdapter
from src.storage.repository import CommentRepository
from src.models.comment import AppStore, Comment


class CommentCollector:
    """评论采集协调器"""

    ADAPTER_MAP = {
        AppStore.HUAWEI: HuaweiAppStoreAdapter,
        AppStore.XIAOMI: XiaomiAppStoreAdapter,
        AppStore.OPPO: OppoAppStoreAdapter,
        AppStore.VIVO: VivoAppStoreAdapter,
    }

    def __init__(self, device_address: str, db_path: str = "data/comments.db"):
        self.device = DeviceConnector()
        self.device.connect(device_address)

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from src.models.comment import Base

        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.repository = CommentRepository(self.session)

    def scrape_game(
        self,
        game_name: str,
        package_name: str,
        app_stores: List[AppStore],
        max_comments: int = 1000
    ) -> Dict[AppStore, int]:
        """
        采集指定游戏的评论

        返回: {应用市场: 采集数量}
        """
        results = {}

        for store in app_stores:
            try:
                adapter_class = self.ADAPTER_MAP.get(store)
                if not adapter_class:
                    print(f"Unsupported app store: {store}")
                    continue

                adapter = adapter_class(self.device)
                comments_data = adapter.scrape_game_comments(
                    game_name, package_name, max_comments
                )

                # 保存到数据库
                game = self.repository.get_or_create_game(
                    game_name, package_name, store
                )

                saved_count = 0
                for comment_data in comments_data:
                    comment = Comment(
                        game_id=game.id,
                        content=comment_data.content,
                        user_id=comment_data.user_id,
                        app_store=store,
                        rating=comment_data.rating,
                        scraped_at=datetime.now()
                    )
                    self.repository.save_comment(comment)
                    saved_count += 1

                results[store] = saved_count
                print(f"{store.value}: Collected {saved_count} comments")

            except NotImplementedError as e:
                print(f"Adapter for {store.value} not implemented yet: {e}")
                results[store] = 0
            except Exception as e:
                print(f"Error scraping from {store.value}: {e}")
                results[store] = 0

        return results

    def scrape_multiple_games(
        self,
        games: List[Dict[str, str]],
        app_stores: List[AppStore],
        max_comments: int = 1000
    ) -> Dict[str, Dict[AppStore, int]]:
        """
        采集多个游戏的评论

        games: [{"name": "游戏名", "package": "包名"}, ...]
        """
        all_results = {}

        for game in games:
            game_name = game["name"]
            package_name = game["package"]
            print(f"\nScraping {game_name}...")

            results = self.scrape_game(
                game_name, package_name, app_stores, max_comments
            )
            all_results[game_name] = results

        return all_results

    def close(self):
        """关闭连接"""
        self.session.close()
        self.device.disconnect()
