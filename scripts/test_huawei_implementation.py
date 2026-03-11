#!/usr/bin/env python3
"""测试华为应用市场适配器"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.device.connector import DeviceConnector
from src.adapters.huawei import HuaweiAppStoreAdapter


def test_huawei_adapter():
    """测试华为应用市场适配器"""
    print("=== Testing Huawei AppGallery Adapter ===\n")

    # 连接设备
    print("1. Connecting to device...")
    device = DeviceConnector()
    device.connect_usb()
    print("   Connected!\n")

    # 创建适配器
    print("2. Creating Huawei adapter...")
    adapter = HuaweiAppStoreAdapter(device)
    print("   Adapter created!\n")

    # 测试采集评论
    print("3. Starting to scrape comments...")
    print("   Game: 王者荣耀 (com.tencent.tmgp.sgame)")
    print("   Max comments: 10\n")

    comments = adapter.scrape_game_comments(
        game_name="王者荣耀",
        package_name="com.tencent.tmgp.sgame",
        max_count=10
    )

    # 显示结果
    print(f"\n4. Results: {len(comments)} comments collected\n")
    for i, comment in enumerate(comments, 1):
        print(f"Comment {i}:")
        print(f"  User: {comment.user_id}")
        print(f"  Content: {comment.content}")
        print(f"  Rating: {comment.rating}")
        print(f"  Time: {comment.comment_date}")
        print()

    device.disconnect()
    print("Test completed!")


if __name__ == "__main__":
    test_huawei_adapter()
