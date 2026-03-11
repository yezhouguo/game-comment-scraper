from src.models.comment import AppStore

# 设备配置
DEVICE_ADDRESS = "10.0.0.114:5555"  # ADB 无线连接地址

# 数据库配置
DB_PATH = "data/comments.db"

# 采集配置
MAX_COMMENTS_PER_GAME = 1000
COMMENT_MONTHS_LIMIT = 6  # 最近6个月

# 默认采集的应用市场
DEFAULT_APP_STORES = [
    AppStore.HUAWEI,
    AppStore.XIAOMI,
    AppStore.OPPO,
    AppStore.VIVO,
]

# 游戏列表配置
GAMES_TO_SCRAPE = [
    {"name": "原神", "package": "com.miHoYo.GenshinImpact"},
    {"name": "王者荣耀", "package": "com.tencent.tmgp.sgame"},
    {"name": "和平精英", "package": "com.tencent.tmgp.pubgmhd"},
    {"name": "崩坏：星穹铁道", "package": "com.HoYoverse.hkrpgoversea"},
    # 添加更多游戏...
]
