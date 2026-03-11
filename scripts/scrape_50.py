#!/usr/bin/env python3
"""华为应用市场 - 爬取50条评论测试脚本"""

import sys
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.device.connector import DeviceConnector
from src.adapters.huawei import HuaweiAppStoreAdapter


def scrape_50_comments():
    """爬取王者荣耀前50条评论"""

    # 测试游戏信息
    GAME_NAME = "王者荣耀"
    PACKAGE_NAME = "com.tencent.tmgp.sgame"
    TARGET_COUNT = 50

    print("=" * 60)
    print(f"华为应用市场 - {GAME_NAME} 评论采集")
    print(f"目标数量: {TARGET_COUNT} 条")
    print("=" * 60)

    # 连接设备
    print("\n[1/4] 连接设备...")
    device = DeviceConnector()
    device.connect_usb()
    print(f"    设备连接成功: {device.device.device_info}")

    # 创建适配器
    print("\n[2/4] 初始化华为适配器...")
    adapter = HuaweiAppStoreAdapter(device)

    # 开始采集
    print(f"\n[3/4] 开始采集评论...")
    print("-" * 60)

    start_time = time.time()

    comments = adapter.scrape_game_comments(
        game_name=GAME_NAME,
        package_name=PACKAGE_NAME,
        max_count=TARGET_COUNT
    )

    elapsed_time = time.time() - start_time

    print("-" * 60)
    print(f"\n[4/4] 采集完成!")
    print(f"    实际采集: {len(comments)} 条")
    print(f"    耗时: {elapsed_time:.1f} 秒")
    print(f"    平均速度: {elapsed_time/len(comments):.2f} 秒/条" if comments else "    平均速度: N/A")

    # 展示所有评论
    print("\n" + "=" * 60)
    print("评论详情")
    print("=" * 60)

    for i, comment in enumerate(comments, 1):
        # 匿名化处理用户ID（保留首尾各2个字符）
        user_id = comment.user_id or "匿名"
        if len(user_id) > 4:
            masked_id = f"{user_id[:2]}***{user_id[-2:]}"
        else:
            masked_id = f"{'*' * (len(user_id) - 1)}{user_id[-1:]}"

        content = comment.content or ""
        # 截断过长的评论
        display_content = content[:80] + "..." if len(content) > 80 else content

        print(f"\n[{i}] {masked_id}")
        print(f"    {display_content}")

    print("\n" + "=" * 60)
    print(f"采集完成，共 {len(comments)} 条评论")
    print("=" * 60)

    return comments


if __name__ == "__main__":
    try:
        comments = scrape_50_comments()
    except KeyboardInterrupt:
        print("\n\n用户中断采集")
    except Exception as e:
        print(f"\n\n采集出错: {e}")
        import traceback
        traceback.print_exc()
