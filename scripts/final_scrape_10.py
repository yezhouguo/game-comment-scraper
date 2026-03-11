#!/usr/bin/env python3
import uiautomator2 as u2
import time
import subprocess

d = u2.connect_usb()

# 确保在评论页面
d.press("home")
time.sleep(1)

# 跳转
url = "market://details?id=com.tencent.tmgp.sgame"
cmd = ["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url, "com.huawei.appmarket"]
subprocess.run(cmd, capture_output=True)
time.sleep(3)

# 点击介绍
intro = d(resourceId="com.huawei.appmarket:id/other_appinfos")
b = intro.info.get('bounds', {})
x = b.get('left', 318) + (b.get('right', 483) - b.get('left', 318)) * 0.3
y = (b.get('top', 315) + b.get('bottom', 343)) / 2
d.click(int(x), int(y))
time.sleep(2)

# 点击评论
d(textContains="评论").click()
time.sleep(2)

print("Scraping 10 comments...\n")

all_comments = []
seen = set()
scroll_count = 0

while len(all_comments) < 10 and scroll_count < 20:
    # 获取所有用户ID和内容
    users = d(resourceId="com.huawei.appmarket:id/detail_comment_user_textview")
    contents = d(resourceId="com.huawei.appmarket:id/detail_comment_content_textview")

    # 匹配用户和内容（成对出现）
    user_count = len(users)
    content_count = len(contents)
    min_count = min(user_count, content_count)

    for i in range(min_count):
        uid = users[i].info.get('text', '')
        cont = contents[i].info.get('text', '')

        # 去重
        if cont and cont not in seen:
            seen.add(cont)
            all_comments.append({'user_id': uid, 'content': cont})

            if len(all_comments) <= 10:
                print(f"[{len(all_comments)}] {uid}: {cont[:50]}...")

    if len(all_comments) >= 10:
        break

    # 滚动加载更多
    d.swipe(0.5, 0.75, 0.5, 0.25, duration=0.3)
    time.sleep(1.5)
    scroll_count += 1

print(f"\n=== Collected {len(all_comments)} comments ===\n")
for i, c in enumerate(all_comments, 1):
    print(f"[{i}] {c['user_id']}")
    print(f"    {c['content']}")
    print()

# 返回首页
d.press("home")
time.sleep(1)
print("Done!")
