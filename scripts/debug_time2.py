#!/usr/bin/env python3 -u
"""调试时间元素 - 详细版本"""
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

# 检查用户和内容数量
users = d(resourceId="com.huawei.appmarket:id/detail_comment_user_textview")
contents = d(resourceId="com.huawei.appmarket:id/detail_comment_content_textview")
times = d(resourceId="com.huawei.appmarket:id/detail_comment_time_textview")

print(f"用户数量: {len(users)}")
print(f"内容数量: {len(contents)}")
print(f"时间数量: {len(times)}")

# 滚动几次，获取更多评论
for scroll in range(3):
    d.swipe(0.5, 0.75, 0.5, 0.25, duration=0.3)
    time.sleep(1.5)

# 再次检查
users = d(resourceId="com.huawei.appmarket:id/detail_comment_user_textview")
contents = d(resourceId="com.huawei.appmarket:id/detail_comment_content_textview")
times = d(resourceId="com.huawei.appmarket:id/detail_comment_time_textview")

print(f"\n滚动后:")
print(f"用户数量: {len(users)}")
print(f"内容数量: {len(contents)}")
print(f"时间数量: {len(times)}")

# 显示前几条的时间
print(f"\n前10条时间:")
for i in range(min(10, len(times))):
    t = times[i].info.get('text', '')
    print(f"  [{i}] {t}")

# 导出 XML 分析
xml_path = "/tmp/huawei_comments.xml"
d.dump_hierarchy(xml_path)
print(f"\nXML 已导出到: {xml_path}")

# 查找所有包含时间格式的文本
import re
with open(xml_path, 'r', encoding='utf-8') as f:
    xml_content = f.read()

# 查找可能包含日期/时间的文本
time_patterns = re.findall(r'text="(\d{1,2}:\d{2})"', xml_content)
print(f"\n找到的时间格式 (HH:MM): {len(time_patterns)} 个")
for i, t in enumerate(time_patterns[:20]):
    print(f"  [{i}] {t}")

# 查找日期格式
date_patterns = re.findall(r'text="(\d{1,2}-\d{1,2})"', xml_content)
print(f"\n找到的日期格式 (MM-DD): {len(date_patterns)} 个")
for i, t in enumerate(date_patterns[:20]):
    print(f"  [{i}] {t}")

# 查找完整的日期时间格式
full_patterns = re.findall(r'text="(\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{2})"', xml_content)
print(f"\n找到的完整日期时间: {len(full_patterns)} 个")
for i, t in enumerate(full_patterns[:10]):
    print(f"  [{i}] {t}")

d.press("home")
