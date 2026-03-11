# Game Comment Scraper

从华为、小米、OPPO、VIVO 应用市场采集游戏评论数据的自动化工具。

## 功能特性

- 支持4大应用市场：华为、小米、OPPO、VIVO
- 自动滚动加载评论
- 数据存储到 SQLite 数据库
- 可配置采集数量和时间范围
- 模块化设计，易于扩展

## 技术栈

- Python 3.10+
- uiautomator2 - Android UI 自动化
- SQLAlchemy - 数据库 ORM
- pytest - 测试框架

## 安装

```bash
# 进入项目目录
cd /root/claudecode/game-comment-scraper

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 1. 设备准备

确保手机通过 ADB 无线连接：

```bash
# 检查设备连接
adb devices

# 初始化 atx-agent
python scripts/init_device.py 10.0.0.114:5555
```

### 2. 配置

编辑 `config/settings.py`，配置：
- 设备地址
- 游戏列表
- 采集参数

### 3. 运行采集

```bash
python scripts/scrape.py
```

### 4. 查询数据

```bash
python scripts/query.py
```

## 项目结构

```
game-comment-scraper/
├── src/              # 源代码
│   ├── device/       # 设备连接管理
│   ├── adapters/     # 应用市场适配器（框架已搭建，具体逻辑待实现）
│   ├── models/       # 数据模型
│   ├── storage/      # 数据存储层
│   ├── scraper/      # 采集协调器
│   └── utils/        # 工具函数
├── tests/            # 测试
├── config/           # 配置文件
├── scripts/          # 执行脚本
├── data/             # 数据存储目录
└── docs/             # 文档
```

## 开发状态

| 模块 | 状态 | 说明 |
|------|------|------|
| 数据模型 | ✅ 完成 | Game, Comment 模型 |
| 存储层 | ✅ 完成 | CommentRepository |
| 设备连接 | ✅ 完成 | DeviceConnector |
| 适配器框架 | ✅ 完成 | BaseAppStoreAdapter |
| 华为适配器 | ⏳ 待实现 | 框架已搭建 |
| 小米适配器 | ⏳ 待实现 | 框架已搭建 |
| OPPO适配器 | ⏳ 待实现 | 框架已搭建 |
| VIVO适配器 | ⏳ 待实现 | 框架已搭建 |
| 采集协调器 | ✅ 完成 | CommentCollector |
| 执行脚本 | ✅ 完成 | init, scrape, query |

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_storage.py -v

# 查看覆盖率
pytest --cov=src --cov-report=html
```

## 注意事项

1. 各应用市场的 UI 结构可能变化，需要更新适配器中的定位符
2. 采集时请遵守应用市场的使用条款
3. 建议在非高峰时段进行采集
4. 首次使用需要在手机上允许 uiautomator2 权限

## 下一步开发

1. **实现适配器**：根据实际应用市场 UI 实现 `open_app_store()`, `search_game()` 等方法
2. **UI 元素定位**：使用 `uiautomator2` 的 viewer 工具获取元素定位符
3. **错误处理**：添加更完善的异常处理和重试机制
4. **日志记录**：添加详细的日志记录
5. **性能优化**：优化滚动和采集性能

## License

MIT
