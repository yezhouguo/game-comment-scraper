#!/usr/bin/env python3
"""华为应用市场适配器 - 单元测试

测试内容:
1. 时间解析功能
2. 采集配置
3. 基础功能（不依赖设备）
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.adapters.huawei import (
    HuaweiAppStoreAdapter,
    HuaweiCommentData,
    ScrapeConfig
)
from datetime import datetime


def test_estimate_time_type():
    """测试时间类型判断"""
    print("\n[1/4] 测试时间类型判断...")

    test_cases = [
        ("08:02", "今天(HH:MM)"),
        ("昨天", "昨天"),
        ("2小时前", "相对时间"),
        ("2026/3/9", "完整日期"),
        ("03-09", "日期(MM-DD)"),
        ("", "未知"),
        (None, "未知"),
    ]

    passed = 0
    for time_str, expected in test_cases:
        result = HuaweiAppStoreAdapter.estimate_time_type(time_str)
        if result == expected:
            passed += 1
        else:
            print(f"  ❌ 失败: '{time_str}' -> 期望 '{expected}', 得到 '{result}'")

    print(f"  ✅ 通过: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_parse_time_to_days_ago():
    """测试天数解析"""
    print("\n[2/4] 测试天数解析...")

    # 获取今天的日期用于计算
    today = datetime.now().date()

    test_cases = [
        ("昨天", 1),
        ("08:02", 0),  # HH:MM 假设是今天
        ("2小时前", None),  # 相对时间无法精确计算
    ]

    # 添加完整日期测试
    test_cases.append((f"{today.year}/3/9", (today - datetime(today.year, 3, 9).date()).days))
    test_cases.append((f"{today.year}-03-09", (today - datetime(today.year, 3, 9).date()).days))

    passed = 0
    for time_str, expected in test_cases:
        result = HuaweiAppStoreAdapter.parse_time_to_days_ago(time_str)
        if result == expected:
            passed += 1
        else:
            print(f"  ❌ 失败: '{time_str}' -> 期望 {expected}, 得到 {result}")

    print(f"  ✅ 通过: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_scrape_config():
    """测试采集配置"""
    print("\n[3/4] 测试采集配置...")

    # 默认配置
    config1 = ScrapeConfig()
    assert config1.max_count == 1000, "默认 max_count 应该是 1000"
    assert config1.max_days is None, "默认 max_days 应该是 None"
    assert config1.max_scrolls == 500, "默认 max_scrolls 应该是 500"

    # 自定义配置
    config2 = ScrapeConfig(
        max_count=100,
        max_days=2,
        max_scrolls=50,
        progress_interval=10
    )
    assert config2.max_count == 100, "自定义 max_count 应该是 100"
    assert config2.max_days == 2, "自定义 max_days 应该是 2"
    assert config2.max_scrolls == 50, "自定义 max_scrolls 应该是 50"
    assert config2.progress_interval == 10, "自定义 progress_interval 应该是 10"

    print("  ✅ 通过: 4/4")
    return True


def test_huawei_comment_data():
    """测试华为评论数据类"""
    print("\n[4/4] 测试华为评论数据类...")

    comment = HuaweiCommentData(
        content="测试评论",
        user_id="test_user",
        time_str="08:02",
        time_type="今天(HH:MM)",
        days_ago=0
    )

    assert comment.content == "测试评论", "content 应该正确"
    assert comment.user_id == "test_user", "user_id 应该正确"
    assert comment.time_str == "08:02", "time_str 应该正确"
    assert comment.time_type == "今天(HH:MM)", "time_type 应该正确"
    assert comment.days_ago == 0, "days_ago 应该正确"

    # 测试继承自 CommentData
    assert hasattr(comment, 'rating'), "应该继承 rating 属性"
    assert hasattr(comment, 'comment_date'), "应该继承 comment_date 属性"

    print("  ✅ 通过: 6/6")
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("华为应用市场适配器 - 单元测试")
    print("=" * 60)

    results = []

    results.append(("时间类型判断", test_estimate_time_type()))
    results.append(("天数解析", test_parse_time_to_days_ago()))
    results.append(("采集配置", test_scrape_config()))
    results.append(("评论数据类", test_huawei_comment_data()))

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {status}: {name}")

    total_passed = sum(1 for _, passed in results if passed)
    print(f"\n总计: {total_passed}/{len(results)} 通过")

    if total_passed == len(results):
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {len(results) - total_passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
