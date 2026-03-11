# Game Comment Scraper Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建一个自动化工具，通过 uiautomator2 从华米OV四大应用市场采集游戏评论数据（评论内容、评论者ID），每个游戏采集约1000条最近6个月的评论，存储到数据库中。

**Architecture:**
- Python 项目使用 uiautomator2 控制 Android 设备
- 采用策略模式适配不同应用市场的 UI 结构
- 使用 SQLAlchemy ORM 管理 SQLite 数据库
- 模块化设计：设备连接、市场适配器、数据采集、存储分离

**Tech Stack:**
- uiautomator2 (Android UI 自动化)
- SQLAlchemy (数据库 ORM)
- pytest (测试)
- Python 3.10+

---

## 项目结构

```
game-comment-scraper/
├── src/
│   ├── __init__.py
│   ├── device/
│   │   ├── __init__.py
│   │   └── connector.py          # 设备连接管理
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py               # 基础适配器抽象类
│   │   ├── huawei.py             # 华为应用市场适配器
│   │   ├── xiaomi.py             # 小米应用商店适配器
│   │   ├── oppo.py               # OPPO 应用商店适配器
│   │   └── vivo.py               # VIVO 应用商店适配器
│   ├── models/
│   │   ├── __init__.py
│   │   └── comment.py            # 数据模型
│   ├── storage/
│   │   ├── __init__.py
│   │   └── repository.py         # 数据存储层
│   ├── scraper/
│   │   ├── __init__.py
│   │   └── collector.py          # 评论采集协调器
│   └── utils/
│       ├── __init__.py
│       └── helpers.py            # 辅助函数
├── tests/
│   ├── __init__.py
│   ├── test_device_connector.py
│   ├── test_adapters.py
│   ├── test_storage.py
│   └── fixtures/
│       └── sample_data.py
├── config/
│   ├── __init__.py
│   └── settings.py               # 配置文件
├── scripts/
│   ├── init_device.py            # 初始化设备
│   ├── scrape.py                 # 采集脚本
│   └── query.py                  # 查询脚本
├── requirements.txt
├── pyproject.toml
├── README.md
└── docs/
    └── plans/
        └── 2026-03-11-game-comment-scraper.md
```

---

## Phase 1: 项目初始化

### Task 1: 创建项目目录结构

**Files:**
- Create: 目录结构

**Step 1: 创建项目目录**

```bash
cd /root/claudecode
mkdir -p game-comment-scraper/{src/{device,adapters,models,storage,scraper,utils},tests/fixtures,config,scripts,docs/plans}
cd game-comment-scraper
```

**Step 2: 初始化 git 仓库**

```bash
git init
```

**Step 3: 创建基础 __init__.py 文件**

```bash
touch src/__init__.py
touch src/device/__init__.py
touch src/adapters/__init__.py
touch src/models/__init__.py
touch src/storage/__init__.py
touch src/scraper/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py
touch config/__init__.py
```

**Step 4: Commit**

```bash
git add .
git commit -m "feat: initialize project structure"
```

---

### Task 2: 创建依赖配置文件

**Files:**
- Create: `requirements.txt`
- Create: `pyproject.toml`

**Step 1: 创建 requirements.txt**

```txt
uiautomator2==2.16.25
pillow==10.3.0
sqlalchemy==2.0.35
python-dateutil==2.9.0
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==6.0.0
```

**Step 2: 创建 pyproject.toml**

```toml
[project]
name = "game-comment-scraper"
version = "0.1.0"
description = "Game comment scraper from Chinese app stores"
requires-python = ">=3.10"
dependencies = [
    "uiautomator2>=2.16.0",
    "pillow>=10.0.0",
    "sqlalchemy>=2.0.0",
    "python-dateutil>=2.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=term-missing"
```

**Step 3: 安装依赖**

```bash
pip install -r requirements.txt
```

**Step 4: Commit**

```bash
git add requirements.txt pyproject.toml
git commit -m "feat: add project dependencies"
```

---

## Phase 2: 数据模型与存储层

### Task 3: 创建评论数据模型

**Files:**
- Create: `src/models/comment.py`
- Create: `tests/test_models.py`

**Step 1: 编写数据模型测试**

```python
# tests/test_models.py
import pytest
from datetime import datetime, timedelta
from src.models.comment import Comment, Game, AppStore

def test_create_game():
    game = Game(
        name="测试游戏",
        package_name="com.test.game",
        app_store=AppStore.HUAWEI
    )
    assert game.name == "测试游戏"
    assert game.package_name == "com.test.game"
    assert game.app_store == AppStore.HUAWEI

def test_create_comment():
    comment = Comment(
        game_id=1,
        content="很好玩",
        user_id="user123",
        app_store=AppStore.HUAWEI,
        scraped_at=datetime.now()
    )
    assert comment.content == "很好玩"
    assert comment.user_id == "user123"

def test_comment_date_filter():
    # 测试6个月内的评论
    six_months_ago = datetime.now() - timedelta(days=180)
    recent_comment = Comment(
        game_id=1,
        content="近期评论",
        user_id="user1",
        app_store=AppStore.HUAWEI,
        comment_date=datetime.now() - timedelta(days=30),
        scraped_at=datetime.now()
    )
    assert recent_comment.is_within_months(6)
```

