#!/usr/bin/env python3 -u
"""调试时间元素获取"""
import uiautomator2 as u2
import time
import subprocess

d = u2.connect_usb()

# 导航到评论页面
d.press("home")
time.sleep(1)

url = "market://details?id=com.tencent.tmgp.sgame"
cmd = ["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url, "com.huawei.appmarket"]
subprocess.run(cmd, capture_output=True)
time.sleep(3)

intro = d(resourceId="com.huawei.appmarket:id/other_appinfos")
b = intro.info.get('bounds', {})
x = b.get('left', 318) + (b.get('right', 483) - b.get('left', 318)) * 0.3
y = (b.get('top', 315) + b.get('bottom', 343)) / 2
d.click(int(x), int(y))
time.sleep(2)

d(textContains="评论").click()
time.sleep(2)

# 检查时间元素
print("检查时间元素...")

# 方式1: 通过 resource-id
times_1 = d(resourceId="com.huawei.appmarket:id/detail_comment_time_textview")
print(f"方式1 (resource-id): 找到 {len(times_1)} 个元素")
if len(times_1) > 0:
    for i in range(min(5, len(times_1))):
        print(f"  [{i}] {times_1[i].info.get('text', '')}")

# 方式2: 获取完整 XML，查找时间相关元素
xml = d.dump_hierarchy()
import re
# 查找包含时间特征的字段
time_patterns = re.findall(r'detail_comment_time_textview[^>]*text="([^"]*)"', xml)
print(f"\n方式2 (XML解析): 找到 {len(time_patterns)} 个时间元素")
for i, t in enumerate(time_patterns[:10]):
    print(f"  [{i}] {t}")

# 方式3: 列出所有包含 "textView" 的 resource-id
all_textviews = re.findall(r'resource-id="([^"]*textView[^"]*)"[^>]*text="([^"]*)"', xml)
print(f"\n所有 textView 元素 (前20个):")
seen_ids = {}
for rid, text in all_textviews:
    if 'comment' in rid.lower() and rid not in seen_ids:
        seen_ids[rid] = text
        print(f"  {rid}: {text[:50] if text else '(empty)'}")
        if len(seen_ids) >= 10:
            break

d.press("home")
