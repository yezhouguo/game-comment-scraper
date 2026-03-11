#!/usr/bin/env python3
"""OPPO应用商店UI元素探索脚本 V2

手动导航到应用详情页并dump界面层级结构
"""

import uiautomator2 as u2
import time
import xml.etree.ElementTree as ET
from pathlib import Path

# 目标游戏
GAME_NAME = "王者荣耀"
GAME_PACKAGE = "com.tencent.tmgp.sgame"
OPPO_STORE_PACKAGE = "com.heytap.market"

# 输出目录
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "oppo_ui_exploration"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def wait_and_click(d, selector, timeout=5, description=""):
    """等待元素出现并点击"""
    print(f"  等待: {description}")
    element = d(selector)
    if element.wait(timeout=timeout):
        print(f"  找到元素，点击")
        element.click()
        time.sleep(1.5)
        return True
    else:
        print(f"  未找到元素: {selector}")
        return False


def explore_oppo_store():
    """探索OPPO应用商店的UI元素"""

    # 连接设备
    print("连接设备...")
    d = u2.connect_usb()
    print(f"已连接: {d.info}")

    # 首先处理可能存在的用户协议对话框
    print("\n=== 处理用户协议对话框 ===")
    try:
        agree_btn = d(resourceId="com.heytap.market:id/enter", text="同意并使用")
        if agree_btn.exists:
            print("发现用户协议对话框，点击同意")
            agree_btn.click()
            time.sleep(2)
    except Exception as e:
        print(f"处理用户协议时出错: {e}")

    # 启动OPPO应用商店
    print("\n=== 启动OPPO应用商店 ===")
    d.app_start(OPPO_STORE_PACKAGE)
    time.sleep(3)

    screenshot_path = OUTPUT_DIR / "00_home.png"
    d.screenshot(str(screenshot_path))
    print(f"首页截图: {screenshot_path}")

    # Step 1: 搜索游戏
    print("\n=== Step 1: 搜索游戏 ===")

    # 查找搜索框 - 可能的resource-id或description
    search_found = False

    # 尝试1: 通过content-desc查找搜索框
    try:
        search_elements = d(descriptionContains="搜索")
        if search_elements.exists:
            print(f"找到搜索框 (通过description)")
            search_elements.click()
            search_found = True
    except Exception as e:
        print(f"通过description查找搜索框失败: {e}")

    # 尝试2: 通过resource-id
    if not search_found:
        possible_ids = [
            "com.heytap.market:id/search_layout",
            "com.heytap.market:id/search",
            "com.heytap.market:id/search_button",
            "com.heytap.market:id/et_search",
        ]
        for rid in possible_ids:
            try:
                elem = d(resourceId=rid)
                if elem.exists:
                    print(f"找到搜索框: {rid}")
                    elem.click()
                    search_found = True
                    break
            except Exception:
                pass

    if not search_found:
        print("无法找到搜索框，尝试其他方式...")

    time.sleep(1.5)

    screenshot_path = OUTPUT_DIR / "01_search_page.png"
    d.screenshot(str(screenshot_path))
    print(f"搜索页截图: {screenshot_path}")

    # 输入游戏名称
    print(f"输入游戏名称: {GAME_NAME}")
    search_input_found = False

    # 查找输入框
    possible_input_ids = [
        "com.heytap.market:id/et_search",
        "com.heytap.market:id/search_input",
        "com.heytap.market:id/edit_text",
        "android:id/search_src_text",
    ]

    for rid in possible_input_ids:
        try:
            elem = d(resourceId=rid)
            if elem.exists:
                print(f"找到输入框: {rid}")
                elem.set_text(GAME_NAME)
                search_input_found = True
                time.sleep(1)
                break
        except Exception:
            pass

    if not search_input_found:
        # 尝试通过className查找EditText
        try:
            edit_texts = d(className="android.widget.EditText")
            if edit_texts.exists:
                print("找到EditText输入框")
                edit_texts.set_text(GAME_NAME)
                search_input_found = True
                time.sleep(1)
        except Exception as e:
            print(f"输入游戏名称失败: {e}")

    # 按Enter键搜索
    if search_input_found:
        print("按Enter键搜索")
        d.press("enter")
        time.sleep(2)

    screenshot_path = OUTPUT_DIR / "02_search_results.png"
    d.screenshot(str(screenshot_path))
    print(f"搜索结果截图: {screenshot_path}")

    # Dump搜索结果XML
    xml_path = OUTPUT_DIR / "02_search_results.xml"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(d.dump_hierarchy())
    print(f"搜索结果XML: {xml_path}")

    # Step 2: 点击游戏进入详情页
    print("\n=== Step 2: 点击游戏进入详情页 ===")

    # 查找王者荣耀游戏项
    game_found = False

    # 通过文本查找
    try:
        game_text = d(text=GAME_NAME)
        if game_text.exists:
            print(f"找到游戏文本: {GAME_NAME}")
            game_text.click()
            game_found = True
    except Exception as e:
        print(f"通过text查找游戏失败: {e}")

    time.sleep(2)

    screenshot_path = OUTPUT_DIR / "03_app_details.png"
    d.screenshot(str(screenshot_path))
    print(f"应用详情截图: {screenshot_path}")

    # Dump应用详情XML
    xml_path = OUTPUT_DIR / "03_app_details.xml"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(d.dump_hierarchy())
    print(f"应用详情XML: {xml_path}")

    # Step 3: 查找并点击评论
    print("\n=== Step 3: 查找并点击评论 ===")

    comment_found = False

    # 尝试多种方式查找评论tab
    comment_keywords = ["评论", "评价", "评价("]

    for keyword in comment_keywords:
        try:
            comment_elem = d(textContains=keyword)
            if comment_elem.exists:
                print(f"找到评论tab: {keyword}")
                comment_elem.click()
                comment_found = True
                break
        except Exception:
            pass

    time.sleep(2)

    screenshot_path = OUTPUT_DIR / "04_comments_section.png"
    d.screenshot(str(screenshot_path))
    print(f"评论区截图: {screenshot_path}")

    # Dump评论区XML
    xml_path = OUTPUT_DIR / "04_comments_section.xml"
    xml_content = d.dump_hierarchy()
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"评论区XML: {xml_path}")

    # Step 4: 分析评论元素
    print("\n=== Step 4: 分析评论元素 ===")
    analyze_comment_elements(xml_content)

    # Step 5: 测试滚动
    print("\n=== Step 5: 测试滚动 ===")
    for i in range(3):
        print(f"滚动 {i+1}/3")
        d.swipe(0.5, 0.75, 0.5, 0.25)
        time.sleep(1.5)

        screenshot_path = OUTPUT_DIR / f"05_scroll_{i+1}.png"
        d.screenshot(str(screenshot_path))

    # Dump滚动后的XML
    xml_path = OUTPUT_DIR / "05_after_scroll.xml"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(d.dump_hierarchy())

    print("\n=== 探索完成 ===")
    print(f"所有文件保存在: {OUTPUT_DIR}")