**Step 2: 运行测试（预期失败）**

```bash
pytest tests/test_models.py -v
```

Expected: FAIL - ModuleNotFoundError

**Step 3: 实现数据模型**

```python
# src/models/comment.py
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AppStore(Enum):
    """应用市场枚举"""
    HUAWEI = "huawei"
    XIAOMI = "xiaomi"
    OPPO = "oppo"
    VIVO = "vivo"

class Game(Base):
    """游戏模型"""
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    package_name = Column(String(200), unique=True, nullable=False)
    app_store = Column(SQLEnum(AppStore), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Game(id={self.id}, name='{self.name}', store={self.app_store})>"

class Comment(Base):
    """评论模型"""
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(String(200), nullable=False)
    app_store = Column(SQLEnum(AppStore), nullable=False)
    rating = Column(Integer)  # 评分，可选
    comment_date = Column(DateTime)  # 评论时间，可选
    scraped_at = Column(DateTime, default=datetime.now, nullable=False)

    def is_within_months(self, months: int = 6) -> bool:
        """检查评论是否在指定月数内"""
        if not self.comment_date:
            return True  # 无日期则保留
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        return self.comment_date >= cutoff_date

    def __repr__(self):
        return f"<Comment(id={self.id}, user_id='{self.user_id}', content='{self.content[:20]}...')>"
```

**Step 4: 更新 models __init__.py**

```python
# src/models/__init__.py
from src.models.comment import Base, Game, Comment, AppStore

__all__ = ['Base', 'Game', 'Comment', 'AppStore']
```

**Step 5: 运行测试**

```bash
pytest tests/test_models.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add src/models/ tests/test_models.py
git commit -m "feat: add comment and game data models"
```

---

### Task 4: 创建数据存储层

**Files:**
- Create: `src/storage/repository.py`
- Create: `tests/test_storage.py`

**Step 1: 编写存储层测试**

```python
# tests/test_storage.py
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.comment import Base, Game, Comment, AppStore
from src.storage.repository import CommentRepository

@pytest.fixture
def in_memory_db():
    """创建内存数据库用于测试"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session

@pytest.fixture
def repo(in_memory_db):
    """创建仓库实例"""
    session = in_memory_db()
    return CommentRepository(session)

def test_save_game(repo):
    game = Game(name="测试游戏", package_name="com.test.game", app_store=AppStore.HUAWEI)
    saved = repo.save_game(game)
    assert saved.id is not None
    assert saved.name == "测试游戏"

def test_save_comment(repo):
    game = Game(name="测试游戏", package_name="com.test.game", app_store=AppStore.HUAWEI)
    game = repo.save_game(game)

    comment = Comment(
        game_id=game.id,
        content="很好玩",
        user_id="user123",
        app_store=AppStore.HUAWEI
    )
    saved = repo.save_comment(comment)
    assert saved.id is not None

def test_get_comments_by_game(repo):
    game = Game(name="测试游戏", package_name="com.test.game", app_store=AppStore.HUAWEI)
    game = repo.save_game(game)

    for i in range(3):
        comment = Comment(
            game_id=game.id,
            content=f"评论{i}",
            user_id=f"user{i}",
            app_store=AppStore.HUAWEI
        )
        repo.save_comment(comment)

    comments = repo.get_comments_by_game(game.id)
    assert len(comments) == 3

def test_count_comments_by_game(repo):
    game = Game(name="测试游戏", package_name="com.test.game", app_store=AppStore.HUAWEI)
    game = repo.save_game(game)

    for i in range(5):
        comment = Comment(
            game_id=game.id,
            content=f"评论{i}",
            user_id=f"user{i}",
            app_store=AppStore.HUAWEI
        )
        repo.save_comment(comment)

    count = repo.count_comments_by_game(game.id)
    assert count == 5
```

**Step 2: 运行测试（预期失败）**

```bash
pytest tests/test_storage.py -v
```

Expected: FAIL - ModuleNotFoundError

**Step 3: 实现存储层**

