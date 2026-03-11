#!/usr/bin/env python3 -u
"""检查华为应用市场评论时间显示机制"""
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

# 滚动获取更多评论
for scroll in range(5):
    d.swipe(0.5, 0.75, 0.5, 0.25, duration=0.3)
    time.sleep(1.5)

# 检查所有可能的元素
print("=== 检查所有包含日期/时间格式的元素 ===")

# 检查是否有包含"天"、"小时"、"分钟"等文本的元素
day_texts = d(textContains="天前")
hour_texts = d(textContains="小时前")
minute_texts = d(textContains="分钟前")
yesterday_texts = d(textContains="昨天")

print(f"'天前' 元素: {len(day_texts)}")
if len(day_texts) > 0:
    for i in range(min(3, len(day_texts))):
        print(f"  [{i}] {day_texts[i].info.get('text', '')}")

print(f"'小时前' 元素: {len(hour_texts)}")
if len(hour_texts) > 0:
    for i in range(min(3, len(hour_texts))):
        print(f"  [{i}] {hour_texts[i].info.get('text', '')}")

print(f"'分钟前' 元素: {len(minute_texts)}")
if len(minute_texts) > 0:
    for i in range(min(3, len(minute_texts))):
        print(f"  [{i}] {minute_texts[i].info.get('text', '')}")

print(f"'昨天' 元素: {len(yesterday_texts)}")
if len(yesterday_texts) > 0:
    for i in range(min(3, len(yesterday_texts))):
        print(f"  [{i}] {yesterday_texts[i].info.get('text', '')}")

# 尝试获取当前页面所有文本
print("\n=== 获取评论区域的全部文本 ===")
comment_area = d(resourceId="com.huawei.appmarket:id/comment_root_view")
if comment_area.exists:
    print(f"评论区域存在，bounds: {comment_area.info.get('bounds', {})}")
else:
    print("评论区域不存在")

# 获取所有时间元素
times = d(resourceId="com.huawei.appmarket:id/detail_comment_time_textview")
print(f"\n时间元素数量: {len(times)}")
print("前15条时间:")
for i in range(min(15, len(times))):
    t = times[i].info.get('text', '')
    print(f"  [{i}] '{t}'")

# 检查是否有其他可能包含日期的元素
print("\n=== 搜索可能包含日期的所有文本元素 ===")
# 使用正则搜索包含日期格式的文本
all_elements = d.xpath("//*[contains(@text, '-')]").all()
date_elements = []
for elem in all_elements:
    text = elem.info.get('text', '')
    if text and '-' in text and any(c.isdigit() for c in text):
        date_elements.append(text)

print(f"包含 '-' 的文本元素: {len(date_elements)}")
for i, t in enumerate(date_elements[:20]):
    print(f"  [{i}] {t}")

d.press("home")
print("\n=== 结论 ===")
print("华为应用市场评论时间格式: 只有 HH:MM，没有日期信息")
print("这意味着无法精确筛选2天内的评论")
print("\n可能的解决方案:")
print("1. 假设评论按时间倒序排列，采集固定数量（如1000条）")
print("2. 点击每条评论进入详情页获取完整时间")
print("3. 接受现状，采集所有可用评论后在Excel中手动筛选")
