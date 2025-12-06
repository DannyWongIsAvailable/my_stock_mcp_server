"""
估值数据工具
src/mcp_tools/valuation.py
提供估值数据查询和分析功能
"""
import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP
from ..data_source_interface import FinancialDataInterface
from ..utils.markdown_formatter import format_list_to_markdown_table

logger = logging.getLogger(__name__)


def register_valuation_tools(app: FastMCP, data_source: FinancialDataInterface):
    """
    注册估值分析工具到MCP应用
    
    Args:
        app: FastMCP应用实例
        data_source: 数据源接口实例
    """
    
    @app.tool()
    def get_valuation_analysis(stock_code: str, indicator_type: int = 1, date_type: int = 3) -> str:
        """
        获取估值分析数据

        获取指定股票的估值分析数据，包括当前值和历史分位数。

        Args:
            stock_code: 股票代码，包含交易所代码，如300059.SZ
            indicator_type: 指标类型
                          1 - 市盈率TTM
                          2 - 市净率MRQ
                          3 - 市销率TTM
                          4 - 市现率TTM
            date_type: 时间周期类型
                     1 - 1年
                     2 - 3年
                     3 - 5年
                     4 - 10年

        Returns:
            估值分析数据的Markdown表格

        Examples:
            - get_valuation_analysis("300059.SZ", 1, 3)
            - get_valuation_analysis("000001.SZ", 2, 2)
        """
        try:
            logger.info(f"获取估值分析数据: {stock_code}, 指标类型: {indicator_type}, 时间周期: {date_type}")

            # 获取估值分析数据
            raw_data = data_source.get_valuation_analysis(stock_code, indicator_type, date_type)
            
            # 检查是否有错误信息
            if raw_data is None:
                return f"未找到股票代码 '{stock_code}' 的估值分析数据"
            
            if "error" in raw_data:
                error_msg = raw_data["error"]
                return f"获取估值分析数据失败: {error_msg}"
            
            # 格式化为表格
            table_data = [{
                "股票代码": raw_data.get("SECUCODE", "N/A"),
                "交易日期": raw_data.get("TRADE_DATE", "N/A")[:10] if raw_data.get("TRADE_DATE") else "N/A",
                "指标类型": raw_data.get("INDICATOR_TYPE", "N/A"),
                "指标值": f"{raw_data.get('INDICATOR_VALUE', 'N/A'):.4f}" if raw_data.get('INDICATOR_VALUE') is not None else 'N/A',
                "统计周期": raw_data.get("STATISTICS_CYCLE", "N/A"),
                "30%分位数": f"{raw_data.get('PERCENTILE_THIRTY', 'N/A'):.4f}" if raw_data.get('PERCENTILE_THIRTY') is not None else 'N/A',
                "中位数(50%)": f"{raw_data.get('PERCENTILE_FIFTY', 'N/A'):.4f}" if raw_data.get('PERCENTILE_FIFTY') is not None else 'N/A',
                "70%分位数": f"{raw_data.get('PERCENTILE_SEVENTY', 'N/A'):.4f}" if raw_data.get('PERCENTILE_SEVENTY') is not None else 'N/A'
            }]
            
            result = "**估值分析数据**\n\n"
            result += format_list_to_markdown_table(table_data)
            
            return result

        except Exception as e:
            logger.error(f"工具执行出错: {e}")
            return f"执行失败: {str(e)}"

    logger.info("估值分析工具已注册")