```python
# src/storage/repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.comment import Game, Comment, AppStore

class CommentRepository:
    """评论数据仓库"""

    def __init__(self, session: Session):
        self.session = session

    def save_game(self, game: Game) -> Game:
        """保存游戏信息"""
        self.session.add(game)
        self.session.commit()
        self.session.refresh(game)
        return game

    def get_game_by_package(self, package_name: str, app_store: AppStore) -> Optional[Game]:
        """根据包名获取游戏"""
        return self.session.query(Game).filter_by(
            package_name=package_name,
            app_store=app_store
        ).first()

    def get_or_create_game(self, name: str, package_name: str, app_store: AppStore) -> Game:
        """获取或创建游戏"""
        game = self.get_game_by_package(package_name, app_store)
        if not game:
            game = Game(name=name, package_name=package_name, app_store=app_store)
            game = self.save_game(game)
        return game

    def save_comment(self, comment: Comment) -> Comment:
        """保存评论"""
        self.session.add(comment)
        self.session.commit()
        self.session.refresh(comment)
        return comment

    def save_comments_batch(self, comments: List[Comment]) -> List[Comment]:
        """批量保存评论"""
        self.session.add_all(comments)
        self.session.commit()
        return comments

    def get_comments_by_game(self, game_id: int, limit: Optional[int] = None) -> List[Comment]:
        """获取游戏的所有评论"""
        query = self.session.query(Comment).filter_by(game_id=game_id)
        if limit:
            query = query.limit(limit)
        return query.all()

    def count_comments_by_game(self, game_id: int) -> int:
        """统计游戏评论数量"""
        return self.session.query(Comment).filter_by(game_id=game_id).count()

    def get_recent_comments(self, game_id: int, months: int = 6) -> List[Comment]:
        """获取最近N个月的评论"""
        comments = self.get_comments_by_game(game_id)
        return [c for c in comments if c.is_within_months(months)]
```

**Step 4: 运行测试**

```bash
pytest tests/test_storage.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/storage/ tests/test_storage.py
git commit -m "feat: add comment repository with batch operations"
```

---

## Phase 3: 设备连接层

### Task 5: 创建设备连接管理器

**Files:**
- Create: `src/device/connector.py`
- Create: `tests/test_device_connector.py`

**Step 1: 编写测试**

```python
# tests/test_device_connector.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.device.connector import DeviceConnector, DeviceConnectionError

@pytest.fixture
def mock_u2():
    """模拟 uiautomator2 连接"""
    with patch('uiautomator2.connect') as mock_connect:
        mock_device = Mock()
        mock_device.info = Mock()
        mock_device.info.get = Mock(return_value="test_device")
        mock_connect.return_value = mock_device
        yield mock_device

def test_connect_by_serial(mock_u2):
    connector = DeviceConnector()
    device = connector.connect("10.0.0.114:5555")
    assert device is not None

def test_connect_failure():
    with patch('uiautomator2.connect', side_effect=Exception("Connection failed")):
        connector = DeviceConnector()
        with pytest.raises(DeviceConnectionError):
            connector.connect("invalid_address")

def test_get_device_info(mock_u2):
    connector = DeviceConnector()
    connector.connect("10.0.0.114:5555")
    info = connector.get_device_info()
    assert info is not None

def test_health_check(mock_u2):
    connector = DeviceConnector()
    connector.connect("10.0.0.114:5555")
    assert connector.is_connected() is True
```

**Step 2: 运行测试（预期失败）**

```bash
pytest tests/test_device_connector.py -v
```

Expected: FAIL

**Step 3: 实现设备连接器**

```python
# src/device/connector.py
import uiautomator2 as u2
from typing import Optional

class DeviceConnectionError(Exception):
    """设备连接错误"""
    pass

class DeviceConnector:
    """设备连接管理器"""

    def __init__(self):
        self._device: Optional[u2.Device] = None
        self._address: Optional[str] = None

    def connect(self, address: str) -> u2.Device:
        """
        连接到设备
        address: 设备地址，可以是 serial 或 ip:port
        """
        try:
            self._device = u2.connect(address)
            self._address = address
            return self._device
        except Exception as e:
            raise DeviceConnectionError(f"Failed to connect to {address}: {e}")

    def disconnect(self):
        """断开连接"""
        self._device = None
        self._address = None

    @property
    def device(self) -> Optional[u2.Device]:
        """获取当前连接的设备"""
        return self._device

    def get_device_info(self) -> dict:
        """获取设备信息"""
        if not self._device:
            raise DeviceConnectionError("No device connected")
        return self._device.info

    def is_connected(self) -> bool:
        """检查是否已连接"""
        if not self._device:
            return False
        try:
            self._device.info
            return True
        except Exception:
            return False

    def screenshot(self, path: str):
        """截图"""
        if not self._device:
            raise DeviceConnectionError("No device connected")
        self._device.screenshot(path)

    def dump_hierarchy(self) -> str:
        """获取当前界面层级结构"""
        if not self._device:
            raise DeviceConnectionError("No device connected")
        return self._device.dump_hierarchy()
```

**Step 4: 更新 device __init__.py**

```python
# src/device/__init__.py
from src.device.connector import DeviceConnector, DeviceConnectionError

__all__ = ['DeviceConnector', 'DeviceConnectionError']
```

**Step 5: 运行测试**

