#!/usr/bin/env python3
import uiautomator2 as u2
import time
import subprocess

d = u2.connect_usb()

# 跳转
url = "market://details?id=com.tencent.tmgp.sgame"
cmd = ["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url, "com.huawei.appmarket"]
subprocess.run(cmd, capture_output=True)
time.sleep(3)

# 点击"介绍"
intro_elem = d(resourceId="com.huawei.appmarket:id/other_appinfos")
bounds = intro_elem.info.get('bounds', {})
intro_x = bounds.get('left', 318) + (bounds.get('right', 483) - bounds.get('left', 318)) * 0.3
intro_y = (bounds.get('top', 315) + bounds.get('bottom', 343)) / 2
d.click(int(intro_x), int(intro_y))
time.sleep(2)

# 点击"评论"
d(textContains="评论").click()
time.sleep(2)

# 采集评论
all_comments = []
seen_contents = set()
max_count = 10

print(f"Scraping {max_count} comments...\n")

scroll_count = 0
while len(all_comments) < max_count and scroll_count < 30:
    # 获取评论根元素
    comment_roots = d(resourceId="com.huawei.appmarket:id/comment_root_view")

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

                    all_comments.append({
                        'user_id': user_id,
                        'content': content
                    })

                    if len(all_comments) <= max_count:
                        print(f"[{len(all_comments)}] {user_id}: {content[:50]}...")
        except:
            pass

    if len(all_comments) >= max_count:
        break

    # 滚动
    d.swipe(0.5, 0.75, 0.5, 0.25, duration=0.3)
    time.sleep(1.5)
    scroll_count += 1

print(f"\n✓ Collected {len(all_comments)} comments!\n")

# 显示所有评论
for i, comment in enumerate(all_comments, 1):
    print(f"[{i}] {comment['user_id']}")
    print(f"    {comment['content']}")
    print()

# 返回首页
d.press("home")
time.sleep(1)
print("Done! Back to home screen.")
