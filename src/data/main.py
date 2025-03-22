#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据主模块
提供统一的API接口，用于从其他脚本中调用花粉数据功能
"""

from datetime import datetime, timedelta
import os
import pandas as pd

from .constants import CITIES, DEFAULT_CONFIG
from .crawler import filter_cities, scrape_cities_data, get_city_name, get_city_by_name
from .processor import process_pollen_data, save_data, create_sample_data, split_city_data

def get_pollen_data_for_cities(city_codes=None, days=30, start_date=None, end_date=None, config=None):
    """
    获取指定城市的花粉数据
    
    参数:
    - city_codes: 城市代码列表，如果为None则获取所有城市
    - days: 相对模式下，获取的天数
    - start_date: 固定日期模式下的开始日期 (YYYY-MM-DD)
    - end_date: 固定日期模式下的结束日期 (YYYY-MM-DD)
    - config: 配置字典，如果为None则使用默认配置
    
    返回:
    - 处理后的花粉数据DataFrame
    """
    # 使用默认配置，如果没有提供
    if config is None:
        config = DEFAULT_CONFIG.copy()
    
    # 更新配置
    if city_codes:
        config["SELECTED_CITIES"] = city_codes
    
    if days:
        config["DAYS_TO_FETCH"] = days
    
    if start_date and end_date:
        config["USE_RELATIVE_DATES"] = False
        config["START_DATE"] = start_date
        config["END_DATE"] = end_date
    
    # 获取日期范围
    if config["USE_RELATIVE_DATES"]:
        # 使用相对日期
        now = datetime.now()
        end_date = now.strftime("%Y-%m-%d")
        start_date = (now - timedelta(days=config["DAYS_TO_FETCH"])).strftime("%Y-%m-%d")
    else:
        # 使用固定日期
        start_date = config["START_DATE"]
        end_date = config["END_DATE"]
    
    # 筛选要爬取的城市
    cities_to_scrape = filter_cities(CITIES, config["SELECTED_CITIES"])
    
    # 爬取数据
    raw_data, successful_cities, failed_cities = scrape_cities_data(
        cities_to_scrape, start_date, end_date, config
    )
    
    # 处理数据
    df = process_pollen_data(raw_data)
    
    return df

def get_pollen_data_for_city(city_code, days=30, start_date=None, end_date=None, config=None):
    """
    获取单个城市的花粉数据
    
    参数:
    - city_code: 城市代码
    - days: 相对模式下，获取的天数
    - start_date: 固定日期模式下的开始日期 (YYYY-MM-DD)
    - end_date: 固定日期模式下的结束日期 (YYYY-MM-DD)
    - config: 配置字典，如果为None则使用默认配置
    
    返回:
    - 处理后的花粉数据DataFrame
    """
    return get_pollen_data_for_cities([city_code], days, start_date, end_date, config)

def save_pollen_data(df, filename=None, format="csv", encoding="utf-8-sig"):
    """
    保存花粉数据到文件
    
    参数:
    - df: 要保存的DataFrame
    - filename: 文件名，如果为None则使用默认格式
    - format: 文件格式，"csv"或"excel"
    - encoding: 文件编码，默认为"utf-8-sig"
    
    返回:
    - 保存的文件名
    """
    if df.empty:
        print("没有数据可保存")
        return None
    
    config = DEFAULT_CONFIG.copy()
    config["OUTPUT_FORMAT"] = format
    config["OUTPUT_ENCODING"] = encoding
    
    if filename:
        config["FILENAME_PREFIX"] = filename
        config["ADD_DATE_TO_FILENAME"] = False
    
    return save_data(df, config)

def get_sample_data(num_cities=5, num_days=30):
    """
    获取示例数据
    
    参数:
    - num_cities: 城市数量
    - num_days: 天数
    
    返回:
    - 示例数据DataFrame
    """
    return create_sample_data(num_cities, num_days)

def get_city_info(city_code_or_name):
    """
    获取城市信息
    
    参数:
    - city_code_or_name: 城市代码或城市名称
    
    返回:
    - 城市信息字典
    """
    # 首先尝试作为城市代码查找
    for city in CITIES:
        if city["en"] == city_code_or_name:
            return city
    
    # 然后尝试作为城市名称查找
    for city in CITIES:
        if city["cn"] == city_code_or_name:
            return city
    
    return None

def list_all_cities():
    """
    获取所有城市的列表
    
    返回:
    - 所有城市的DataFrame
    """
    return pd.DataFrame(CITIES) 