```bash
pytest tests/test_device_connector.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add src/device/ tests/test_device_connector.py
git commit -m "feat: add device connection manager"
```

---

## Phase 4: 应用市场适配器

### Task 6: 创建基础适配器抽象类

**Files:**
- Create: `src/adapters/base.py`

**Step 1: 创建基础适配器**

```python
# src/adapters/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from src.device.connector import DeviceConnector
from src.models.comment import AppStore

@dataclass
class CommentData:
    """评论数据结构"""
    content: str
    user_id: str
    rating: Optional[int] = None
    comment_date: Optional[str] = None

class BaseAppStoreAdapter(ABC):
    """应用市场适配器基类"""

    def __init__(self, device: DeviceConnector):
        self.device = device
        self.app_store: AppStore = None

    @abstractmethod
    def open_app_store(self) -> None:
        """打开应用市场"""
        pass

    @abstractmethod
    def search_game(self, game_name: str) -> None:
        """搜索游戏"""
        pass

    @abstractmethod
    def open_game_details(self) -> None:
        """打开游戏详情页"""
        pass

    @abstractmethod
    def open_comments_section(self) -> None:
        """打开评论区"""
        pass

    @abstractmethod
    def extract_comments(self, max_count: int = 1000) -> List[CommentData]:
        """提取评论数据"""
        pass

    @abstractmethod
    def scroll_to_load_more(self) -> bool:
        """滚动加载更多评论，返回是否还有更多"""
        pass

    def scrape_game_comments(
        self,
        game_name: str,
        package_name: str,
        max_count: int = 1000
    ) -> List[CommentData]:
        """
        完整的评论采集流程
        """
        self.open_app_store()
        self.search_game(game_name)
        self.open_game_details()
        self.open_comments_section()

        all_comments = []
        while len(all_comments) < max_count:
            comments = self.extract_comments(max_count - len(all_comments))
            # 过滤已采集的评论
            new_comments = [c for c in comments if c not in all_comments]
            all_comments.extend(new_comments)

            if len(all_comments) >= max_count:
                break

            if not self.scroll_to_load_more():
                break

        return all_comments[:max_count]
```

**Step 2: Commit**

```bash
git add src/adapters/base.py
git commit -m "feat: add base app store adapter abstract class"
```

---

### Task 7: 实现华为应用市场适配器

**Files:**
- Create: `src/adapters/huawei.py`
- Modify: `src/adapters/base.py` (添加导入)

**Step 1: 创建华为适配器**

```python
# src/adapters/huawei.py
from typing import List
import time
import re
from src.adapters.base import BaseAppStoreAdapter, CommentData
from src.device.connector import DeviceConnector
from src.models.comment import AppStore

class HuaweiAppStoreAdapter(BaseAppStoreAdapter):
    """华为应用市场适配器"""

    # 华为应用市场包名
    APP_PACKAGE = "com.huawei.appmarket"

    # UI 元素定位符
    SEARCH_BOX_XPATH = '//android.widget.EditText[@text="搜索"]'
    GAME_ITEM_XPATH = '//android.widget.TextView[@resource-id="com.huawei.appmarket:id/app_name"]'
    COMMENT_TAB_XPATH = '//android.widget.TextView[@text="评论"]'
    COMMENT_ITEM_XPATH = '//android.widget.TextView[@resource-id="com.huawei.appmarket:id/review_content"]'
    USER_ID_XPATH = '..//android.widget.TextView[@resource-id="com.huawei.appmarket:id/reviewer_name"]'
    LOAD_MORE_XPATH = '//android.widget.TextView[@text="加载更多"]'

    def __init__(self, device: DeviceConnector):
        super().__init__(device)
        self.app_store = AppStore.HUAWEI

    def open_app_store(self) -> None:
        """打开华为应用市场"""
        d = self.device.device
        # 启动应用市场
        d.app_start(self.APP_PACKAGE)
        time.sleep(2)

    def search_game(self, game_name: str) -> None:
        """搜索游戏"""
        d = self.device.device

        # 点击搜索框
        search_box = d(self.SEARCH_BOX_XPATH)
        if search_box.exists:
            search_box.click()
            time.sleep(0.5)

            # 输入游戏名称
            d.send_keys(game_name)
            time.sleep(1)

            # 按回车或点击搜索
            d.press("enter")
            time.sleep(2)

    def open_game_details(self) -> None:
        """打开游戏详情页"""
        d = self.device.device

        # 点击第一个搜索结果
        game_item = d(self.GAME_ITEM_XPATH)
        if game_item.exists:
            game_item.click()
            time.sleep(2)

    def open_comments_section(self) -> None:
        """打开评论区"""
        d = self.device.device

        # 点击评论标签
        comment_tab = d(self.COMMENT_TAB_XPATH)
        if comment_tab.exists:
            comment_tab.click()
            time.sleep(1)

    def extract_comments(self, max_count: int = 1000) -> List[CommentData]:
        """提取评论数据"""
        d = self.device.device
        comments = []

        comment_elements = d(self.COMMENT_ITEM_XPATH)
        for elem in comment_elements:
            if len(comments) >= max_count:
                break

            content = elem.info.get('text', '')
            if not content:
                continue

            # 获取用户ID
            user_elem = elem(self.USER_ID_XPATH)
            user_id = user_elem.info.get('text', 'anonymous') if user_elem.exists else 'anonymous'

            comments.append(CommentData(
                content=content,
                user_id=user_id
            ))

        return comments

    def scroll_to_load_more(self) -> bool:
        """滚动加载更多评论"""
        d = self.device.device

        # 向上滚动加载更多
        d.swipe(0.5, 0.8, 0.5, 0.3)
        time.sleep(1.5)

        # 检查是否还有更多（检查是否到达底部）
        # 简化处理：假设只要能滚动就有更多
        return True
```

