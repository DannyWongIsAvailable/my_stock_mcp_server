"""
网络爬虫数据源实现

基于网络爬虫的数据源实现
"""

import logging
from typing import List, Optional, Dict
from .data_source_interface import FinancialDataSource, DataSourceError, NoDataFoundError, LoginError

logger = logging.getLogger(__name__)


class WebCrawlerDataSource(FinancialDataSource):
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
        获取K线数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            frequency: K线周期，可选值: "d"(日), "w"(周), "m"(月), "5"(5分钟), "15"(15分钟), "30"(30分钟), "60"(60分钟)
            
        Returns:
            K线数据列表，每个元素是一个字典，包含以下字段：
            date, open, close, high, low, volume, amount, amplitude, change_percent, change_amount, turnover_rate
            
        Raises:
            LoginError: If login to the data source fails.
            NoDataFoundError: If no data is found for the query.
            CrawlerDataSourceError: For other data source related errors.
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
            
            # 解析klines数据
            result = []
            for kline in klines:
                fields = kline.split(",")
                if len(fields) >= 11:
                    result.append({
                        "date": fields[0],           # 日期
                        "open": float(fields[1]),    # 开盘
                        "close": float(fields[2]),   # 收盘
                        "high": float(fields[3]),    # 最高
                        "low": float(fields[4]),     # 最低
                        "volume": int(fields[5]),    # 成交量
                        "amount": float(fields[6]),  # 成交额
                        "amplitude": float(fields[7]), # 振幅
                        "change_percent": float(fields[8]), # 涨跌幅
                        "change_amount": float(fields[9]),  # 涨跌额
                        "turnover_rate": float(fields[10])  # 换手率
                    })

            
            logger.info(f"成功获取股票 {stock_code} 的 {len(result)} 条K线数据")
            return result
            
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
        获取技术指标数据

        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            frequency: K线周期，可选值: "d"(日), "w"(周), "m"(月), "5"(5分钟), "15"(15分钟), "30"(30分钟), "60"(60分钟)

        Returns:
            技术指标数据列表，每个元素是一个字典，包含以下字段：
            date, ma5, ma10, ma20, ma60, macd, macd_signal, macd_hist, rsi6, rsi12, rsi24, kdj_k, kdj_d, kdj_j

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

        # 提取收盘价、最高价、最低价用于计算
        closes = [item['close'] for item in k_data]
        highs = [item['high'] for item in k_data]
        lows = [item['low'] for item in k_data]

        try:
            # 计算各种技术指标
            ma5 = self._calculate_ma(closes, 5)
            ma10 = self._calculate_ma(closes, 10)
            ma20 = self._calculate_ma(closes, 20)
            ma60 = self._calculate_ma(closes, 60)

            macd_data = self._calculate_macd(closes)
            rsi_data = self._calculate_rsi(closes)
            kdj_data = self._calculate_kdj(highs, lows, closes)

            # 组合结果
            result = []
            for i, item in enumerate(k_data):
                result.append({
                    "date": item['date'],
                    "ma5": ma5[i] if ma5[i] is not None else None,
                    "ma10": ma10[i] if ma10[i] is not None else None,
                    "ma20": ma20[i] if ma20[i] is not None else None,
                    "ma60": ma60[i] if ma60[i] is not None else None,
                    "macd_dif": macd_data['DIF'][i] if macd_data['DIF'][i] is not None else None,
                    "macd_dea": macd_data['DEA'][i] if macd_data['DEA'][i] is not None else None,
                    "macd_bar": macd_data['MACD'][i] if macd_data['MACD'][i] is not None else None,
                    "rsi6": rsi_data['rsi6'][i] if rsi_data['rsi6'][i] is not None else None,
                    "rsi12": rsi_data['rsi12'][i] if rsi_data['rsi12'][i] is not None else None,
                    "rsi24": rsi_data['rsi24'][i] if rsi_data['rsi24'][i] is not None else None,
                    "kdj_k": kdj_data['k'][i] if kdj_data['k'][i] is not None else None,
                    "kdj_d": kdj_data['d'][i] if kdj_data['d'][i] is not None else None,
                    "kdj_j": kdj_data['j'][i] if kdj_data['j'][i] is not None else None,
                })

            logger.info(f"成功计算股票 {stock_code} 的 {len(result)} 条技术指标数据")
            return result

        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            raise DataSourceError(f"计算技术指标失败: {e}")


    def _calculate_ma(self, data: List[float], period: int) -> List[Optional[float]]:
        """
        计算移动平均线（MA）

        Args:
            data: 价格数据列表
            period: 周期

        Returns:
            MA值列表
        """
        result = []
        for i in range(len(data)):
            if i < period - 1:
                result.append(None)
            else:
                ma_value = sum(data[i - period + 1:i + 1]) / period
                result.append(round(ma_value, 2))
        return result

    def _calculate_macd(
            self,
            closes: List[float],
            fast: int = 12,
            slow: int = 26,
            dea_period: int = 9
    ) -> Dict[str, List[Optional[float]]]:
        """
        计算 MACD 指标（DIF / DEA / MACD 柱）

        标准参数：fast=12, slow=26, dea_period=9
        约定：
            DIF = EMA(fast) - EMA(slow)
            DEA = DIF 的 dea_period 期 EMA
            MACD = 2 * (DIF - DEA)   # 即柱状图

        Args:
            closes: 收盘价列表
            fast: 快速 EMA 周期（默认 12）
            slow: 慢速 EMA 周期（默认 26）
            dea_period: DEA 平滑周期（默认 9）

        Returns:
            {
                "DIF": [...],
                "DEA": [...],
                "MACD": [...],   # 柱状图
            }
            每个列表长度与 closes 相同，前期数据不足时为 None
        """
        length = len(closes)
        if length == 0:
            return {
                "DIF": [],
                "DEA": [],
                "MACD": [],
            }

        # 1. 计算快、慢 EMA
        ema_fast = self._calculate_ema(closes, fast)
        ema_slow = self._calculate_ema(closes, slow)

        # 2. 计算 DIF = EMA_fast - EMA_slow
        dif: List[Optional[float]] = []
        for i in range(length):
            if ema_fast[i] is not None and ema_slow[i] is not None:
                dif_value = ema_fast[i] - ema_slow[i]
                dif.append(dif_value)
            else:
                dif.append(None)

        # 3. 计算 DEA = DIF 的 dea_period 期 EMA
        dea: List[Optional[float]] = self._calculate_ema(dif, dea_period)

        # 4. 计算 MACD 柱状图 = 2 * (DIF - DEA)
        macd_bar: List[Optional[float]] = []
        for i in range(length):
            if dif[i] is not None and dea[i] is not None:
                # A 股常用写法：MACD = 2 * (DIF - DEA)
                macd_value = 2 * (dif[i] - dea[i])
                macd_bar.append(round(macd_value, 2))
            else:
                macd_bar.append(None)

        # 5. 对 DIF / DEA 保留两位小数
        dif_rounded: List[Optional[float]] = [
            round(x, 2) if x is not None else None for x in dif
        ]
        dea_rounded: List[Optional[float]] = [
            round(x, 2) if x is not None else None for x in dea
        ]

        return {
            "DIF": dif_rounded,
            "DEA": dea_rounded,
            "MACD": macd_bar,  # 柱状图
        }

    def _calculate_ema(self, data: List[Optional[float]], period: int) -> List[Optional[float]]:
        """
        计算指数移动平均线（EMA）

        Args:
            data: 数据列表
            period: 周期

        Returns:
            EMA值列表
        """
        result = []
        multiplier = 2 / (period + 1)

        # 找到第一个非None值作为初始EMA
        ema = None
        start_idx = 0
        for i, value in enumerate(data):
            if value is not None:
                ema = value
                start_idx = i
                break

        # 填充前面的None
        for i in range(start_idx):
            result.append(None)

        result.append(ema)

        # 计算EMA
        for i in range(start_idx + 1, len(data)):
            if data[i] is not None:
                ema = (data[i] - ema) * multiplier + ema
                result.append(ema)
            else:
                result.append(None)

        return result

    def _calculate_rsi(self, closes: List[float], periods: List[int] = [6, 12, 24]) -> Dict:
        """
        计算RSI指标（Wilder 平滑版本）
        该实现方式与大多数行情软件的 RSI 计算方法保持一致

        Args:
            closes: 收盘价列表
            periods: RSI周期列表，默认[6, 12, 24]

        Returns:
            包含 rsi6、rsi12、rsi24 等字段的字典
        """
        result: Dict[str, List[Optional[float]]] = {}

        n = len(closes)
        if n == 0:
            # 没有数据直接返回空结果
            for period in periods:
                result[f"rsi{period}"] = []
            return result

        # 1. 预先计算每天的涨跌额 change，以及对应的涨幅 gain、跌幅 loss
        #    change[i] = closes[i] - closes[i-1]
        #    gain[i]   = max(change[i], 0)
        #    loss[i]   = max(-change[i], 0)
        changes: List[float] = [0.0] * n
        gains: List[float] = [0.0] * n
        losses: List[float] = [0.0] * n

        for i in range(1, n):
            change = closes[i] - closes[i - 1]
            changes[i] = change
            if change > 0:
                gains[i] = change
                losses[i] = 0.0
            else:
                gains[i] = 0.0
                losses[i] = -change  # 跌幅取正值

        # 2. 对每一个 RSI 周期分别计算
        for period in periods:
            rsi_values: List[Optional[float]] = [None] * n  # 与收盘价长度一致

            if period <= 0 or n <= period:
                # 数据长度不够一个周期，或者周期非法，全部为 None
                result[f"rsi{period}"] = rsi_values
                continue

            # 2.1 先计算第一个平均涨幅 / 跌幅（使用前 period 天的简单平均）
            #     注意：第 0 天没有变化，从第 1 天到第 period 天一共 period 天的变化
            sum_gain = sum(gains[1:period + 1])  # 索引 1 ~ period
            sum_loss = sum(losses[1:period + 1])

            avg_gain = sum_gain / period
            avg_loss = sum_loss / period

            # 2.2 在第 period 位置算出第一个 RSI
            #     对应 K 线索引为 period
            if avg_loss == 0:
                rsi_values[period] = 100.0  # 没有下跌，RSI 视为 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                rsi_values[period] = round(rsi, 2)

            # 2.3 后续位置使用 Wilder 平滑公式递推
            #     avg_gain_today = (avg_gain_yesterday * (period - 1) + gain_today) / period
            #     avg_loss_today = (avg_loss_yesterday * (period - 1) + loss_today) / period
            for i in range(period + 1, n):
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period

                if avg_loss == 0:
                    rsi_values[i] = 100.0
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                    rsi_values[i] = round(rsi, 2)

            # 前 period 天（索引 < period）的 RSI 没法计算，保持 None
            result[f"rsi{period}"] = rsi_values

        return result

    def _calculate_kdj(self, highs: List[float], lows: List[float], closes: List[float],
                       period: int = 9, k_period: int = 3, d_period: int = 3) -> Dict:
        """
        计算KDJ指标

        Args:
            highs: 最高价列表
            lows: 最低价列表
            closes: 收盘价列表
            period: RSV周期，默认9
            k_period: K值平滑周期，默认3
            d_period: D值平滑周期，默认3

        Returns:
            包含k、d、j的字典
        """
        rsv_list = []

        # 计算RSV
        for i in range(len(closes)):
            if i < period - 1:
                rsv_list.append(None)
            else:
                period_high = max(highs[i - period + 1:i + 1])
                period_low = min(lows[i - period + 1:i + 1])

                if period_high == period_low:
                    rsv = 50  # 避免除零
                else:
                    rsv = (closes[i] - period_low) / (period_high - period_low) * 100

                rsv_list.append(rsv)

        # 计算K值
        k_values = []
        k = 50  # K初始值
        for rsv in rsv_list:
            if rsv is None:
                k_values.append(None)
            else:
                k = (k * (k_period - 1) + rsv) / k_period
                k_values.append(round(k, 2))

        # 计算D值
        d_values = []
        d = 50  # D初始值
        for i, k_val in enumerate(k_values):
            if k_val is None:
                d_values.append(None)
            else:
                d = (d * (d_period - 1) + k_val) / d_period
                d_values.append(round(d, 2))

        # 计算J值
        j_values = []
        for i in range(len(k_values)):
            if k_values[i] is None or d_values[i] is None:
                j_values.append(None)
            else:
                j = 3 * k_values[i] - 2 * d_values[i]
                j_values.append(round(j, 2))

        return {
            'k': k_values,
            'd': d_values,
            'j': j_values
        }