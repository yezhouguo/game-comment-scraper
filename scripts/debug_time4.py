#!/usr/bin/env python3 -u
"""深入分析华为应用市场评论时间格式"""
import uiautomator2 as u2
import time
import subprocess
from datetime import datetime, timedelta

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

print("=" * 60)
print("华为应用市场评论时间格式分析")
print("=" * 60)

# 不滚动，先看最新的评论
print("\n【初始状态 - 最新评论】")
times = d(resourceId="com.huawei.appmarket:id/detail_comment_time_textview")
print(f"时间元素数量: {len(times)}")
for i in range(min(10, len(times))):
    print(f"  [{i}] '{times[i].info.get('text', '')}'")

# 滚动10次，观察时间变化
for scroll in range(1, 16):
    d.swipe(0.5, 0.75, 0.5, 0.25, duration=0.3)
    time.sleep(1.5)

    times = d(resourceId="com.huawei.appmarket:id/detail_comment_time_textview")
    print(f"\n【滚动 {scroll} 次后】时间元素数量: {len(times)}")

    # 统计不同格式
    formats = {}
    for t in times:
        text = t.info.get('text', '')
        if text:
            # 判断格式
            if '昨天' in text:
                key = '昨天'
            elif '前' in text:
                key = '相对时间'
            elif ':' in text:
                key = 'HH:MM'
            elif '-' in text:
                key = 'MM-DD'
            else:
                key = '其他'
            formats[key] = formats.get(key, 0) + 1

    print(f"  格式统计: {formats}")

    # 显示前3个和最后3个时间
    if len(times) > 0:
        print(f"  前3个: ", end='')
        for i in range(min(3, len(times))):
            print(f"'{times[i].info.get('text', '')}' ", end='')
        print()
        if len(times) > 6:
            print(f"  后3个: ", end='')
            for i in range(max(0, len(times)-3), len(times)):
                print(f"'{times[i].info.get('text', '')}' ", end='')
            print()

print("\n" + "=" * 60)
print("结论:")
print("  - 最新评论显示相对时间（如'昨天'）")
print("  - 较旧评论显示 HH:MM 格式")
print("  - HH:MM 格式无法确定具体日期")
print("  - 建议：采集时记录所有格式，后续手动筛选或估算日期")
print("=" * 60)

d.press("home")
