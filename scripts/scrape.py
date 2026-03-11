#!/usr/bin/env python3
"""游戏评论采集脚本"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scraper.collector import CommentCollector
from src.models.comment import AppStore
from config.settings import (
    DEVICE_ADDRESS, DB_PATH, MAX_COMMENTS_PER_GAME,
    DEFAULT_APP_STORES, GAMES_TO_SCRAPE
)


def main():
    print("=== Game Comment Scraper ===\n")

    # 创建采集器
    print(f"Connecting to device: {DEVICE_ADDRESS}")
    collector = CommentCollector(DEVICE_ADDRESS, DB_PATH)
    print("Connected!\n")

    # 显示配置
    print(f"App stores: {[s.value for s in DEFAULT_APP_STORES]}")
    print(f"Games to scrape ({len(GAMES_TO_SCRAPE)}):")
    for i, game in enumerate(GAMES_TO_SCRAPE, 1):
        print(f"  {i}. {game['name']} ({game['package']})")
    print(f"\nMax comments per game: {MAX_COMMENTS_PER_GAME}\n")

    # 开始采集
    print("Starting collection...\n")

    results = collector.scrape_multiple_games(
        games=GAMES_TO_SCRAPE,
        app_stores=DEFAULT_APP_STORES,
        max_comments=MAX_COMMENTS_PER_GAME
    )

    # 输出结果
    print("\n=== Collection Summary ===")
    for game_name, store_results in results.items():
        print(f"\n{game_name}:")
        total = 0
        for store, count in store_results.items():
            print(f"  {store.value}: {count} comments")
            total += count
        print(f"  Total: {total} comments")

    collector.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
