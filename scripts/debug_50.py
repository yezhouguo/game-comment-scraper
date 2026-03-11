#!/usr/bin/env python3
"""华为应用市场 - 调试脚本，定位50条评论采集失败问题"""

import sys
import time
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.device.connector import DeviceConnector
from src.adapters.huawei import HuaweiAppStoreAdapter


def debug_navigation():
    """逐步调试导航流程"""

    GAME_NAME = "王者荣耀"
    PACKAGE_NAME = "com.tencent.tmgp.sgame"

    print("=" * 60)
    print("华为应用市场 - 导航调试")
    print("=" * 60)

    # 连接设备
    print("\n[1] 连接设备...")
    device = DeviceConnector()
    device.connect_usb()
    d = device.device
    print(f"    设备: {d.device_info}")

    # 返回首页，确保干净状态
    print("\n[2] 返回首页...")
    d.press("home")
    time.sleep(1)

    # Step 1: Market 协议跳转
    print(f"\n[3] Market 协议跳转到 {PACKAGE_NAME}...")
    url = f"market://details?id={PACKAGE_NAME}"
    cmd = ["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url, "com.huawei.appmarket"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    print(f"    ADB 命令输出: {result.stdout.strip()}")
    time.sleep(3)

    # 检查当前页面
    print("\n[4] 检查当前页面...")
    current_activity = d.app_current()['activity']
    print(f"    当前 Activity: {current_activity}")

    # 检查关键元素
    print("\n[5] 检查页面元素...")

    # 检查 "介绍" 元素
    intro_elem = d(resourceId="com.huawei.appmarket:id/other_appinfos")
    print(f"    '介绍' 元素存在: {intro_elem.exists}")
    if intro_elem.exists:
        info = intro_elem.info
        print(f"    '介绍' 元素 info: {info}")

    # 检查 "评论" 元素
    comment_elem = d(textContains="评论")
    print(f"    '评论' 元素存在: {comment_elem.exists}")
    if comment_elem.exists:
        print(f"    '评论' 元素数量: {len(comment_elem)}")
        for i, elem in enumerate(comment_elem):
            print(f"      [{i}] {elem.info.get('text', '')} - bounds: {elem.info.get('bounds', {})}")

    # Step 2: 点击"介绍"
    print("\n[6] 点击 '介绍'...")
    if intro_elem.exists:
        info = intro_elem.info
        bounds = info.get('bounds', {})
        if bounds:
            left = bounds.get('left', 318)
            right = bounds.get('right', 483)
            intro_x = left + (right - left) * 0.3
            intro_y = (bounds.get('top', 315) + bounds.get('bottom', 343)) / 2
            print(f"    点击坐标: ({intro_x:.0f}, {intro_y:.0f})")
            d.click(int(intro_x), int(intro_y))
        else:
            d.click(350, 329)
    else:
        print("    '介绍' 元素不存在，尝试点击默认位置")
        d.click(350, 329)

    time.sleep(2.5)

    # 再次检查元素
    print("\n[7] 点击后检查 '评论' 元素...")
    comment_elem = d(textContains="评论")
    print(f"    '评论' 元素存在: {comment_elem.exists}")
    if comment_elem.exists:
        print(f"    '评论' 元素数量: {len(comment_elem)}")
        for i, elem in enumerate(comment_elem):
            info = elem.info
            text = info.get('text', '')
            bounds = info.get('bounds', {})
            print(f"      [{i}] text='{text}' bounds={bounds}")

            # 检查是否可点击
            is_clickable = info.get('clickable', False)
            print(f"          clickable={is_clickable}")

    # Step 3: 点击"评论"
    print("\n[8] 点击 '评论'...")
    comment_elem = d(textContains="评论")
    if comment_elem.exists:
        # 尝试点击第一个"评论"元素
        comment_elem[0].click()
        print("    点击成功")
    else:
        print("    '评论' 元素不存在!")

    time.sleep(2)

    # Step 4: 检查评论区域
    print("\n[9] 检查评论区域...")

    # 检查用户ID元素
    users = d(resourceId="com.huawei.appmarket:id/detail_comment_user_textview")
    print(f"    用户ID 元素存在: {users.exists}")
    if users.exists:
        print(f"    用户ID 数量: {len(users)}")
        for i in range(min(3, len(users))):
            print(f"      [{i}] {users[i].info.get('text', '')}")

    # 检查评论内容元素
    contents = d(resourceId="com.huawei.appmarket:id/detail_comment_content_textview")
    print(f"    评论内容 元素存在: {contents.exists}")
    if contents.exists:
        print(f"    评论内容 数量: {len(contents)}")
        for i in range(min(3, len(contents))):
            text = contents[i].info.get('text', '')
            preview = text[:50] + "..." if len(text) > 50 else text
            print(f"      [{i}] {preview}")

    # 保存当前页面 XML 供分析
    print("\n[10] 保存页面 XML...")
    xml_path = "/tmp/huawei_debug_page.xml"
    d.dump_hierarchy(xml_path)
    print(f"    XML 已保存到: {xml_path}")

    # 返回首页
    print("\n[11] 返回首页...")
    d.press("home")
    time.sleep(1)

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        debug_navigation()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n\n调试出错: {e}")
        import traceback
        traceback.print_exc()
