# 游戏评论采集项目 - 开发进度

## 项目概述

**目标**: 从华为、小米、OPPO、VIVO 应用市场采集游戏评论数据

**技术方案**:
- Python + uiautomator2 + atx-agent
- 通过 ADB USB 连接设备
- SQLite 数据库存储
- Excel 数据导出

**设备**: NLA-NX1 (Android 16), USB (serial: A7JDBB5B19100121)

---

## 项目结构

```
game-comment-scraper/
├── src/
│   ├── device/connector.py       # ✅ 设备连接管理 (支持 USB 连接)
│   ├── adapters/
│   │   ├── base.py              # ✅ 适配器基类
│   │   ├── huawei.py            # ✅ 华为应用市场适配器 (增强版)
│   │   ├── oppo.py              # ✅ OPPO应用市场适配器 (已完成)
│   │   ├── xiaomi.py            # ⏳ 小米适配器 (待实现)
│   │   └── vivo.py              # ⏳ VIVO 适配器 (待实现)
│   ├── models/comment.py         # ✅ 数据模型 (Game, Comment, AppStore)
│   ├── storage/repository.py     # ✅ 数据存储层 (CommentRepository)
│   └── scraper/collector.py      # ✅ 采集协调器
├── config/settings.py            # ✅ 配置文件
├── scripts/
│   ├── adapter_scrape.py         # ✅ 适配器便捷脚本
│   ├── scrape_to_excel.py        # ✅ 华为爬取脚本
│   ├── test_oppo.py              # ✅ OPPO测试脚本
│   └── debug_*.py                # 🔧 调试脚本
├── tests/
│   ├── test_huawei_adapter.py    # ✅ 单元测试
│   └── test_huawei_integration.py # ✅ 集成测试
├── data/
│   ├── huawei_*.xlsx             # 📊 华为采集数据
│   └── oppo_*.xlsx               # 📊 OPPO采集数据
└── docs/
    └── PROGRESS.md               # 📝 本文档
```

---

## 完成进度

### Phase 1: 项目框架 ✅
- [x] 创建项目目录结构
- [x] 安装依赖 (uiautomator2, SQLAlchemy, openpyxl)
- [x] 配置 Git 仓库

### Phase 2: 数据层 ✅
- [x] 数据模型 (Game, Comment, AppStore)
- [x] 存储 Repository (CRUD 操作)
- [x] 数据库设计

### Phase 3: 设备连接 ✅
- [x] DeviceConnector 类
- [x] USB 连接方法 `connect_usb()`
- [x] 设备: NLA-NX1 (Android 16)

### Phase 4: 应用市场适配器
| 应用市场 | 状态 | 说明 |
|---------|------|------|
| 华为 | ✅ 完成 | 增强版适配器 + 单元测试 + 集成测试 |
| OPPO | ✅ 完成 | 完整适配器 + 测试验证 |
| 小米 | ⏳ 待实现 | 框架已搭建 |
| VIVO | ⏳ 待实现 | 框架已搭建 |

### Phase 5: 数据导出 ✅
- [x] Excel 格式导出
- [x] 时间类型标注
- [x] 按天数统计

### Phase 6: 测试 ✅
- [x] 华为单元测试 (4/4 通过)
- [x] 华为集成测试 (2/2 通过)
- [x] OPPO功能测试 (通过)

---

## 华为应用市场适配器

### 核心类
```python
from src.adapters.huawei import HuaweiAppStoreAdapter, ScrapeConfig

adapter = HuaweiAppStoreAdapter(device)
config = ScrapeConfig(
    max_count=200,
    max_days=2,
    max_scrolls=100,
    progress_interval=5
)
comments = adapter.scrape_game_comments("王者荣耀", "com.tencent.tmgp.sgame", config)
```

### 导航流程
1. Market 协议跳转: `market://details?id={package_name}`
2. 点击"介绍": `resourceId="com.huawei.appmarket:id/other_appinfos"`, 点击左侧30%
3. 点击"评论": `textContains="评论"`
4. 滚动加载: `swipe(0.5, 0.75, 0.5, 0.25)`

