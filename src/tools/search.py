"""
股票搜索工具
src/tools/search.py
提供股票搜索和查询功能
"""
import logging
from mcp.server.fastmcp import FastMCP
from ..data_source_interface import FinancialDataInterface

logger = logging.getLogger(__name__)


def register_search_tools(app: FastMCP, data_source: FinancialDataInterface):
    """
    注册股票搜索相关工具

    Args:
        app: FastMCP应用实例
        data_source: 数据源实例
    """

    @app.tool()
    def get_stock_search(keyword: str) -> str:
        """
        搜索股票信息

        根据关键字搜索相关的股票信息。

        Args:
            keyword: 搜索关键字，可以是股票代码、股票名称等

        Returns:
            股票信息的Markdown表格

        Examples:
            - get_stock_search("宁德时代")
            - get_stock_search("300750")
            - get_stock_search("新能源")
        """
        try:
            logger.info(f"搜索股票: 关键字 '{keyword}'")

            # 从数据源获取原始搜索结果
            search_results = data_source.get_stock_search(keyword)

            if not search_results:
                return f"未找到与关键字 '{keyword}' 相关的股票信息"

            # 格式化数据
            formatted_data = []
            for stock in search_results:
                # 处理状态显示
                status = '正常' if stock.get('status', 0) == 10 else '异常'

                # 处理证券类型（可能是列表）
                security_types = stock.get('securityType', [])
                if isinstance(security_types, list):
                    security_type_str = ', '.join(map(str, security_types))
                else:
                    security_type_str = str(security_types)

                formatted_data.append({
                    '股票代码': stock.get('code', ''),
                    '股票名称': stock.get('shortName', ''),
                    '市场类型': stock.get('securityTypeName', ''),
                    '拼音': stock.get('pinyin', ''),
                    '内部代码': stock.get('innerCode', ''),
                    '市场编号': stock.get('market', ''),
                    '证券类型': security_type_str,
                    '小类类型': stock.get('smallType', ''),
                    '状态': status,
                    '标记': stock.get('flag', ''),
                    '扩展小类类型': stock.get('extSmallType', ''),
                })

            # 构建Markdown表格
            columns = [
                '股票代码', '股票名称', '市场类型', '拼音', '内部代码', '市场编号',
                '证券类型', '小类类型', '状态', '标记', '扩展小类类型'
            ]

            header = "| " + " | ".join(columns) + " |"
            separator = "| " + " | ".join(["---"] * len(columns)) + " |"

            rows = []
            for item in formatted_data:
                row_data = [str(item.get(col, "")) for col in columns]
                row = "| " + " | ".join(row_data) + " |"
                rows.append(row)

            table = "\n".join([header, separator] + rows)
            note = f"\n\n💡 找到 {len(formatted_data)} 只与 '{keyword}' 相关的股票"
            return f"## 股票搜索结果\n\n{table}{note}"

        except Exception as e:
            logger.error(f"搜索股票时出错: {e}")
            return f"搜索股票失败: {str(e)}"

    @app.tool()
    def get_last_trading_day() -> str:
        """
        获取最近交易日信息

        获取最新的交易日历信息，包括最近的交易日和休市日。

        Returns:
            最近交易日信息的Markdown表格

        Examples:
            - get_last_trading_day()
        """
        try:
            logger.info("获取最近交易日信息")

            # 从数据源获取最近交易日信息
            trading_data = data_source.get_last_trading_day()

            if not trading_data:
                return "未能获取到交易日信息"

            # 解包并格式化数据
            raw_data = trading_data.get("data", [])
            now_date = trading_data.get("nowdate", "")
            
            if not raw_data:
                return "交易日数据为空"

            # 格式化数据
            formatted_data = []
            for item in raw_data:
                # 处理交易状态显示
                trade_status = '交易日' if item.get('jybz', '0') == '1' else '休市'
                
                formatted_data.append({
                    '交易日序号': item.get('zrxh', ''),
                    '日期': item.get('jyrq', ''),
                    '状态': trade_status,
                })

            # 构建Markdown表格
            columns = ['交易日序号', '日期', '状态']
            header = "| " + " | ".join(columns) + " |"
            separator = "| " + " | ".join(["---"] * len(columns)) + " |"

            rows = []
            for item in formatted_data:
                row_data = [str(item.get(col, "")) for col in columns]
                row = "| " + " | ".join(row_data) + " |"
                rows.append(row)

            table = "\n".join([header, separator] + rows)
            note = f"\n\n📅 当前日期: {now_date}"
            return f"## 最近交易日信息\n\n{table}{note}"

        except Exception as e:
            logger.error(f"获取最近交易日信息时出错: {e}")
            return f"获取最近交易日信息失败: {str(e)}"
