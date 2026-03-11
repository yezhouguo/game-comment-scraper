"""VIVO应用商店适配器

支持:
- 时间解析 (YYYY-MM-DD, HH:MM格式)
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
class VivoCommentData(CommentData):
    """VIVO评论数据（扩展版）"""
    time_str: str = ""          # 原始时间字符串
    time_type: str = ""         # 时间类型
    days_ago: Optional[int] = None  # 几天前
    like_count: Optional[int] = None  # 点赞数
    ip_location: Optional[str] = None  # IP归属地
    device_model: Optional[str] = None  # 设备型号


@dataclass
class VivoScrapeConfig:
    """VIVO采集配置"""
    max_count: int = 1000           # 最大评论数
    max_days: Optional[int] = None  # 最大天数限制（None=不限制）
    max_scrolls: int = 500          # 最大滚动次数
    progress_interval: int = 5      # 进度报告间隔（滚动次数）
    progress_callback: Optional[Callable[[int, int, Dict[str, Any]], None]] = None


class VivoAppStoreAdapter(BaseAppStoreAdapter):
    """VIVO应用商店适配器

    使用 market 协议直接跳转到应用详情页
    """

    APP_PACKAGE = "com.bbk.appstore"
    MARKET_SCHEME = "market://details?id={package}"

    # 导航按钮文本
    APP_DETAILS_TEXT = "查看应用详情"
    COMMENTS_TEXT = "评分及评论"

    # 评论数据定位符
    USER_ID_ID = "com.bbk.appstore:id/comment_user"
    COMMENT_CONTENT_ID = "com.bbk.appstore:id/expand_content_tv"
    COMMENT_TIME_ID = "com.bbk.appstore:id/time"
    COMMENT_LIKE_ID = "com.bbk.appstore:id/comment_like_count"
    IP_LOCATION_ID = "com.bbk.appstore:id/ip_address"
    DEVICE_MODEL_ID = "com.bbk.appstore:id/model"
    EXPAND_BTN_ID = "com.bbk.appstore:id/expand_tv"  # 展开按钮
    EXPAND_TEXT = "展开"

    def __init__(self, device: DeviceConnector):
        super().__init__(device)
        self.app_store = AppStore.VIVO
        self.d = device.device

    # ==================== 导航相关 ====================

    def open_app_store(self) -> None:
        """打开VIVO应用商店（不再需要单独打开）"""
        pass

    def search_game(self, game_name: str) -> None:
        """搜索游戏（不再需要，使用 market 协议直接跳转）"""
        pass

    def open_game_details(self) -> None:
        """通过 market 协议直接打开游戏详情页"""
        pass

    def open_details_by_package(self, package_name: str) -> None:
        """使用 market 协议直接跳转到应用详情页

        完整流程：
        1. market 协议跳转（进入预览页）
        2. 点击"查看应用详情"进入详情页
        3. 点击"评分及评论"进入评论页
        """
        url = self.MARKET_SCHEME.format(package=package_name)

        cmd = [
            "adb", "shell", "am", "start",
            "-a", "android.intent.action.VIEW",
            "-d", url,
            self.APP_PACKAGE
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            time.sleep(3)  # 等待页面加载
        except Exception:
            time.sleep(3)

        # 点击"查看应用详情"
        details_btn = self.d(text=self.APP_DETAILS_TEXT)
        if details_btn.exists:
            details_btn.click()
            time.sleep(2)

        # 点击"评分及评论"
        comments_btn = self.d(text=self.COMMENTS_TEXT)
        if comments_btn.exists:
            comments_btn.click()
            time.sleep(2)

    def open_comments_section(self) -> None:
        """打开评论区（已在 open_details_by_package 中处理）"""
        pass

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
        elif ":" in time_str:
            return "今天(HH:MM)"
        elif "-" in time_str and len(time_str) >= 8:
            return "完整日期(YYYY-MM-DD)"
        else:
            return "其他"

    @staticmethod
    def parse_time_to_days_ago(time_str: str) -> Optional[int]:
        """解析时间字符串，返回几天前

        VIVO时间格式:
        - "HH:MM" -> 0天（今天）
        - "YYYY-MM-DD" -> 计算天数差

        返回值:
            None: 无法解析
            0: 今天
            n: n天前
        """
        if not time_str:
            return None

        today = datetime.now().date()

        try:
            # "HH:MM" 格式 - 假设是今天
            if ":" in time_str and "-" not in time_str:
                return 0

            # "YYYY-MM-DD" 格式
            if "-" in time_str:
                parts = time_str.split("-")
                if len(parts) == 3:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    comment_date = datetime(year, month, day).date()
                    delta = (today - comment_date).days
                    return max(0, delta)

        except Exception:
            pass

        return None

    # ==================== 数据提取 ====================

    def expand_all_comments(self) -> None:
        """展开所有折叠的评论"""
        try:
            expand_btns = self.d(resourceId=self.EXPAND_BTN_ID, text=self.EXPAND_TEXT)
            if expand_btns.exists:
                count = len(expand_btns)
                # 从下往上点击，避免布局变化影响
                for i in range(count - 1, -1, -1):
                    try:
                        expand_btns[i].click()
                        time.sleep(0.1)  # 短暂等待展开动画
                    except Exception:
                        continue
                time.sleep(0.5)  # 等待所有展开完成
        except Exception:
            pass

    def extract_comments(self, config: VivoScrapeConfig) -> List[VivoCommentData]:
        """提取当前页面的评论数据

        VIVO的评论使用 expand_content_tv 来显示完整内容
        长评论默认折叠，需要点击"展开"按钮
        """
        comments = []

        # 先展开所有折叠的评论
        self.expand_all_comments()

        # 获取所有评论元素
        users = self.d(resourceId=self.USER_ID_ID)
        contents = self.d(resourceId=self.COMMENT_CONTENT_ID)
        times = self.d(resourceId=self.COMMENT_TIME_ID)
        likes = self.d(resourceId=self.COMMENT_LIKE_ID)

        if not users.exists or not contents.exists:
            return comments

        min_count = min(len(users), len(contents))

        for i in range(min_count):
            try:
                user_id = users[i].info.get('text', '')
                content = contents[i].info.get('text', '')
                time_str = times[i].info.get('text', '') if i < len(times) else ''
                like_str = likes[i].info.get('text', '') if i < len(likes) else ''

                if not content:
                    continue

                # 解析点赞数
                like_count = None
                if like_str:
                    try:
                        like_count = int(like_str)
                    except ValueError:
                        pass

                # 解析时间
                time_type = self.estimate_time_type(time_str)
                days_ago = self.parse_time_to_days_ago(time_str)

                # 时间筛选
                if config.max_days is not None and days_ago is not None:
                    if days_ago > config.max_days:
                        continue

                comments.append(VivoCommentData(
                    content=content,
                    user_id=user_id,
                    rating=None,
                    comment_date=None,
                    time_str=time_str,
                    time_type=time_type,
                    days_ago=days_ago,
                    like_count=like_count
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
        config: Optional[VivoScrapeConfig] = None
    ) -> List[VivoCommentData]:
        """
        完整的评论采集流程

        Args:
            game_name: 游戏名称
            package_name: 应用包名
            config: 采集配置（可选）

        Returns:
            评论数据列表
        """
        if config is None:
            config = VivoScrapeConfig()

        print(f"开始采集 {game_name} ({package_name})...")
        if config.max_days:
            print(f"  筛选条件: {config.max_days}天内")
        print(f"  目标数量: {config.max_count}条")

        # 导航到评论页面
        self.go_home()
        self.open_details_by_package(package_name)

        # 采集评论
        all_comments: List[VivoCommentData] = []
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
        config = VivoScrapeConfig(max_count=max_count)
        vivo_comments = self.scrape_game_comments(game_name, package_name, config)

        # 转换为旧格式
        legacy_comments = []
        for vc in vivo_comments:
            legacy_comments.append(CommentData(
                content=vc.content,
                user_id=vc.user_id,
                rating=vc.rating,
                comment_date=vc.comment_date
            ))

        return legacy_comments
