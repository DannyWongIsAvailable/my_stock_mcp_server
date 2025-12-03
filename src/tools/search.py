"""
股票搜索工具

提供股票搜索和查询功能
"""
import logging
from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.utils import format_number

logger = logging.getLogger(__name__)


def register_search_tools(app: FastMCP, data_source: FinancialDataSource):
    """
    注册股票搜索相关工具

    Args:
        app: FastMCP应用实例
        data_source: 数据源实例
    """

    @app.tool()
    def get_stock_search(
        keyword: str
    ) -> str:
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
            search_results = data_source.get_stock_search(keyword)

            if not search_results:
                return f"未找到与关键字 '{keyword}' 相关的股票信息"

            # 格式化数据
            formatted_data = []
            for stock in search_results:
                formatted_data.append({
                    '股票代码': stock.get('code', ''),
                    '股票名称': stock.get('shortName', ''),
                    '市场类型': stock.get('securityTypeName', ''),
                    '拼音': stock.get('pinyin', ''),
                    '内部代码': stock.get('innerCode', ''),
                    '市场编号': stock.get('market', ''),
                    '证券类型': ', '.join(map(str, stock.get('securityType', []))),
                    '小类类型': stock.get('smallType', ''),
                    '状态': '正常' if stock.get('status', 0) == 10 else '异常',
                    '标记': stock.get('flag', ''),
                    '扩展小类类型': stock.get('extSmallType', ''),
                })

            # 手动构建Markdown表格
            columns = ['股票代码', '股票名称', '市场类型', '拼音', '内部代码', '市场编号',
                       '证券类型', '小类类型', '状态', '标记', '扩展小类类型']

            # 创建表头
            header = "| " + " | ".join(columns) + " |"
            separator = "| " + " | ".join(["---"] * len(columns)) + " |"

            # 创建数据行
            rows = []
            for item in formatted_data:
                row_data = [str(item.get(col, "")) for col in columns]
                row = "| " + " | ".join(row_data) + " |"
                rows.append(row)

            # 组合表格
            table = "\n".join([header, separator] + rows)

            note = f"\n\n💡 找到 {len(formatted_data)} 只与 '{keyword}' 相关的股票"
            return f"## 股票搜索结果\n\n{table}{note}"

        except Exception as e:
            logger.error(f"搜索股票时出错: {e}")
            return f"搜索股票失败: {str(e)}"