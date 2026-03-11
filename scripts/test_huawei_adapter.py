#!/usr/bin/env python3
"""华为应用市场适配器测试脚本"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import uiautomator2 as u2
import time


class HuaweiAppStoreTester:
    """华为应用市场测试器"""

    # UI 元素定位符
    SEARCH_LAYOUT_ID = "com.huawei.appmarket:id/search_layout"
    SEARCH_BOX_ID = "com.huawei.appmarket:id/search_src_text"
    SEARCH_ICON_ID = "com.huawei.appmarket:id/hwsearchview_search_src_icon"

    def __init__(self):
        self.d = u2.connect_usb()

    def open_app_store(self):
        """打开华为应用市场"""
        print("Opening Huawei AppGallery...")
        self.d.app_start("com.huawei.appmarket")
        time.sleep(2)
        print("App opened!")

    def search_game(self, game_name: str, package_name: str):
        """搜索游戏"""
        print(f"Searching for {game_name}...")

        # 点击搜索框
        search_icon = self.d(resourceId=self.SEARCH_ICON_ID)
        if search_icon.exists:
            search_icon.click()
            time.sleep(1)
            print("Search icon clicked")
        else:
            # 尝试点击整个搜索布局
            search_layout = self.d(resourceId=self.SEARCH_LAYOUT_ID)
            if search_layout.exists:
                search_layout.click()
                time.sleep(1)
                print("Search layout clicked")

        # 输入游戏名称
        search_box = self.d(resourceId=self.SEARCH_BOX_ID)
        if search_box.exists:
            search_box.set_text(game_name)
            time.sleep(1)
            print(f"Entered: {game_name}")

            # 按回车搜索
            self.d.press("enter")
            time.sleep(2)
            print("Search submitted!")
        else:
            print("Search box not found!")

        # 截图
        self.d.screenshot("/tmp/huawei_search_results.png")
        print("Screenshot saved: /tmp/huawei_search_results.png")

    def analyze_search_results(self):
        """分析搜索结果页面"""
        xml = self.d.dump_hierarchy()

        print("\n=== Search Results Analysis ===")
        print("Finding game list items...")

        # 查找游戏列表项
        lines = xml.split('\n')
        for i, line in enumerate(lines):
            if 'app_name' in line or 'item_app' in line or 'game' in line.lower():
                print(line[:200])
                if i > 50:  # 只显示前50个匹配项
                    break

    def open_first_result(self):
        """打开第一个搜索结果"""
        print("\nOpening first result...")

        # 尝试多种方式点击第一个结果
        # 方式1: 通过 resource-id
        first_item = self.d(resourceId="com.huawei.appmarket:id/app_name")
        if first_item.exists:
            items = first_item
            items[0].click()
            print("Clicked via app_name")
            time.sleep(2)
            return

        # 方式2: 通过文本查找
        result = self.d(text="王者荣耀")
        if result.exists:
            result.click()
            print("Clicked via text '王者荣耀'")
            time.sleep(2)
            return

        # 方式3: 点击屏幕中央偏上位置
        self.d.click(0.5, 0.3)
        print("Clicked center position")
        time.sleep(2)

    def analyze_game_details(self):
        """分析游戏详情页"""
        xml = self.d.dump_hierarchy()

        print("\n=== Game Details Page Analysis ===")

        # 查找评论区相关元素
        keywords = ['comment', 'review', 'rating', 'score', '评论', '评分']
        lines = xml.split('\n')
        for i, line in enumerate(lines):
            if any(kw in line.lower() for kw in keywords):
                print(line[:200])
                if i > 100:
                    break

        self.d.screenshot("/tmp/huawei_game_details.png")
        print("Screenshot saved: /tmp/huawei_game_details.png")

    def find_and_click_comments(self):
        """查找并点击评论区"""
        print("\nLooking for comments section...")

        # 尝试通过文本查找"评论"
        comment_tab = self.d(text="评论")
        if comment_tab.exists:
            print("Found '评论' text!")
            comment_tab.click()
            time.sleep(2)
            return True

        # 尝试其他可能的文本
        for text in ["评价", "用户评价", "评论区", "Reviews"]:
            elem = self.d(text=text)
            if elem.exists:
                print(f"Found '{text}' text!")
                elem.click()
                time.sleep(2)
                return True

        print("Comments section not found, showing screenshot...")
        self.d.screenshot("/tmp/huawei_no_comments.png")
        return False

    def analyze_comments_page(self):
        """分析评论页面"""
        xml = self.d.dump_hierarchy()

        print("\n=== Comments Page Analysis ===")

        lines = xml.split('\n')
        for i, line in enumerate(lines):
            # 查找评论相关元素
            if any(kw in line.lower() for kw in ['content', 'text', 'user', 'reviewer', '评论内容', '用户']):
                print(line[:200])
                if i > 200:
                    break

        self.d.screenshot("/tmp/huawei_comments_page.png")
        print("Screenshot saved: /tmp/huawei_comments_page.png")


def main():
    tester = HuaweiAppStoreTester()

    # 1. 打开应用市场
    tester.open_app_store()

    # 2. 搜索王者荣耀
    tester.search_game("王者荣耀", "com.tencent.tmgp.sgame")

    # 3. 分析搜索结果
    tester.analyze_search_results()

    # 4. 打开第一个结果
    tester.open_first_result()

    # 5. 分析详情页
    tester.analyze_game_details()

    # 6. 点击评论区
    if tester.find_and_click_comments():
        # 7. 分析评论页面
        tester.analyze_comments_page()


if __name__ == "__main__":
    main()
