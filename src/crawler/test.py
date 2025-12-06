from src.crawler.fundamental_data import FundamentalDataCrawler
crawler = FundamentalDataCrawler()

# 测试获取主营业务构成
r = crawler.get_main_business("688041.SH", "2025-06-30")
print("主营业务构成:")
print(r)


#  测试获取主营业务范围
# business_scope = crawler.get_business_scope("688041.SH")
# print("\n主营业务范围:")
# print(business_scope)
#
# # 测试获取经营评述
# data = crawler.get_business_review("688041.SH")
# # 提取BUSINESS_REVIEW内容
# business_review = data.get('BUSINESS_REVIEW', 'N/A')
# print("\n经营评述:")
# print(business_review)