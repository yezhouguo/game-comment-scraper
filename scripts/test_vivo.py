"""VIVO应用商店适配器测试脚本

用法:
    python scripts/test_vivo.py              # 测试模式 (10条评论)
    python scripts/test_vivo.py 50           # 采集50条评论
    python scripts/test_vivo.py 100 --days 1 # 采集1天内最多100条评论
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
from src.device.connector import DeviceConnector
from src.adapters.vivo import VivoAppStoreAdapter, VivoScrapeConfig


def main():
    # 解析参数
    max_count = 10  # 默认测试模式
    max_days = None

    if len(sys.argv) > 1:
        try:
            max_count = int(sys.argv[1])
        except ValueError:
            print("Usage: python test_vivo.py [max_count] [--days N]")
            return

    if "--days" in sys.argv:
        idx = sys.argv.index("--days")
        if idx + 1 < len(sys.argv):
            try:
                max_days = int(sys.argv[idx + 1])
            except ValueError:
                print("Invalid days value")
                return

    # 连接设备
    print("连接设备...")
    device_connector = DeviceConnector()
    device_connector.connect_usb()
    adapter = VivoAppStoreAdapter(device_connector)

    # 配置采集参数
    config = VivoScrapeConfig(
        max_count=max_count,
        max_days=max_days,
        max_scrolls=500,
        progress_interval=5
    )

    # 测试游戏信息
    game_name = "王者荣耀"
    package_name = "com.tencent.tmgp.sgame"

    print(f"\n开始测试 VIVO 适配器")
    print(f"游戏: {game_name}")
    print(f"包名: {package_name}")
    print(f"目标数量: {max_count}")
    if max_days:
        print(f"时间限制: {max_days}天内")
    print()

    # 采集评论
    comments = adapter.scrape_game_comments(game_name, package_name, config)

    # 统计结果
    print(f"\n=== 采集结果 ===")
    print(f"总评论数: {len(comments)}")

    # 按天数统计
    days_count = {}
    time_type_count = {}
    for comment in comments:
        if comment.days_ago is not None:
            days_count[comment.days_ago] = days_count.get(comment.days_ago, 0) + 1
        if comment.time_type:
            time_type_count[comment.time_type] = time_type_count.get(comment.time_type, 0) + 1

    print(f"\n按天数分布:")
    for days in sorted(days_count.keys()):
        label = "今天" if days == 0 else f"{days}天前"
        print(f"  {label}: {days_count[days]}条")

    print(f"\n按时间类型分布:")
    for time_type, count in time_type_count.items():
        print(f"  {time_type}: {count}条")

    # 显示前5条评论预览
    print(f"\n前5条评论预览:")
    for i, comment in enumerate(comments[:5]):
        days_info = f" ({comment.days_ago}天前)" if comment.days_ago is not None else ""
        like_info = f" | {comment.like_count}赞" if comment.like_count else ""
        print(f"  [{i+1}] {comment.user_id}{days_info}{like_info}")
        print(f"      {comment.content[:50]}...")

    # 导出为 Excel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/vivo_{game_name}_{timestamp}.xlsx"

    # 准备数据
    data = []
    for comment in comments:
        days_label = ""
        if comment.days_ago is not None:
            if comment.days_ago == 0:
                days_label = "今天"
            else:
                days_label = f"{comment.days_ago}天前"

        data.append({
            "用户ID": comment.user_id,
            "评论内容": comment.content,
            "原始时间": comment.time_str,
            "时间类型": comment.time_type,
            "天数": days_label,
            "点赞数": comment.like_count or "",
            "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    df = pd.DataFrame(data)

    # 添加统计信息
    summary_rows = []
    summary_rows.append(["=== 统计信息 ===", "", "", "", "", "", ""])
    summary_rows.append(["总评论数", len(comments), "", "", "", "", ""])

    for days in sorted(days_count.keys()):
        label = "今天" if days == 0 else f"{days}天前"
        summary_rows.append([label, days_count[days], "", "", "", "", ""])

    summary_df = pd.DataFrame(summary_rows, columns=df.columns)

    # 合并数据并导出
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='统计', index=False)
        df.to_excel(writer, sheet_name='评论数据', index=False)

    print(f"\n数据已导出至: {filename}")
    print(f"  - 统计工作表: 按天数分布")
    print(f"  - 评论数据工作表: 完整评论列表")

    print(f"\n测试完成!")


if __name__ == "__main__":
    # 确保目录存在
    os.makedirs("data", exist_ok=True)

    main()
