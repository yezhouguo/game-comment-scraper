#!/usr/bin/env python3 -u
"""华为应用市场适配器 - 集成测试（需要连接设备）

测试内容:
1. 设备连接
2. 完整采集流程
3. 时间限制筛选
4. 条数限制
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.device.connector import DeviceConnector
from src.adapters.huawei import (
    HuaweiAppStoreAdapter,
    HuaweiCommentData,
    ScrapeConfig
)


def test_device_connection():
    """测试设备连接"""
    print("\n[1/3] 测试设备连接...")
    try:
        device = DeviceConnector()
        device.connect_usb()
        print(f"  ✅ 设备连接成功: {device.device.device_info['model']}")
        return device
    except Exception as e:
        print(f"  ❌ 设备连接失败: {e}")
        return None


def test_basic_scrape(device, count=10):
    """测试基础采集功能"""
    print(f"\n[2/3] 测试基础采集 ({count}条)...")

    adapter = HuaweiAppStoreAdapter(device)
    config = ScrapeConfig(max_count=count, max_scrolls=20)

    try:
        comments = adapter.scrape_game_comments(
            game_name="王者荣耀",
            package_name="com.tencent.tmgp.sgame",
            config=config
        )

        if len(comments) > 0:
            print(f"  ✅ 采集成功: {len(comments)} 条评论")

            # 显示前3条
            for i, c in enumerate(comments[:3], 1):
                days_info = f"{c.days_ago}天前" if c.days_ago is not None else "未知"
                print(f"    [{i}] {c.time_str} ({days_info}): {c.content[:30]}...")

            return True
        else:
            print("  ❌ 未采集到评论")
            return False

    except Exception as e:
        print(f"  ❌ 采集失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_days_filter(device):
    """测试天数筛选"""
    print(f"\n[3/3] 测试天数筛选 (只采集2天内)...")

    adapter = HuaweiAppStoreAdapter(device)
    config = ScrapeConfig(max_count=50, max_days=2, max_scrolls=30)

    try:
        comments = adapter.scrape_game_comments(
            game_name="王者荣耀",
            package_name="com.tencent.tmgp.sgame",
            config=config
        )

        # 统计天数分布
        days_stats = {}
        for c in comments:
            if c.days_ago is not None:
                days_stats[c.days_ago] = days_stats.get(c.days_ago, 0) + 1

        print(f"  ✅ 采集成功: {len(comments)} 条评论")

        # 检查是否有超出2天的评论
        out_of_range = sum(1 for c in comments if c.days_ago and c.days_ago > 2)

        print(f"  天数分布:")
        for days in sorted(days_stats.keys()):
            label = "今天" if days == 0 else ("昨天" if days == 1 else f"{days}天前")
            print(f"    {label}: {days_stats[days]} 条")

        if out_of_range > 0:
            print(f"  ⚠️  发现 {out_of_range} 条超出2天的评论（可能需要检查筛选逻辑）")
            return False
        else:
            print(f"  ✅ 筛选正确: 所有评论都在2天内")
            return True

    except Exception as e:
        print(f"  ❌ 采集失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_integration_tests():
    """运行集成测试"""
    print("=" * 60)
    print("华为应用市场适配器 - 集成测试")
    print("=" * 60)

    # 测试设备连接
    device = test_device_connection()
    if not device:
        print("\n❌ 设备连接失败，跳过后续测试")
        return 1

    results = []

    # 测试基础采集
    results.append(("基础采集", test_basic_scrape(device, count=10)))

    # 测试天数筛选
    results.append(("天数筛选", test_days_filter(device)))

    # 返回首页
    print("\n返回首页...")
    device.device.press("home")

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {status}: {name}")

    total_passed = sum(1 for _, passed in results if passed)
    print(f"\n总计: {total_passed}/{len(results)} 通过")

    if total_passed == len(results):
        print("\n🎉 所有集成测试通过！")
        return 0
    else:
        print(f"\n⚠️  {len(results) - total_passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit_code = run_integration_tests()
    sys.exit(exit_code)
