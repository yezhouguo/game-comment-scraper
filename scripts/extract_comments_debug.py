#!/usr/bin/env python3
"""调试并提取华为应用市场评论"""

import uiautomator2 as u2
import time
import subprocess
import re

d = u2.connect_usb()

# 确保在评论页面
d.press("home")
time.sleep(1)

url = "market://details?id=com.tencent.tmgp.sgame"
cmd = ["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url, "com.huawei.appmarket"]
subprocess.run(cmd, capture_output=True)
time.sleep(3)

intro_elem = d(resourceId="com.huawei.appmarket:id/other_appinfos")
bounds = intro_elem.info.get('bounds', {})
intro_x = bounds.get('left', 318) + (bounds.get('right', 483) - bounds.get('left', 318)) * 0.3
intro_y = (bounds.get('top', 315) + bounds.get('bottom', 343)) / 2
d.click(int(intro_x), int(intro_y))
time.sleep(2)

d(textContains="评论").click()
time.sleep(2)

# 滚动几次
for i in range(2):
    d.swipe(0.5, 0.75, 0.5, 0.25, duration=0.3)
    time.sleep(1)

# 获取完整XML分析一条评论的结构
xml = d.dump_hierarchy()

# 找到 comment_root_view 的结构
print("=== Finding comment structure ===")
lines = xml.split('\n')
in_comment = False
capture_lines = []

for i, line in enumerate(lines):
    if 'comment_root_view' in line:
        in_comment = True

    if in_comment:
        capture_lines.append(line)

        # 捕获足够多行后停止
        if len(capture_lines) > 80:
            break

for line in capture_lines:
    print(line)

# 现在尝试提取评论
print("\n=== Extracting comments ===")
comment_roots = d(resourceId="com.huawei.appmarket:id/comment_root_view")
print(f"Found {len(comment_roots)} comment roots")

comments_data = []
for i, root in enumerate(comment_roots[:5]):
    print(f"\n--- Comment {i+1} ---")

    # 尝试获取内容（长文本）
    all_texts = []
    for elem in root:
        text = elem.info.get('text', '')
        if text and len(text) > 5:  # 至少5个字符
            rid = elem.info.get('resourceId', '')
            all_texts.append((rid, text))

    # 显示所有文本
    for rid, text in all_texts:
        if rid:
            rname = rid.split('/')[-1]
            print(f"  [{rname}]: {text[:60]}...")
        else:
            print(f"  [no-id]: {text[:60]}...")
