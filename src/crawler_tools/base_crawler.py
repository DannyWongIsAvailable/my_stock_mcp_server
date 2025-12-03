import re
import time
import json
import random
import requests
from abc import ABC
from typing import Optional, Dict, Any


class EastMoneyBaseSpider(ABC):
    """
    东方财富爬虫基类

    提供通用功能：
    - Session 管理
    - 请求头/Cookies 配置
    - JSONP 解析
    - 股票代码格式转换
    """

    # 子类可覆盖的默认配置
    DEFAULT_TIMEOUT = 10
    DEFAULT_HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/129.0.0.0 Safari/537.36"
        ),
    }

    def __init__(
            self,
            session: Optional[requests.Session] = None,
            timeout: int = None,
    ):
        self.session = session or requests.Session()
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.headers = self.DEFAULT_HEADERS.copy()
        self.cookies: Dict[str, str] = {}

    # ==================== 通用工具方法 ====================

    def _get(
            self,
            url: str,
            params: Dict[str, Any] = None,
            **kwargs
    ) -> requests.Response:
        """封装 GET 请求"""
        return self.session.get(
            url,
            params=params,
            headers=self.headers,
            cookies=self.cookies,
            timeout=self.timeout,
            **kwargs
        )

    def _get_json(self, url: str, params: Dict[str, Any] = None) -> Dict:
        """GET 请求并解析 JSON"""
        resp = self._get(url, params)
        resp.raise_for_status()
        return resp.json()

    def _get_jsonp(self, url: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """GET 请求并解析 JSONP"""
        resp = self._get(url, params)
        resp.raise_for_status()
        return self._parse_jsonp(resp.text)

    @staticmethod
    def _parse_jsonp(text: str) -> Optional[Dict]:
        """
        解析 JSONP 响应

        :param text: 形如 callback({...}) 的字符串
        :return: 解析后的字典，失败返回 None
        """
        match = re.search(r'^\w+\((.*)\)$', text.strip(), re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _generate_callback() -> str:
        """生成 jQuery 风格的 JSONP callback 名称"""
        rand_part = random.randint(10 ** 19, 10 ** 20 - 1)
        ts = int(time.time() * 1000)
        return f"jQuery{rand_part}_{ts}"

    @staticmethod
    def _timestamp_ms() -> int:
        """当前时间戳（毫秒）"""
        return int(time.time() * 1000)

    @staticmethod
    def format_secid(stock_code: str) -> str:
        """
        将股票代码转换为东方财富的 secid 格式

        支持格式：
        - "000977"      -> "0.000977" (深市)
        - "600000"      -> "1.600000" (沪市)
        - "000977.SZ"   -> "0.000977"
        - "600000.SH"   -> "1.600000"
        - "0.000977"    -> "0.000977" (已是 secid)

        :param stock_code: 股票代码
        :return: secid 格式字符串
        """
        code = stock_code.strip().upper()

        if "." in code:
            left, right = code.split(".", maxsplit=1)

            # 已经是 secid 格式
            if left in {"0", "1"} and right.isdigit():
                return f"{left}.{right}"

            # 带后缀格式：000977.SZ
            if right in {"SZ", "SH"}:
                market = "0" if right == "SZ" else "1"
                return f"{market}.{left}"

        # 纯数字代码
        if code.isdigit():
            # 6 开头沪市，其他深市
            market = "1" if code.startswith("6") else "0"
            return f"{market}.{code}"

        raise ValueError(f"无法解析股票代码: {stock_code}")