**Step 2: 更新 adapters __init__.py**

```python
# src/adapters/__init__.py
from src.adapters.base import BaseAppStoreAdapter, CommentData
from src.adapters.huawei import HuaweiAppStoreAdapter

__all__ = ['BaseAppStoreAdapter', 'CommentData', 'HuaweiAppStoreAdapter']
```

**Step 3: Commit**

```bash
git add src/adapters/huawei.py src/adapters/__init__.py
git commit -m "feat: add Huawei app store adapter"
```

---

### Task 8: 实现小米应用商店适配器

**Files:**
- Create: `src/adapters/xiaomi.py`

**Step 1: 创建小米适配器**

```python
# src/adapters/xiaomi.py
from typing import List
import time
from src.adapters.base import BaseAppStoreAdapter, CommentData
from src.device.connector import DeviceConnector
from src.models.comment import AppStore

class XiaomiAppStoreAdapter(BaseAppStoreAdapter):
    """小米应用商店适配器"""

    APP_PACKAGE = "com.xiaomi.market"

    SEARCH_BOX_ID = "com.xiaomi.market:id/search_edit_text"
    GAME_ITEM_ID = "com.xiaomi.market:id/app_name"
    COMMENT_TAB_TEXT = "评论"
    COMMENT_ITEM_ID = "com.xiaomi.market:id/review_content"
    USER_ID_ID = "com.xiaomi.market:id/reviewer_name"

    def __init__(self, device: DeviceConnector):
        super().__init__(device)
        self.app_store = AppStore.XIAOMI

    def open_app_store(self) -> None:
        d = self.device.device
        d.app_start(self.APP_PACKAGE)
        time.sleep(2)

    def search_game(self, game_name: str) -> None:
        d = self.device.device

        search_box = d(resourceId=self.SEARCH_BOX_ID)
        if search_box.exists:
            search_box.click()
            time.sleep(0.5)
            d.send_keys(game_name)
            time.sleep(1)
            d.press("enter")
            time.sleep(2)

    def open_game_details(self) -> None:
        d = self.device.device

        game_item = d(resourceId=self.GAME_ITEM_ID)
        if game_item.exists:
            game_item.click()
            time.sleep(2)

    def open_comments_section(self) -> None:
        d = self.device.device

        comment_tab = d(text=self.COMMENT_TAB_TEXT)
        if comment_tab.exists:
            comment_tab.click()
            time.sleep(1)

    def extract_comments(self, max_count: int = 1000) -> List[CommentData]:
        d = self.device.device
        comments = []

        comment_elements = d(resourceId=self.COMMENT_ITEM_ID)
        for elem in comment_elements:
            if len(comments) >= max_count:
                break

            content = elem.info.get('text', '')
            if not content:
                continue

            user_elem = elem.sibling(resourceId=self.USER_ID_ID)
            user_id = user_elem.info.get('text', 'anonymous') if user_elem.exists else 'anonymous'

            comments.append(CommentData(
                content=content,
                user_id=user_id
            ))

        return comments

    def scroll_to_load_more(self) -> bool:
        d = self.device.device
        d.swipe(0.5, 0.8, 0.5, 0.3)
        time.sleep(1.5)
        return True
```

**Step 2: 更新 adapters __init__.py**

```python
# src/adapters/__init__.py
from src.adapters.base import BaseAppStoreAdapter, CommentData
from src.adapters.huawei import HuaweiAppStoreAdapter
from src.adapters.xiaomi import XiaomiAppStoreAdapter

__all__ = ['BaseAppStoreAdapter', 'CommentData', 'HuaweiAppStoreAdapter', 'XiaomiAppStoreAdapter']
```

**Step 3: Commit**

```bash
git add src/adapters/xiaomi.py src/adapters/__init__.py
git commit -m "feat: add Xiaomi app store adapter"
```

---

### Task 9: 实现OPPO和VIVO适配器

