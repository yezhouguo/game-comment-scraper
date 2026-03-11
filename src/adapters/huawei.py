"""华为应用市场适配器 - 增强版

支持:
- 时间解析 (HH:MM、昨天、YYYY/M/D)
- 条数限制
- 天数限制
- 进度回调
"""
from typing import List, Optional, Callable, Dict, Any
import time
import subprocess
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.adapters.base import BaseAppStoreAdapter, CommentData
from src.device.connector import DeviceConnector
from src.models.comment import AppStore


@dataclass
class HuaweiCommentData(CommentData):
    """华为评论数据（扩展版）"""
    time_str: str = ""          # 原始时间字符串
    time_type: str = ""         # 时间类型（今天/昨天/完整日期等）
    days_ago: Optional[int] = None  # 几天前


@dataclass
class ScrapeConfig:
    """采集配置"""
    max_count: int = 1000           # 最大评论数
    max_days: Optional[int] = None  # 最大天数限制（None=不限制）
    max_scrolls: int = 500          # 最大滚动次数
    progress_interval: int = 5      # 进度报告间隔（滚动次数）
    progress_callback: Optional[Callable[[int, int, Dict[str, Any]], None]] = None
    # progress_callback(collected_count, scroll_count, stats_dict)


class HuaweiAppStoreAdapter(BaseAppStoreAdapter):
    """华为应用市场适配器（增强版）

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

    # ==================== 导航相关 ====================

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
        intro_elem = self.d(resourceId="com.huawei.appmarket:id/other_appinfos")
        if intro_elem.exists:
            info = intro_elem.info
            bounds = info.get('bounds', {})
            if bounds:
                left = bounds.get('left', 318)
                right = bounds.get('right', 483)
                intro_x = left + (right - left) * 0.3
                intro_y = (bounds.get('top', 315) + bounds.get('bottom', 343)) / 2
                self.d.click(int(intro_x), int(intro_y))
                time.sleep(2)
            else:
                self.d.click(350, 329)
                time.sleep(2)
        else:
            self.d.click(350, 329)
            time.sleep(2)

    def open_comments_section(self) -> None:
        """打开评论区"""
        comment_tab = self.d(textContains=self.COMMENT_TAB_TEXT)
        if comment_tab.exists:
            comment_tab.click()
            time.sleep(1)

    def go_home(self) -> None:
        """返回手机首页，准备下一次采集"""
        self.d.press("home")
        time.sleep(1)

    # ==================== 时间解析 ====================

    @staticmethod
    def estimate_time_type(time_str: str) -> str:
        """判断时间类型"""
        if not time_str:
            return "未知"
        elif "昨天" in time_str:
            return "昨天"
        elif "前" in time_str:
            return "相对时间"
        elif ":" in time_str and "/" not in time_str:
            return "今天(HH:MM)"
        elif "/" in time_str:
            return "完整日期"
        elif "-" in time_str and len(time_str) < 10:
            return "日期(MM-DD)"
        else:
            return "其他"

    @staticmethod
    def parse_time_to_days_ago(time_str: str) -> Optional[int]:
        """解析时间字符串，返回几天前

        返回值:
            None: 无法解析
            0: 今天
            1: 昨天
            n: n天前
        """
        if not time_str:
            return None

        today = datetime.now().date()

        try:
            # "昨天"
            if "昨天" in time_str:
                return 1

            # "2026/3/9" 格式
            if "/" in time_str and "年" not in time_str:
                parts = time_str.split("/")
                if len(parts) == 3:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    comment_date = datetime(year, month, day).date()
                    delta = (today - comment_date).days
                    return max(0, delta)

            # "YYYY-MM-DD" 格式
            if "-" in time_str and len(time_str) >= 10:
                comment_date = datetime.strptime(time_str, "%Y-%m-%d").date()
                delta = (today - comment_date).days
                return max(0, delta)

            # "MM-DD" 格式（假设是今年）
            if "-" in time_str and len(time_str) < 10:
                parts = time_str.split("-")
                if len(parts) == 2:
                    month, day = int(parts[0]), int(parts[1])
                    comment_date = datetime(today.year, month, day).date()
                    if comment_date > datetime.now().date():
                        comment_date = datetime(today.year - 1, month, day).date()
                    delta = (today - comment_date).days
                    return max(0, delta)

            # "HH:MM" 格式 - 假设是今天
            if ":" in time_str:
                return 0

        except Exception:
            pass

        return None

    # ==================== 数据提取 ====================

    def extract_comments(self, config: ScrapeConfig) -> List[HuaweiCommentData]:
        """提取当前页面的评论数据

        华为应用市场的评论元素是全局排列的，需要通过索引匹配用户和内容
        """
        comments = []

        # 获取所有评论元素
        users = self.d(resourceId=self.USER_ID_ID)
        contents = self.d(resourceId=self.COMMENT_CONTENT_ID)
        times = self.d(resourceId=self.COMMENT_TIME_ID)

        if not users.exists or not contents.exists:
            return comments

        min_count = min(len(users), len(contents), len(times) if times.exists else 0)

        for i in range(min_count):
            try:
                user_id = users[i].info.get('text', '')
                content = contents[i].info.get('text', '')
                time_str = times[i].info.get('text', '') if i < len(times) else ''

                if not content:
                    continue

                # 解析时间
                time_type = self.estimate_time_type(time_str)
                days_ago = self.parse_time_to_days_ago(time_str)

                # 时间筛选
                if config.max_days is not None and days_ago is not None:
                    if days_ago > config.max_days:
                        continue

                comments.append(HuaweiCommentData(
                    content=content,
                    user_id=user_id,
                    rating=None,
                    comment_date=None,
                    time_str=time_str,
                    time_type=time_type,
                    days_ago=days_ago
                ))

            except Exception:
                continue

        return comments

    def scroll_to_load_more(self) -> bool:
        """滚动加载更多评论"""
        self.d.swipe(0.5, 0.75, 0.5, 0.25, duration=0.3)
        time.sleep(1.5)
        return True

    # ==================== 主要采集方法 ====================

    def scrape_game_comments(
        self,
        game_name: str,
        package_name: str,
        config: Optional[ScrapeConfig] = None
    ) -> List[HuaweiCommentData]:
        """
        完整的评论采集流程（增强版）

        Args:
            game_name: 游戏名称
            package_name: 应用包名
            config: 采集配置（可选）

        Returns:
            评论数据列表
        """
        if config is None:
            config = ScrapeConfig()

        print(f"开始采集 {game_name} ({package_name})...")
        if config.max_days:
            print(f"  筛选条件: {config.max_days}天内")
        print(f"  目标数量: {config.max_count}条")

        # 导航到评论页面
        self.go_home()
        self.open_details_by_package(package_name)
        self.open_comments_section()

        # 采集评论
        all_comments: List[HuaweiCommentData] = []
        seen_contents = set()
        scroll_count = 0
        consecutive_no_new = 0

        # 统计信息
        time_stats: Dict[str, int] = {}
        days_stats: Dict[int, int] = {}

        start_time = time.time()

        while scroll_count < config.max_scrolls:
            # 提取当前页面的评论
            comments = self.extract_comments(config)

            # 去重并筛选
            new_comments = []
            batch_days_ago = []

            for comment in comments:
                if comment.content not in seen_contents:
                    seen_contents.add(comment.content)
                    new_comments.append(comment)

                    # 统计
                    time_stats[comment.time_type] = time_stats.get(comment.time_type, 0) + 1
                    if comment.days_ago is not None:
                        days_stats[comment.days_ago] = days_stats.get(comment.days_ago, 0) + 1
                        batch_days_ago.append(comment.days_ago)

            all_comments.extend(new_comments)

            # 进度报告
            if scroll_count % config.progress_interval == 0:
                max_days = max(batch_days_ago) if batch_days_ago else 0
                stats = {
                    'time_stats': time_stats.copy(),
                    'days_stats': days_stats.copy(),
                    'max_days_ago': max_days,
                    'elapsed': time.time() - start_time
                }

                if config.progress_callback:
                    config.progress_callback(len(all_comments), scroll_count, stats)

                # 默认输出
                time_info = ", ".join([f"{k}:{v}" for k, v in time_stats.items()])
                print(f"  滚动 {scroll_count}: 已采集 {len(all_comments)} 条 | 最旧: {max_days}天前 | ({time_info})", flush=True)

            # 检查是否达到目标数量
            if len(all_comments) >= config.max_count:
                print(f"  已达到目标数量 {config.max_count} 条")
                break

            # 检查是否有新评论
            if not new_comments:
                consecutive_no_new += 1
                if consecutive_no_new >= 5:
                    print("  没有新评论，已到达底部")
                    break
            else:
                consecutive_no_new = 0

            # 滚动加载更多
            if not self.scroll_to_load_more():
                break

            scroll_count += 1

        elapsed = time.time() - start_time
        print(f"  采集完成: {len(all_comments)} 条评论，耗时 {elapsed:.1f} 秒")

        # 返回首页
        self.go_home()

        return all_comments[:config.max_count]

    def scrape_to_legacy_format(
        self,
        game_name: str,
        package_name: str,
        max_count: int = 1000
    ) -> List[CommentData]:
        """采集并转换为旧格式（向后兼容）"""
        config = ScrapeConfig(max_count=max_count)
        huawei_comments = self.scrape_game_comments(game_name, package_name, config)

        # 转换为旧格式
        legacy_comments = []
        for hc in huawei_comments:
            legacy_comments.append(CommentData(
                content=hc.content,
                user_id=hc.user_id,
                rating=hc.rating,
                comment_date=hc.comment_date
            ))

        return legacy_comments
