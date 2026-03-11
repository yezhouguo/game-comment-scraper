#!/usr/bin/env python3
"""华为应用市场 - 爬取N条评论脚本

用法:
    python scripts/scrape_n.py          # 默认爬取50条
    python scripts/scrape_n.py 100      # 爬取100条
    python scripts/scrape_n.py 10       # 爬取10条
"""
import uiautomator2 as u2
import time
import subprocess
import sys

# 从命令行参数获取目标评论数量
try:
    TARGET_COUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 50
except ValueError:
    print("请输入有效的评论数量")
    sys.exit(1)

# 测试游戏配置
GAME_NAME = "王者荣耀"
PACKAGE_NAME = "com.tencent.tmgp.sgame"

print("=" * 60)
print(f"华为应用市场 - {GAME_NAME} 评论采集")
print(f"目标数量: {TARGET_COUNT} 条")
print("=" * 60)

# 连接设备
print("\n[1/3] 连接设备...")
d = u2.connect_usb()
print(f"    设备连接成功")

# 确保在首页
print("\n[2/3] 导航到评论页面...")
d.press("home")
time.sleep(1)

# Market 协议跳转
url = f"market://details?id={PACKAGE_NAME}"
cmd = ["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url, "com.huawei.appmarket"]
subprocess.run(cmd, capture_output=True)
time.sleep(3)

# 点击"介绍"tab
intro = d(resourceId="com.huawei.appmarket:id/other_appinfos")
b = intro.info.get('bounds', {})
x = b.get('left', 318) + (b.get('right', 483) - b.get('left', 318)) * 0.3
y = (b.get('top', 315) + b.get('bottom', 343)) / 2
d.click(int(x), int(y))
time.sleep(2)

# 点击"评论"tab
d(textContains="评论").click()
time.sleep(2)

print("\n[3/3] 开始采集评论...")
print("-" * 60)

# 采集评论
all_comments = []
seen = set()
scroll_count = 0
max_scrolls = 200  # 最大滚动次数

start_time = time.time()

while len(all_comments) < TARGET_COUNT and scroll_count < max_scrolls:
    # 获取所有用户ID和内容
    users = d(resourceId="com.huawei.appmarket:id/detail_comment_user_textview")
    contents = d(resourceId="com.huawei.appmarket:id/detail_comment_content_textview")

    # 匹配用户和内容（成对出现）
    min_count = min(len(users), len(contents))

    new_added = 0
    for i in range(min_count):
        uid = users[i].info.get('text', '')
        cont = contents[i].info.get('text', '')

        # 去重
        if cont and cont not in seen:
            seen.add(cont)
            all_comments.append({'user_id': uid, 'content': cont})
            new_added += 1

    # 进度报告（每5次滚动报告一次）
    if scroll_count % 5 == 0:
        print(f"    滚动 {scroll_count}: 已采集 {len(all_comments)}/{TARGET_COUNT} 条评论")

    if len(all_comments) >= TARGET_COUNT:
        break

    # 如果没有新评论，可能到底了
    if new_added == 0 and scroll_count > 5:
        print("    没有新评论，已到达底部")
        break

    # 滚动加载更多
    d.swipe(0.5, 0.75, 0.5, 0.25, duration=0.3)
    time.sleep(1.5)
    scroll_count += 1

elapsed_time = time.time() - start_time

print("-" * 60)
print(f"\n采集完成!")
print(f"    实际采集: {len(all_comments)} 条")
print(f"    耗时: {elapsed_time:.1f} 秒")
if len(all_comments) > 0:
    print(f"    平均速度: {elapsed_time/len(all_comments):.2f} 秒/条")

# 展示所有评论
print("\n" + "=" * 60)
print("评论详情")
print("=" * 60)

for i, c in enumerate(all_comments, 1):
    # 匿名化处理用户ID
    uid = c['user_id'] or "匿名"
    if len(uid) > 4:
        masked = f"{uid[:2]}***{uid[-2:]}"
    else:
        masked = f"{'*' * (len(uid) - 1)}{uid[-1:]}"

    content = c['content']
    # 截断过长的评论用于展示
    display = content[:80] + "..." if len(content) > 80 else content

    print(f"\n[{i}] {masked}")
    print(f"    {display}")

# 返回首页
d.press("home")
time.sleep(1)

print("\n" + "=" * 60)
print(f"采集完成，共 {len(all_comments)} 条评论")
print("=" * 60)