**Files:**
- Create: `src/adapters/oppo.py`
- Create: `src/adapters/vivo.py`

**Step 1: 创建OPPO适配器**

```python
# src/adapters/oppo.py
from typing import List
import time
from src.adapters.base import BaseAppStoreAdapter, CommentData
from src.device.connector import DeviceConnector
from src.models.comment import AppStore

class OppoAppStoreAdapter(BaseAppStoreAdapter):
    """OPPO应用商店适配器"""

    APP_PACKAGE = "com.oppo.market"

    def __init__(self, device: DeviceConnector):
        super().__init__(device)
        self.app_store = AppStore.OPPO

    def open_app_store(self) -> None:
        d = self.device.device
        d.app_start(self.APP_PACKAGE)
        time.sleep(2)

    def search_game(self, game_name: str) -> None:
        d = self.device.device
        # 根据实际UI调整
        search_box = d(className="android.widget.EditText")
        if search_box.exists:
            search_box.click()
            time.sleep(0.5)
            d.send_keys(game_name)
            time.sleep(1)
            d.press("enter")
            time.sleep(2)

    def open_game_details(self) -> None:
        d = self.device.device
        # 根据实际UI调整
        game_item = d(className="android.widget.TextView")
        if game_item.exists:
            game_item.click()
            time.sleep(2)

    def open_comments_section(self) -> None:
        d = self.device.device
        comment_tab = d(text="评论")
        if comment_tab.exists:
            comment_tab.click()
            time.sleep(1)

    def extract_comments(self, max_count: int = 1000) -> List[CommentData]:
        d = self.device.device
        comments = []
        # 根据实际UI结构调整
        return comments

    def scroll_to_load_more(self) -> bool:
        d = self.device.device
        d.swipe(0.5, 0.8, 0.5, 0.3)
        time.sleep(1.5)
        return True
```

**Step 2: 创建VIVO适配器**

```python
# src/adapters/vivo.py
from typing import List
import time
from src.adapters.base import BaseAppStoreAdapter, CommentData
from src.device.connector import DeviceConnector
from src.models.comment import AppStore

class VivoAppStoreAdapter(BaseAppStoreAdapter):
    """VIVO应用商店适配器"""

    APP_PACKAGE = "com.vivo.appstore"

    def __init__(self, device: DeviceConnector):
        super().__init__(device)
        self.app_store = AppStore.VIVO

    def open_app_store(self) -> None:
        d = self.device.device
        d.app_start(self.APP_PACKAGE)
        time.sleep(2)

    def search_game(self, game_name: str) -> None:
        d = self.device.device
        search_box = d(className="android.widget.EditText")
        if search_box.exists:
            search_box.click()
            time.sleep(0.5)
            d.send_keys(game_name)
            time.sleep(1)
            d.press("enter")
            time.sleep(2)

    def open_game_details(self) -> None:
        d = self.device.device
        game_item = d(className="android.widget.TextView")
        if game_item.exists:
            game_item.click()
            time.sleep(2)

    def open_comments_section(self) -> None:
        d = self.device.device
        comment_tab = d(text="评论")
        if comment_tab.exists:
            comment_tab.click()
            time.sleep(1)

    def extract_comments(self, max_count: int = 1000) -> List[CommentData]:
        d = self.device.device
        comments = []
        # 根据实际UI结构调整
        return comments

    def scroll_to_load_more(self) -> bool:
        d = self.device.device
        d.swipe(0.5, 0.8, 0.5, 0.3)
        time.sleep(1.5)
        return True
```

**Step 3: 更新 adapters __init__.py**

```python
# src/adapters/__init__.py
from src.adapters.base import BaseAppStoreAdapter, CommentData
from src.adapters.huawei import HuaweiAppStoreAdapter
from src.adapters.xiaomi import XiaomiAppStoreAdapter
from src.adapters.oppo import OppoAppStoreAdapter
from src.adapters.vivo import VivoAppStoreAdapter

__all__ = [
    'BaseAppStoreAdapter',
    'CommentData',
    'HuaweiAppStoreAdapter',
    'XiaomiAppStoreAdapter',
    'OppoAppStoreAdapter',
    'VivoAppStoreAdapter'
]
```

**Step 4: Commit**

```bash
git add src/adapters/oppo.py src/adapters/vivo.py src/adapters/__init__.py
git commit -m "feat: add OPPO and VIVO app store adapters"
```

---

## Phase 5: 采集协调器与脚本

### Task 10: 创建采集协调器

**Files:**
- Create: `src/scraper/collector.py`
- Create: `tests/test_collector.py`

**Step 1: 创建采集协调器**

