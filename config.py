#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据爬虫配置文件
可以根据需要修改以下配置参数
"""

# 爬取数据的日期范围

# 方法1：基于当前日期的相对时间范围
# 设置为True表示使用相对时间范围，False表示使用固定日期范围
USE_RELATIVE_DATES = True
# 爬取过去多少天的数据
DAYS_TO_FETCH = 30

# 方法2：固定日期范围（如果USE_RELATIVE_DATES=False）
# 格式为"YYYY-MM-DD"
START_DATE = "2023-03-01"
END_DATE = "2023-05-31"

# 爬虫行为设置
# 请求间隔时间（秒），避免过快请求被限制
REQUEST_DELAY = 2
# 请求超时时间（秒）
REQUEST_TIMEOUT = 10
# 最大重试次数
MAX_RETRIES = 3

# 输出设置
# 数据保存格式，支持"csv"和"excel"
OUTPUT_FORMAT = "csv"
# 是否自动在文件名中添加日期
ADD_DATE_TO_FILENAME = True
# 自定义文件名前缀
FILENAME_PREFIX = "pollen_data"
# 输出编码
OUTPUT_ENCODING = "utf-8-sig"  # 使用带BOM的UTF-8，Excel可以正确识别中文

# 是否只抓取指定城市
# 设置为空列表表示抓取所有城市
SELECTED_CITIES = []
# 例如，只抓取北京和上海：
# SELECTED_CITIES = ["beijing", "shanghai"] 