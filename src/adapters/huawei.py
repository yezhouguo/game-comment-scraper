from typing import List, Optional
import time
import subprocess
from src.adapters.base import BaseAppStoreAdapter, CommentData
from src.device.connector import DeviceConnector
from src.models.comment import AppStore


class HuaweiAppStoreAdapter(BaseAppStoreAdapter):
    """华为应用市场适配器

    使用 market 协议直接跳转到应用详情页，无需搜索
    """

    APP_PACKAGE = "com.huawei.appmarket"
    MARKET_SCHEME = "market://details?id={package}"

    # 评论元素定位符
    COMMENT_TAB_TEXT = "评论"
    COMMENT_ROOT_ID = "com.huawei.appmarket:id/comment_root_view"

    # 评论数据定位符
    USER_ID_ID = "com.huawei.appmarket:id/detail_comment_user_textview"
    COMMENT_CONTENT_ID = "com.huawei.appmarket:id/detail_comment_content_textview"
    COMMENT_TIME_ID = "com.huawei.appmarket:id/detail_comment_time_textview"
    COMMENT_RATING_ID = "com.huawei.appmarket:id/detail_comment_stars_ratingbar"

    def __init__(self, device: DeviceConnector):
        super().__init__(device)
        self.app_store = AppStore.HUAWEI
        self.d = device.device

    def open_app_store(self) -> None:
        """打开华为应用市场（不再需要单独打开）"""
        pass

    def search_game(self, game_name: str) -> None:
        """搜索游戏（不再需要，使用 market 协议直接跳转）"""
        pass

    def open_game_details(self) -> None:
        """通过 market 协议直接打开游戏详情页"""
        # 这个方法现在由 open_details_by_package 替代
        pass

    def open_details_by_package(self, package_name: str) -> None:
        """使用 market 协议直接跳转到应用详情页

        完整流程：
        1. market 协议跳转
        2. 点击"介绍"进入真正详情页
        """
        # 构建 market 协议 URL
        url = self.MARKET_SCHEME.format(package=package_name)

        # 使用 adb shell am start 启动
        cmd = [
            "adb", "shell", "am", "start",
            "-a", "android.intent.action.VIEW",
            "-d", url,
            self.APP_PACKAGE
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            time.sleep(2)  # 等待页面加载
        except Exception:
            time.sleep(2)

        # 点击"介绍"进入真正的详情页
        # " | 介绍 | 隐私 | 权限" 元素的 bounds: left=318, right=483, top=315, bottom=343
        # 介绍位于左侧约30%位置
        intro_elem = self.d(resourceId="com.huawei.appmarket:id/other_appinfos")
        if intro_elem.exists:
            # 获取元素位置并点击"介绍"部分
            info = intro_elem.info
            bounds = info.get('bounds', {})
            if bounds:
                left = bounds.get('left', 318)
                right = bounds.get('right', 483)
                # "介绍"在左侧约30%处
                intro_x = left + (right - left) * 0.3
                intro_y = (bounds.get('top', 315) + bounds.get('bottom', 343)) / 2
                self.d.click(int(intro_x), int(intro_y))
                time.sleep(2)
            else:
                # 备选：直接点击估算位置
                self.d.click(350, 329)
                time.sleep(2)
        else:
            # 如果找不到元素，尝试直接点击估算位置
            self.d.click(350, 329)
            time.sleep(2)

    def open_comments_section(self) -> None:
        """打开评论区"""
        # 点击"评论"tab
        comment_tab = self.d(textContains=self.COMMENT_TAB_TEXT)
        if comment_tab.exists:
            comment_tab.click()
            time.sleep(1)

    def extract_comments(self, max_count: int = 1000) -> List[CommentData]:
        """提取当前页面的评论数据

        华为应用市场的评论元素是全局排列的，需要通过索引匹配用户和内容
        """
        comments = []

        # 直接获取所有用户ID和评论内容（全局获取）
        users = self.d(resourceId=self.USER_ID_ID)
        contents = self.d(resourceId=self.COMMENT_CONTENT_ID)

        if not users.exists or not contents.exists:
            return comments

        # 匹配用户和内容（成对出现）
        min_count = min(len(users), len(contents))

        for i in range(min_count):
            if len(comments) >= max_count:
                break

            try:
                user_id = users[i].info.get('text', 'anonymous')
                content = contents[i].info.get('text', '')

                if not content:
                    continue

                comments.append(CommentData(
                    content=content,
                    user_id=user_id,
                    rating=None,
                    comment_date=None
                ))

            except Exception:
                continue

        return comments

    def scroll_to_load_more(self) -> bool:
        """滚动加载更多评论"""
        # 向上滚动加载更多
        self.d.swipe(0.5, 0.75, 0.5, 0.25, duration=0.3)
        time.sleep(1.5)
        return True

    def go_home(self) -> None:
        """返回手机首页，准备下一次采集"""
        self.d.press("home")
        time.sleep(1)

    def scrape_game_comments(
        self,
        game_name: str,
        package_name: str,
        max_count: int = 1000
    ) -> List[CommentData]:
        """
        完整的评论采集流程（优化版本）

        新流程：
        1. 使用 market 协议直接跳转到详情页
        2. 点击评论区
        3. 滚动提取评论
        4. 返回首页
        """
        print(f"Scraping {game_name} ({package_name})...")

        # 直接跳转到详情页
        self.open_details_by_package(package_name)

        # 打开评论区
        self.open_comments_section()

        # 采集评论
        all_comments = []
        seen_contents = set()

        scroll_count = 0
        max_scrolls = 100

        while len(all_comments) < max_count and scroll_count < max_scrolls:
            comments = self.extract_comments(max_count - len(all_comments))

            # 去重
            new_comments = []
            for comment in comments:
                if comment.content not in seen_contents:
                    seen_contents.add(comment.content)
                    new_comments.append(comment)

            all_comments.extend(new_comments)

            if scroll_count % 5 == 0:  # 每5次滚动输出一次
                print(f"  Progress: {len(all_comments)} comments collected...")

            if len(all_comments) >= max_count:
                break

            if not new_comments:
                print("  No new comments, reached the end")
                break

            if not self.scroll_to_load_more():
                break

            scroll_count += 1

        print(f"  Collected {len(all_comments)} comments total")

        # 返回首页
        self.go_home()

        return all_comments[:max_count]