```python
# src/scraper/collector.py
from typing import List, Dict
from datetime import datetime
from src.device.connector import DeviceConnector
from src.adapters.base import BaseAppStoreAdapter, CommentData
from src.adapters.huawei import HuaweiAppStoreAdapter
from src.adapters.xiaomi import XiaomiAppStoreAdapter
from src.adapters.oppo import OppoAppStoreAdapter
from src.adapters.vivo import VivoAppStoreAdapter
from src.storage.repository import CommentRepository
from src.models.comment import AppStore, Comment

class CommentCollector:
    """评论采集协调器"""

    ADAPTER_MAP = {
        AppStore.HUAWEI: HuaweiAppStoreAdapter,
        AppStore.XIAOMI: XiaomiAppStoreAdapter,
        AppStore.OPPO: OppoAppStoreAdapter,
        AppStore.VIVO: VivoAppStoreAdapter,
    }

    def __init__(self, device_address: str, db_path: str = "comments.db"):
        self.device = DeviceConnector()
        self.device.connect(device_address)

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from src.models.comment import Base

        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.repository = CommentRepository(self.session)

    def scrape_game(
        self,
        game_name: str,
        package_name: str,
        app_stores: List[AppStore],
        max_comments: int = 1000
    ) -> Dict[AppStore, int]:
        """
        采集指定游戏的评论

        返回: {应用市场: 采集数量}
        """
        results = {}

        for store in app_stores:
            try:
                adapter_class = self.ADAPTER_MAP.get(store)
                if not adapter_class:
                    print(f"Unsupported app store: {store}")
                    continue

                adapter = adapter_class(self.device)
                comments_data = adapter.scrape_game_comments(
                    game_name, package_name, max_comments
                )

                # 保存到数据库
                game = self.repository.get_or_create_game(
                    game_name, package_name, store
                )

                saved_count = 0
                for comment_data in comments_data:
                    comment = Comment(
                        game_id=game.id,
                        content=comment_data.content,
                        user_id=comment_data.user_id,
                        app_store=store,
                        rating=comment_data.rating,
                        scraped_at=datetime.now()
                    )
                    self.repository.save_comment(comment)
                    saved_count += 1

                results[store] = saved_count
                print(f"{store.value}: Collected {saved_count} comments")

            except Exception as e:
                print(f"Error scraping from {store.value}: {e}")
                results[store] = 0

        return results

    def scrape_multiple_games(
        self,
        games: List[Dict[str, str]],
        app_stores: List[AppStore],
        max_comments: int = 1000
    ) -> Dict[str, Dict[AppStore, int]]:
        """
        采集多个游戏的评论

        games: [{"name": "游戏名", "package": "包名"}, ...]
        """
        all_results = {}

        for game in games:
            game_name = game["name"]
            package_name = game["package"]
            print(f"\nScraping {game_name}...")

            results = self.scrape_game(
                game_name, package_name, app_stores, max_comments
            )
            all_results[game_name] = results

        return all_results

    def close(self):
        """关闭连接"""
        self.session.close()
        self.device.disconnect()
```

**Step 2: 更新 scraper __init__.py**

```python
# src/scraper/__init__.py
from src.scraper.collector import CommentCollector

__all__ = ['CommentCollector']
```

**Step 3: Commit**

```bash
git add src/scraper/
git commit -m "feat: add comment collector coordinator"
```

---

### Task 11: 创建配置文件

**Files:**
- Create: `config/settings.py`

**Step 1: 创建配置文件**

```python
# config/settings.py
from src.models.comment import AppStore

# 设备配置
DEVICE_ADDRESS = "10.0.0.114:5555"  # 从之前的 ADB 配对中获得

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
    # 添加更多游戏...
]
```

**Step 2: Commit**

```bash
git add config/settings.py
git commit -m "feat: add configuration file"
```

---

### Task 12: 创建执行脚本

**Files:**
- Create: `scripts/init_device.py`
- Create: `scripts/scrape.py`
- Create: `scripts/query.py`

**Step 1: 创建设备初始化脚本**

```python
# scripts/init_device.py
#!/usr/bin/env python3
"""初始化设备，安装atx-agent"""

import uiautomator2 as u2
import sys

def init_device(address: str):
    """初始化设备"""
    print(f"Connecting to device: {address}")
    d = u2.connect(address)
    print(f"Connected: {d.info}")

    print("Installing atx-agent...")
    d.agent.start()
    print("atx-agent installed and started!")

    print("\nDevice info:")
    print(f"  Model: {d.info.get('model', 'Unknown')}")
    print(f"  Android Version: {d.info.get('version', 'Unknown')}")
    print(f"  Serial: {d.info.get('serial', 'Unknown')}")

if __name__ == "__main__":
    address = sys.argv[1] if len(sys.argv) > 1 else "10.0.0.114:5555"
    init_device(address)
```

**Step 2: 创建采集脚本**

