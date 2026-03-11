#!/usr/bin/env python3
"""测试华为应用市场适配器（优化版本）"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.device.connector import DeviceConnector
from src.adapters.huawei import HuaweiAppStoreAdapter


def test_market_protocol():
    """测试 market 协议跳转"""
    import subprocess

    print("=== Testing Market Protocol ===\n")

    # 测试直接跳转到王者荣耀详情页
    package_name = "com.tencent.tmgp.sgame"
    url = f"market://details?id={package_name}"

    print(f"Opening {url}...")
    cmd = [
        "adb", "shell", "am", "start",
        "-a", "android.intent.action.VIEW",
        "-d", url,
        "com.huawei.appmarket"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Command result: {result.returncode}")
    if result.stdout:
        print(f"stdout: {result.stdout}")
    if result.stderr:
        print(f"stderr: {result.stderr}")

    print("\nWaiting 3 seconds for page to load...")
    import time
    time.sleep(3)

    # 检查当前页面
    d = None
    try:
        import uiautomator2 as u2
        d = u2.connect_usb()
        xml = d.dump_hierarchy()

        print("\n=== Checking if we're on detail page ===")
        if '王者荣耀' in xml:
            print("✓ Found 王者荣耀 on page!")
        if '评论' in xml:
            print("✓ Found 评论 tab!")

    except Exception as e:
        print(f"Error: {e}")


def test_huawei_adapter():
    """测试华为应用市场适配器"""
    print("\n=== Testing Huawei Adapter (Optimized) ===\n")

    # 连接设备
    print("1. Connecting to device...")
    device = DeviceConnector()
    device.connect_usb()
    print("   Connected!\n")

    # 创建适配器
    print("2. Creating Huawei adapter...")
    adapter = HuaweiAppStoreAdapter(device)
    print("   Adapter created!\n")

    # 测试采集评论（先采集少量测试）
    print("3. Starting to scrape comments...")
    print("   Game: 王者荣耀")
    print("   Package: com.tencent.tmgp.sgame")
    print("   Max comments: 5\n")

    comments = adapter.scrape_game_comments(
        game_name="王者荣耀",
        package_name="com.tencent.tmgp.sgame",
        max_count=5
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
    # 先测试 market 协议
    test_market_protocol()

    # 再测试完整适配器
    test_huawei_adapter()
