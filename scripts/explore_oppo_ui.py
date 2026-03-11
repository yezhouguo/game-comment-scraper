#!/usr/bin/env python3
"""OPPO应用商店UI元素探索脚本

通过market协议跳转到王者荣耀详情页，并dump界面层级结构
"""

import uiautomator2 as u2
import time
import xml.etree.ElementTree as ET
from pathlib import Path

# 目标游戏
GAME_PACKAGE = "com.tencent.tmgp.sgame"  # 王者荣耀
OPPO_STORE_PACKAGE = "com.heytap.market"

# 输出目录
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "oppo_ui_exploration"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def dump_oppo_store():
    """探索OPPO应用商店的UI元素"""

    # 连接设备
    print("连接设备...")
    d = u2.connect_usb()
    print(f"已连接: {d.info}")

    # Step 1: 使用market协议跳转到王者荣耀详情页
    print("\n=== Step 1: 使用market协议跳转 ===")
    market_url = f"market://details?id={GAME_PACKAGE}"
    cmd = f"am start -a android.intent.action.VIEW -d '{market_url}' {OPPO_STORE_PACKAGE}"
    print(f"执行: adb shell {cmd}")
    d.shell(cmd)

    time.sleep(3)  # 等待页面加载

    # 截图保存
    screenshot_path = OUTPUT_DIR / "01_app_details.png"
    d.screenshot(str(screenshot_path))
    print(f"截图保存: {screenshot_path}")

    # Dump UI层级
    xml_path = OUTPUT_DIR / "01_app_details.xml"
    xml_content = d.dump_hierarchy()
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"XML保存: {xml_path}")

    # Step 2: 查找并点击评论tab
    print("\n=== Step 2: 查找评论tab ===")

    # 尝试多种定位方式
    comment_found = False

    # 方法1: 通过文本查找"评论"
    try:
        print("尝试通过text='评论'查找...")
        comment_elements = d(text="评论")
        if comment_elements.exists:
            print(f"找到 {len(comment_elements)} 个'评论'元素")
            for i, elem in enumerate(comment_elements):
                info = elem.info
                print(f"  元素{i}: {info}")
            # 点击第一个评论元素
            comment_elements[0].click()
            comment_found = True
    except Exception as e:
        print(f"通过text查找失败: {e}")

    # 方法2: 通过textContains查找
    if not comment_found:
        try:
            print("尝试通过textContains='评论'查找...")
            comment_elements = d(textContains="评论")
            if comment_elements.exists:
                print(f"找到 {len(comment_elements)} 个包含'评论'的元素")
                for i, elem in enumerate(comment_elements):
                    info = elem.info
                    print(f"  元素{i}: {info}")
                comment_elements[0].click()
                comment_found = True
        except Exception as e:
            print(f"通过textContains查找失败: {e}")

    # 方法3: 通过resourceId查找（需要先了解可能的ID模式）
    if not comment_found:
        print("尝试查找常见的tab resource-id模式...")
        # 尝试常见的tab ID模式
        possible_ids = [
            "com.heytap.market:id/tab_comment",
            "com.heytap.market:id/comment_tab",
            "com.heytap.market:id/comment",
            "com.heytap.market:id/comments",
        ]

        for rid in possible_ids:
            try:
                elem = d(resourceId=rid)
                if elem.exists:
                    print(f"找到resourceId: {rid}")
                    elem.click()
                    comment_found = True
                    break
            except Exception:
                pass

    time.sleep(2)

    # 截图评论页面
    screenshot_path = OUTPUT_DIR / "02_comments_section.png"
    d.screenshot(str(screenshot_path))
    print(f"截图保存: {screenshot_path}")

    # Dump评论页面UI
    xml_path = OUTPUT_DIR / "02_comments_section.xml"
    xml_content = d.dump_hierarchy()
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"XML保存: {xml_path}")

    # Step 3: 分析评论列表元素
    print("\n=== Step 3: 分析评论列表元素 ===")
    analyze_comment_elements(xml_content)

    # Step 4: 测试滚动
    print("\n=== Step 4: 测试滚动 ===")
    for i in range(3):
        print(f"滚动 {i+1}/3")
        d.swipe(0.5, 0.75, 0.5, 0.25)
        time.sleep(1.5)

        screenshot_path = OUTPUT_DIR / f"03_scroll_{i+1}.png"
        d.screenshot(str(screenshot_path))
        print(f"  截图: {screenshot_path}")

    # 最终dump
    xml_path = OUTPUT_DIR / "03_after_scroll.xml"
    xml_content = d.dump_hierarchy()
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"滚动后XML保存: {xml_path}")

    print("\n=== 探索完成 ===")
    print(f"所有文件保存在: {OUTPUT_DIR}")


def analyze_comment_elements(xml_content: str):
    """分析评论列表的关键元素"""

    root = ET.fromstring(xml_content)

    # 查找所有包含"评论"相关文字的节点
    print("\n查找评论相关元素...")

    # 收集可能评论相关的resource-id
    comment_ids = set()

    for node in root.iter():
        # 检查resource-id
        resource_id = node.attrib.get("resource-id", "")
        if resource_id and any(keyword in resource_id.lower() for keyword in ["comment", "user", "content", "time", "review"]):
            comment_ids.add(resource_id)

        # 检查text属性
        text = node.attrib.get("text", "")
        if text and len(text) > 0 and len(text) < 100:
            # 打印一些示例文本
            if "评论" in text or len(text) > 10:
                clickable = node.attrib.get("clickable", "false")
                print(f"  text='{text[:50]}...', clickable={clickable}, resource-id={resource_id}")

    print(f"\n找到 {len(comment_ids)} 个可能的评论相关resource-id:")
    for cid in sorted(comment_ids):
        print(f"  - {cid}")

    # 查找ListView/RecyclerView
    print("\n查找列表容器...")
    for node in root.iter():
        class_name = node.attrib.get("class", "")
        if "ListView" in class_name or "RecyclerView" in class_name:
            resource_id = node.attrib.get("resource-id", "")
            print(f"  容器: class={class_name}, resource-id={resource_id}")


if __name__ == "__main__":
    dump_oppo_store()