### 元素定位
| 元素 | resource-id |
|------|-------------|
| 用户ID | `detail_comment_user_textview` |
| 评论内容 | `detail_comment_content_textview` |
| 评论时间 | `detail_comment_time_textview` |

### 时间格式解析
| 格式 | 示例 | 解析结果 |
|------|------|----------|
| HH:MM | `08:02` | 今天 (0天前) |
| 昨天 | `昨天` | 1天前 |
| YYYY/M/D | `2026/3/9` | 计算天数差 |

### 测试结果 (2026-03-11)
- 单元测试: 4/4 通过
- 集成测试: 2/2 通过
- 采集测试: 202条评论，2天内97条

---

## OPPO应用商店适配器

### 核心类
```python
from src.adapters.oppo import OppoAppStoreAdapter, OppoScrapeConfig

adapter = OppoAppStoreAdapter(device)
config = OppoScrapeConfig(
    max_count=200,
    max_days=2,
    max_scrolls=100,
    progress_interval=5
)
comments = adapter.scrape_game_comments("王者荣耀", "com.tencent.tmgp.sgame", config)
```

### 包名
`com.heytap.market` (注意：不是 com.oppo.market)

### 导航流程
1. Market 协议跳转: `market://details?id={package_name}`
2. 点击"应用详情": `resourceId="com.heytap.market:id/show_more_text"`
3. 点击"更多": `resourceId="com.heytap.market:id/tv_more_text"`
4. 点击"最热"切换到"最新": `resourceId="com.heytap.market:id/tv_sort"` → 点击"最新"
5. 滚动加载: `swipe(0.5, 0.75, 0.5, 0.25, duration=0.3)`

### 元素定位
| 元素 | resource-id |
|------|-------------|
| 用户ID | `com.heytap.market:id/tv_item_username` |
| 评论内容 | `com.heytap.market:id/expand_tv` |
| 评论时间 | `com.heytap.market:id/tv_item_time` |
| 点赞数 | `com.heytap.market:id/tv_item_praise` |

### 时间格式解析
| 格式 | 示例 | 解析结果 |
|------|------|----------|
| 刚刚 | `刚刚` | 0天前 |
| X分钟前 | `2 分钟前` | 0天前 |
| X小时前 | `3 小时前` | 0天前 |
| YYYY/MM/DD | `2026/02/04` | 计算天数差 |

### 测试结果 (2026-03-11)
- ✅ 50条测试: 105秒
- ✅ 100条测试 (max_days=1): 213秒，全部为今天评论
- ✅ 时间过滤功能正常

### 采集速度
- 约2.1秒/条评论
- 1000条约需35-40分钟

---

## 脚本使用说明

### 华为应用市场
```bash
# 测试模式 (10条)
python scripts/adapter_scrape.py test

# 采集指定数量
python scripts/adapter_scrape.py 100

# 采集指定天数内的评论
python scripts/adapter_scrape.py 200 --days 2
```

### OPPO应用市场
```bash
# 测试模式
python scripts/test_oppo.py
```

---

## 下一步计划

### 短期 (1-2天)
1. ⏳ 实现小米应用商店适配器
2. ⏳ 实现VIVO应用商店适配器

### 中期 (3-7天)
1. ⏳ 统一采集脚本
2. ⏳ 添加日志记录

### 长期
1. 支持更多应用市场
2. Web 界面展示
3. 定时采集任务

---

## 待办事项

- [ ] 实现小米应用商店适配器
- [ ] 实现VIVO应用商店适配器
- [ ] 统一采集脚本入口
- [ ] 添加更多测试游戏
- [ ] 添加日志记录
- [ ] 处理网络异常

### 已完成
- [x] 华为适配器 + 单元测试 + 集成测试
- [x] OPPO适配器 + 功能测试
- [x] 数据导出为 Excel
- [x] 时间解析与筛选
- [x] 去重机制

---

## 依赖项

```
uiautomator2>=3.0.0
SQLAlchemy>=2.0.0
openpyxl>=3.0.0
pandas
```

---

**最后更新**: 2026-03-11
**当前版本**: 0.4.0
**华为适配器**: ✅ 生产就绪
**OPPO适配器**: ✅ 生产就绪
