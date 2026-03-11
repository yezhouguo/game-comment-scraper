#!/usr/bin/env python3
"""采集华为应用市场100条评论"""

import sys
sys.path.insert(0, '/root/claudecode/game-comment-scraper')

import uiautomator2 as u2
import time
import subprocess

d = u2.connect_usb()

# 步骤1: market 协议跳转
url = "market://details?id=com.tencent.tmgp.sgame"
cmd = ["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url, "com.huawei.appmarket"]
subprocess.run(cmd, capture_output=True)
time.sleep(3)
print("Step 1: Market protocol jump - Done")

# 步骤2: 点击"介绍"
intro_elem = d(resourceId="com.huawei.appmarket:id/other_appinfos")
if intro_elem.exists:
    info = intro_elem.info
    bounds = info.get('bounds', {})
    intro_x = bounds.get('left', 318) + (bounds.get('right', 483) - bounds.get('left', 318)) * 0.3
    intro_y = (bounds.get('top', 315) + bounds.get('bottom', 343)) / 2
    d.click(int(intro_x), int(intro_y))
    time.sleep(2)
    print("Step 2: Clicked '介绍' - Done")

# 步骤3: 点击"评论"
comment_tab = d(textContains="评论")
if comment_tab.exists:
    comment_tab.click()
    time.sleep(2)
    print("Step 3: Clicked '评论' - Done")

# 步骤4: 滚动并采集评论
all_comments = []
seen_contents = set()
max_count = 100

print(f"\nStep 4: Scraping {max_count} comments...")

scroll_count = 0
while len(all_comments) < max_count and scroll_count < 50:
    # 获取当前页面的评论
    comment_roots = d(resourceId="com.huawei.appmarket:id/comment_root_view")

    new_count = 0
    for root in comment_roots:
        if len(all_comments) >= max_count:
            break

        try:
            # 获取评论内容
            content_elem = root(resourceId="com.huawei.appmarket:id/detail_comment_content_textview")
            if content_elem.exists:
                content = content_elem.info.get('text', '')

                # 去重
                if content and content not in seen_contents:
                    seen_contents.add(content)

                    # 获取用户ID
                    user_elem = root(resourceId="com.huawei.appmarket:id/detail_comment_user_textview")
                    user_id = user_elem.info.get('text', 'anonymous') if user_elem.exists else 'anonymous'

                    # 获取时间
                    time_elem = root(resourceId="com.huawei.appmarket:id/detail_comment_time_textview")
                    comment_time = time_elem.info.get('text', '') if time_elem.exists else ''

                    all_comments.append({
                        'user_id': user_id,
                        'content': content,
                        'time': comment_time
                    })
                    new_count += 1
        except:
            pass

    if scroll_count % 5 == 0:
        print(f"  Scroll {scroll_count + 1}: {len(all_comments)} comments collected...")

    if len(all_comments) >= max_count:
        break

    # 滚动加载更多
    d.swipe(0.5, 0.75, 0.5, 0.25, duration=0.3)
    time.sleep(1.5)
    scroll_count += 1

print(f"\n✓ Collected {len(all_comments)} comments total!")

# 显示前20条评论
print("\n=== First 20 Comments ===")
for i, comment in enumerate(all_comments[:20], 1):
    print(f"\n[{i}] {comment['user_id']} ({comment['time']})")
    print(f"    {comment['content'][:100]}...")

# 返回首页
d.press("home")
time.sleep(1)
print("\nDone! Returned to home screen.")
