import uiautomator2 as u2
from typing import Optional


class DeviceConnectionError(Exception):
    """设备连接错误"""
    pass


class DeviceConnector:
    """设备连接管理器"""

    def __init__(self):
        self._device: Optional[u2.Device] = None
        self._address: Optional[str] = None

    def connect(self, address: str) -> u2.Device:
        """
        连接到设备
        address: 设备地址，可以是 serial 或 ip:port
        """
        try:
            self._device = u2.connect(address)
            self._address = address
            return self._device
        except Exception as e:
            raise DeviceConnectionError(f"Failed to connect to {address}: {e}")

    def connect_usb(self) -> u2.Device:
        """通过 USB 连接到设备"""
        try:
            self._device = u2.connect_usb()
            self._address = "usb"
            return self._device
        except Exception as e:
            raise DeviceConnectionError(f"Failed to connect via USB: {e}")

    def disconnect(self):
        """断开连接"""
        self._device = None
        self._address = None

    @property
    def device(self) -> Optional[u2.Device]:
        """获取当前连接的设备"""
        return self._device

    def get_device_info(self) -> dict:
        """获取设备信息"""
        if not self._device:
            raise DeviceConnectionError("No device connected")
        return self._device.info

    def is_connected(self) -> bool:
        """检查是否已连接"""
        if not self._device:
            return False
        try:
            self._device.info
            return True
        except Exception:
            return False

    def screenshot(self, path: str):
        """截图"""
        if not self._device:
            raise DeviceConnectionError("No device connected")
        self._device.screenshot(path)

    def dump_hierarchy(self) -> str:
        """获取当前界面层级结构"""
        if not self._device:
            raise DeviceConnectionError("No device connected")
        return self._device.dump_hierarchy()
