#!/usr/bin/env python3
"""初始化设备，安装atx-agent"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import uiautomator2 as u2


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