def analyze_comment_elements(xml_content: str):
    """分析评论列表的关键元素"""

    root = ET.fromstring(xml_content)

    # 收集所有resource-id
    all_ids = set()
    # 收集评论相关的text示例
    text_examples = []

    for node in root.iter():
        resource_id = node.attrib.get("resource-id", "")
        if resource_id and "com.heytap.market" in resource_id:
            all_ids.add(resource_id)

        text = node.attrib.get("text", "")
        if text and len(text) > 0 and len(text) < 200:
            class_name = node.attrib.get("class", "")
            clickable = node.attrib.get("clickable", "false")

            # 收集可能的评论内容
            if len(text) > 5 and "TextView" in class_name:
                text_examples.append({
                    "text": text[:50],
                    "class": class_name,
                    "resource_id": resource_id,
                    "clickable": clickable
                })

    print(f"\n找到 {len(all_ids)} 个resource-id:")
    for cid in sorted(all_ids):
        print(f"  - {cid}")

    print(f"\n找到 {len(text_examples)} 个文本元素示例 (前20个):")
    for i, example in enumerate(text_examples[:20]):
        print(f"  {i+1}. text='{example['text']}', id={example['resource_id'].split(':')[-1] if ':' in example['resource_id'] else example['resource_id']}")

    # 查找列表容器
    print("\n查找列表容器:")
    for node in root.iter():
        class_name = node.attrib.get("class", "")
        if "ListView" in class_name or "RecyclerView" in class_name:
            resource_id = node.attrib.get("resource-id", "")
            print(f"  class={class_name}, resource-id={resource_id}")


if __name__ == "__main__":
    explore_oppo_store()
