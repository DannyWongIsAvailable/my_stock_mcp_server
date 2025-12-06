from src.crawler.valuation_data import ValuationDataCrawler

# 测试估值分析数据
valuation_crawler = ValuationDataCrawler()

# 测试默认参数（市盈率TTM，5年周期）
print("测试默认参数（市盈率TTM，5年周期）:")
valuation_data = valuation_crawler.get_valuation_analysis("688041.SH")
print(valuation_data)

# 测试市净率MRQ，3年周期
print("\n测试市净率MRQ，3年周期:")
pb_data = valuation_crawler.get_valuation_analysis(
    "688041.SH", 
    ValuationDataCrawler.INDICATOR_TYPE_PB_MRQ, 
    ValuationDataCrawler.DATE_TYPE_3YEAR
)
print(pb_data)

# 测试市销率TTM，10年周期
print("\n测试市销率TTM，10年周期:")
ps_data = valuation_crawler.get_valuation_analysis(
    "688041.SH", 
    ValuationDataCrawler.INDICATOR_TYPE_PS_TTM, 
    ValuationDataCrawler.DATE_TYPE_10YEAR
)
print(ps_data)