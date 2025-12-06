from src.crawler.base_crawler import EastMoneyBaseSpider

import requests
from typing import List, Optional, Dict

class StockSearcher(EastMoneyBaseSpider):
    """
    股票搜索（支持代码、名称、拼音模糊搜索）

    使用示例：
        searcher = StockSearcher()
        results = searcher.search("宁德")
    """

    SEARCH_URL = "https://search-codetable.eastmoney.com/codetable/search/web"
    LAST_TRADING_DAY_URL = "https://www.szse.cn/api/report/exchange/onepersistenthour/monthList?"

    def __init__(
            self,
            session: Optional[requests.Session] = None,
            timeout: int = 10,
            page_size: int = 10,
    ):
        super().__init__(session, timeout)
        self.page_size = page_size
        self.headers["Referer"] = "https://www.eastmoney.com/"

    def search(self, keyword: str, page_index: int = 1) -> Optional[List[Dict]]:
        """
        搜索股票

        :param keyword: 搜索关键字（代码/名称/拼音）
        :param page_index: 页码
        :return: 搜索结果列表，失败返回 None
        """
        params = {
            "client": "web",
            "clientType": "webSuggest",
            "clientVersion": "lastest",
            "cb": self._generate_callback(),
            "keyword": keyword,
            "pageIndex": page_index,
            "pageSize": self.page_size,
            "securityFilter": "",
            "_": self._timestamp_ms(),
        }

        try:
            data = self._get_jsonp(self.SEARCH_URL, params)
            if data is None:
                print(f"[StockSearcher] 解析 JSONP 响应失败")
                return None

            if data.get("code") != "0":
                print(f"[StockSearcher] 接口错误: {data.get('msg')}")
                return None

            items = data.get("result")
            if not items:
                print(f"[StockSearcher] 未找到: '{keyword}'")
                return None

            return items

        except requests.RequestException as e:
            print(f"[StockSearcher] 请求出错: {e}")
            return None

    def last_trading_day(self) -> Optional[Dict]:
        """
        获取最近交易日信息

        :return: 包含交易日信息的字典，失败返回 None
        """
        # 保存原始headers
        original_headers = self.headers.copy()
        
        # 设置适合深交所API的请求头
        self.headers["Referer"] = "https://www.szse.cn/"
        self.headers["Host"] = "www.szse.cn"
        
        try:
            response = self._get(self.LAST_TRADING_DAY_URL)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[StockSearcher] 获取最近交易日信息出错: {e}")
            return None
        finally:
            # 恢复原始headers
            self.headers = original_headers

if __name__ == '__main__':
    searcher = StockSearcher()
    # 获取最近交易日信息
    last_trading_day = searcher.last_trading_day()
    print(f"api返回: {last_trading_day}")

    # 搜索股票
    results = searcher.search("赛力")
    print(f"api返回: {results}")
    if results:
        print("格式化搜索结果:")
        for item in results[:3]:
            print(f"  {item['code']} - {item['shortName']} ({item['securityTypeName']})")

