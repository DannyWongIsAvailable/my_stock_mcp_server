"""
网络爬虫数据源实现
src/stock_data_source.py
基于网络爬虫的数据源实现
"""

import logging
from typing import List, Optional, Dict
from .data_source_interface import FinancialDataInterface, DataSourceError, NoDataFoundError, LoginError

logger = logging.getLogger(__name__)


class WebCrawlerDataSource(FinancialDataInterface):
    """
    基于网络爬虫的数据源实现
    """
    
    def __init__(self):
        """        
        初始化网络爬虫数据源
        """
        self.kline_spider = None
        self.searcher = None
        logger.info("WebCrawler数据源实例已创建")
    
    def initialize(self) -> bool:
        """
        初始化数据源连接
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 初始化爬虫连接
            from src.crawler_tools.basic_data import StockSearcher
            from src.crawler_tools.technical_data import KlineSpider
            self.kline_spider = KlineSpider()
            self.searcher = StockSearcher()
            logger.info("WebCrawler连接成功")
            return True
        except Exception as e:
            logger.warning(f"WebCrawler初始化失败: {e}")
            return False

    def cleanup(self):
        """
        清理数据源连接，释放资源
        """
        # 清理爬虫连接（如果需要的话）
        self.kline_spider = None
        self.searcher = None
        logger.info("WebCrawler连接已清理")

    # ==================== 行情数据 ====================
    
    def get_historical_k_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        frequency: str = "d",
    ) -> List[Dict]:
        """
        获取K线数据（原始数据，不做格式化处理）

        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            frequency: K线周期，可选值: "d"(日), "w"(周), "m"(月), "5"(5分钟), "15"(15分钟), "30"(30分钟), "60"(60分钟)

        Returns:
            K线数据列表，每个元素是一个字典，包含原始字段

        Raises:
            LoginError: If login to the data source fails.
            NoDataFoundError: If no data is found for the query.
            DataSourceError: For other data source related errors.
            ValueError: If input parameters are invalid.
        """
        # 检查kline_spider是否已初始化
        if self.kline_spider is None:
            logger.error("爬虫未初始化")
            raise DataSourceError("爬虫未初始化，请先调用initialize()方法")

        # 将日期格式从 YYYY-MM-DD 转换为 YYYYMMDD
        beg = start_date.replace("-", "")
        end = end_date.replace("-", "")

        # 将frequency映射到klt参数
        frequency_map = {
            "5": 5,      # 5分钟
            "15": 15,    # 15分钟
            "30": 30,    # 30分钟
            "60": 60,    # 60分钟
            "d": 101,    # 日线
            "w": 102,    # 周线
            "m": 103     # 月线
        }

        klt = frequency_map.get(frequency, 101)  # 默认日线

        try:
            # 调用爬虫获取数据
            klines = self.kline_spider.get_klines(
                stock_code=stock_code,
                beg=beg,
                end=end,
                klt=klt,
                fqt=1  # 前复权
            )

            # 如果没有数据，抛出NoDataFoundError异常
            if not klines:
                logger.warning(f"未找到股票 {stock_code} 在 {start_date} 到 {end_date} 期间的K线数据")
                raise NoDataFoundError(f"未找到股票 {stock_code} 在 {start_date} 到 {end_date} 期间的K线数据")

            # 直接返回原始数据字符串列表
            logger.info(f"成功获取股票 {stock_code} 的 {len(klines)} 条K线数据")
            return klines

        except NoDataFoundError:
            # 重新抛出NoDataFoundError
            raise
        except Exception as e:
            logger.error(f"获取K线数据失败: {e}")
            raise DataSourceError(f"获取K线数据失败: {e}")

    # ==================== 查询功能 ====================

    def get_stock_search(
        self,
        keyword: str
    ) -> Optional[List[Dict]]:
        """
        根据关键字搜索股票信息

        Args:
            keyword: 搜索关键字，可以是股票代码、股票名称等

        Returns:
            股票信息列表，每个元素是一个字典，包含股票的基本信息
            如：{'code': '300750', 'name': '宁德时代', 'pinyinString': 'ndsd', ...}
            如果没有找到匹配的股票，返回空列表

        Raises:
            DataSourceError: 当数据源出现错误时
        """
        # 检查searcher是否已初始化
        if self.searcher is None:
            logger.error("股票搜索器未初始化")
            raise DataSourceError("股票搜索器未初始化，请先调用initialize()方法")

        try:
            # 调用搜索器获取数据
            search_results = self.searcher.search(keyword)

            # 如果没有数据，返回空列表
            if not search_results:
                logger.info(f"未找到与关键字 '{keyword}' 匹配的股票")
                return []

            logger.info(f"成功搜索到 {len(search_results)} 只与 '{keyword}' 相关的股票")
            return search_results

        except Exception as e:
            logger.error(f"搜索股票失败: {e}")
            raise DataSourceError(f"搜索股票失败: {e}")

    def get_technical_indicators(
            self,
            stock_code: str,
            start_date: str,
            end_date: str,
            frequency: str = "d",
    ) -> List[Dict]:
        """
        获取技术指标数据（原始数据，不做格式化处理）

        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            frequency: K线周期，可选值: "d"(日), "w"(周), "m"(月), "5"(5分钟), "15"(15分钟), "30"(30分钟), "60"(60分钟)

        Returns:
            包含K线数据和技术指标的原始数据

        Raises:
            LoginError: If login to the data source fails.
            NoDataFoundError: If no data is found for the query.
            DataSourceError: For other data source related errors.
            ValueError: If input parameters are invalid.
        """
        # 检查kline_spider是否已初始化
        if self.kline_spider is None:
            logger.error("爬虫未初始化")
            raise DataSourceError("爬虫未初始化，请先调用initialize()方法")

        # 首先获取K线数据
        k_data = self.get_historical_k_data(stock_code, start_date, end_date, frequency)

        if not k_data:
            raise NoDataFoundError(f"未找到股票 {stock_code} 的K线数据，无法计算技术指标")

        # 直接返回原始K线数据，不进行技术指标计算
        logger.info(f"成功获取股票 {stock_code} 的 {len(k_data)} 条K线数据")
        return k_data

    def get_last_trading_day(self) -> Optional[Dict]:
        """
        获取最近交易日信息

        Returns:
            包含交易日信息的字典

        Raises:
            DataSourceError: 当数据源出现错误时
        """
        # 检查searcher是否已初始化
        if self.searcher is None:
            logger.error("股票搜索器未初始化")
            raise DataSourceError("股票搜索器未初始化，请先调用initialize()方法")

        try:
            # 调用搜索器获取最近交易日数据
            last_trading_day_data = self.searcher.last_trading_day()

            # 如果没有数据，返回None
            if not last_trading_day_data:
                logger.info("未获取到最近交易日信息")
                return None

            logger.info("成功获取最近交易日信息")
            return last_trading_day_data

        except Exception as e:
            logger.error(f"获取最近交易日信息失败: {e}")
            raise DataSourceError(f"获取最近交易日信息失败: {e}")
