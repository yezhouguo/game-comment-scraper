"""OPPO应用商店评论采集测试脚本"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.oppo import OppoAppStoreAdapter, OppoScrapeConfig
from src.device.connector import DeviceConnector
import pandas as pd
from datetime import datetime


def main():
    # 连接设备
    print("连接设备...")
    device = DeviceConnector()
    device.connect_usb()
    d = device.device

    # 创建适配器
    adapter = OppoAppStoreAdapter(device)

    # 测试游戏
    game_name = "王者荣耀"
    package_name = "com.tencent.tmgp.sgame"

    # 采集配置 - 测试1000条
    config = OppoScrapeConfig(
        max_count=1000,
        max_scrolls=500,
        progress_interval=10
    )

    print(f"\n{'='*50}")
    print(f"开始测试: {game_name}")
    print(f"{'='*50}\n")

    # 采集评论
    comments = adapter.scrape_game_comments(game_name, package_name, config)

    print(f"\n{'='*50}")
    print(f"采集完成: {len(comments)} 条评论")
    print(f"{'='*50}\n")

    # 显示前几条评论
    for i, comment in enumerate(comments[:5], 1):
        print(f"[{i}] 用户: {comment.user_id}")
        print(f"    时间: {comment.time_str} ({comment.days_ago}天前)" if comment.days_ago is not None else f"    时间: {comment.time_str}")
        print(f"    内容: {comment.content[:60]}...")
        print()

    # 保存到Excel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/oppo_{game_name}_{timestamp}.xlsx"

    # 转换数据
    data = []
    for c in comments:
        data.append({
            "用户ID": c.user_id,
            "评论内容": c.content,
            "原始时间": c.time_str,
            "几天前": c.days_ago if c.days_ago is not None else "",
        })

    df = pd.DataFrame(data)
    os.makedirs("data", exist_ok=True)
    df.to_excel(output_file, index=False, engine='openpyxl')

    print(f"数据已保存到: {output_file}")

    # 清理
    print("\n清理后台...")
    import subprocess
    subprocess.run(["adb", "shell", "am", "force-stop", "com.heytap.market"], capture_output=True)


if __name__ == "__main__":
    main()