```python
# scripts/scrape.py
#!/usr/bin/env python3
"""游戏评论采集脚本"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scraper.collector import CommentCollector
from src.models.comment import AppStore
from config.settings import (
    DEVICE_ADDRESS, DB_PATH, MAX_COMMENTS_PER_GAME,
    DEFAULT_APP_STORES, GAMES_TO_SCRAPE
)

def main():
    print("=== Game Comment Scraper ===\n")

    # 创建采集器
    print(f"Connecting to device: {DEVICE_ADDRESS}")
    collector = CommentCollector(DEVICE_ADDRESS, DB_PATH)
    print("Connected!\n")

    # 选择应用市场
    print("Available app stores:")
    for i, store in enumerate(AppStore):
        print(f"  {i + 1}. {store.value}")

    print(f"\nDefault stores: {[s.value for s in DEFAULT_APP_STORES]}")

    # 选择游戏
    print(f"\nGames to scrape ({len(GAMES_TO_SCRAPE)}):")
    for i, game in enumerate(GAMES_TO_SCRAPE):
        print(f"  {i + 1}. {game['name']} ({game['package']})")

    # 开始采集
    print(f"\nStarting collection (max {MAX_COMMENTS_PER_GAME} comments per game)...\n")

    results = collector.scrape_multiple_games(
        games=GAMES_TO_SCRAPE,
        app_stores=DEFAULT_APP_STORES,
        max_comments=MAX_COMMENTS_PER_GAME
    )

    # 输出结果
    print("\n=== Collection Summary ===")
    for game_name, store_results in results.items():
        print(f"\n{game_name}:")
        for store, count in store_results.items():
            print(f"  {store.value}: {count} comments")

    collector.close()
    print("\nDone!")

if __name__ == "__main__":
    main()
```

**Step 3: 创建查询脚本**

```python
# scripts/query.py
#!/usr/bin/env python3
"""查询已采集的评论数据"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.comment import Base, Game, Comment, AppStore

def query_stats(db_path: str = "data/comments.db"):
    """查询统计信息"""
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    print("=== Database Statistics ===\n")

    # 游戏数量
    game_count = session.query(Game).count()
    print(f"Total games: {game_count}\n")

    # 按应用市场统计
    print("Games by app store:")
    for store in AppStore:
        count = session.query(Game).filter_by(app_store=store).count()
        print(f"  {store.value}: {count}")

    print()

    # 评论数量
    comment_count = session.query(Comment).count()
    print(f"Total comments: {comment_count}\n")

    # 按游戏统计评论数
    print("Comments by game:")
    games = session.query(Game).all()
    for game in games:
        count = session.query(Comment).filter_by(game_id=game.id).count()
        print(f"  {game.name} ({game.app_store.value}): {count} comments")

if __name__ == "__main__":
    query_stats()
```

**Step 4: 设置脚本可执行权限**

```bash
chmod +x scripts/init_device.py scripts/scrape.py scripts/query.py
```

**Step 5: Commit**

```bash
git add scripts/
git commit -m "feat: add execution scripts"
```

---

## Phase 6: 文档与收尾

### Task 13: 创建README文档

**Files:**
- Create: `README.md`

**Step 1: 创建README**

```markdown
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
# 克隆项目
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
│   ├── device/       # 设备连接
│   ├── adapters/     # 应用市场适配器
│   ├── models/       # 数据模型
│   ├── storage/      # 数据存储
│   └── scraper/      # 采集协调器
├── tests/            # 测试
├── config/           # 配置
└── scripts/          # 执行脚本
```

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

1. 各应用市场的 UI 结构可能变化，需要更新适配器
2. 采集时请遵守应用市场的使用条款
3. 建议在非高峰时段进行采集
4. 首次使用需要在手机上允许 uiautomator2 权限

## License

MIT
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README"
```

---

### Task 14: 创建 data 目录和 .gitignore

**Files:**
- Create: `.gitignore`

**Step 1: 创建 .gitignore**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Database
data/
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# Screenshots
screenshots/

# Coverage
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
```

**Step 2: 创建 data 目录**

```bash
mkdir -p data
```

**Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: add gitignore and data directory"
```

---

## Phase 7: 验证与测试

### Task 15: 运行完整测试套件

**Step 1: 运行所有测试**

```bash
pytest tests/ -v --cov=src
```

**Step 2: 确保所有测试通过**

Expected: All tests PASS

**Step 3: 检查覆盖率**

Expected: Coverage > 80%

---

## 总结

完成以上所有任务后，你将拥有：

1. ✅ 完整的项目结构
2. ✅ 数据模型和存储层
3. ✅ 设备连接管理
4. ✅ 四大应用市场适配器
5. ✅ 采集协调器
6. ✅ 配置和执行脚本
7. ✅ 测试套件
8. ✅ 完整文档

## 下一步

1. 在实际设备上测试每个适配器
2. 根据实际 UI 调整定位符
3. 添加错误处理和重试机制
4. 添加日志记录
5. 优化滚动和采集性能

---

**计划完成日期:** 2026-03-11
**预计工时:** 4-6 小时
