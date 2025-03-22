#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据爬虫核心功能模块
此模块提供了从中国天气网爬取花粉数据的核心功能
"""

import requests
import json
import time
from datetime import datetime, timedelta

from .constants import CITIES

def get_pollen_data(city_info, start_date, end_date, config, retry_count=0):
    """
    获取指定城市的花粉数据
    
    参数:
    - city_info: 城市信息字典
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    - config: 配置字典
    - retry_count: 当前重试次数
    
    返回:
    - 花粉数据列表
    """
    url = f"https://graph.weatherdt.com/ty/pollen/v2/hfindex.html"
    params = {
        "eletype": 1,
        "city": city_info["en"],
        "start": start_date,
        "end": end_date,
        "predictFlag": "true"
    }
    
    # 更全面的请求头，模拟浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Referer": "https://www.weather.com.cn/forecast/hf_index.shtml?id=101010100",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Host": "graph.weatherdt.com"
    }
    
    try:
        response = requests.get(
            url, 
            params=params, 
            headers=headers, 
            timeout=config["REQUEST_TIMEOUT"]
        )
        
        # 响应内容不是标准的JSON格式，需要处理
        if response.status_code == 200:
            # 尝试直接解析为JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                # 如果失败，尝试手动解析文本
                text = response.text
                if text.startswith("(") and text.endswith(")"):
                    text = text[1:-1]  # 移除括号
                
                try:
                    data = json.loads(text)
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {str(e)}")
                    return []
            
            # 根据实际返回数据结构调整 - 使用'dataList'字段而非'data'
            if "dataList" in data:
                print(f"成功获取 {city_info['cn']} 的花粉数据，共 {len(data['dataList'])} 条记录")
                return data["dataList"]
            else:
                print(f"数据格式错误，缺少'dataList'字段")
                return []
        else:
            print(f"请求失败: {response.status_code}")
            
            # 如果请求失败并且未超过最大重试次数，则重试
            if retry_count < config["MAX_RETRIES"]:
                retry_count += 1
                print(f"正在进行第 {retry_count} 次重试...")
                time.sleep(config["REQUEST_DELAY"] * 2)  # 重试前等待更长时间
                return get_pollen_data(city_info, start_date, end_date, config, retry_count)
            
            return []
    except Exception as e:
        print(f"获取 {city_info['cn']} 的花粉数据时出错: {str(e)}")
        
        # 如果请求出错并且未超过最大重试次数，则重试
        if retry_count < config["MAX_RETRIES"]:
            retry_count += 1
            print(f"正在进行第 {retry_count} 次重试...")
            time.sleep(config["REQUEST_DELAY"] * 2)  # 重试前等待更长时间
            return get_pollen_data(city_info, start_date, end_date, config, retry_count)
            
        return []

def scrape_cities_data(cities_to_scrape, start_date, end_date, config):
    """
    爬取多个城市的花粉数据
    
    参数:
    - cities_to_scrape: 要爬取的城市列表
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    - config: 配置字典
    
    返回:
    - 所有城市的花粉数据列表
    - 成功爬取的城市列表
    - 爬取失败的城市列表
    """
    print(f"\n开始爬取花粉数据，日期范围: {start_date} 至 {end_date}")
    print(f"共需爬取 {len(cities_to_scrape)} 个城市的数据")
    
    # 存储所有数据的列表
    all_data = []
    
    # 记录成功和失败的城市
    successful_cities = []
    failed_cities = []
    
    # 遍历所有城市
    for i, city in enumerate(cities_to_scrape):
        city_name = city['cn']
        city_code = city['en']
        city_id = city['id']
        
        print(f"\n[{i+1}/{len(cities_to_scrape)}] 正在获取 {city_name} 的花粉数据...")
        city_data = get_pollen_data(city, start_date, end_date, config)
        
        if city_data:
            # 添加额外的城市信息
            for item in city_data:
                item["city_id"] = city_id  # 添加城市ID
                item["city_name"] = city_name  # 添加城市名称
                item["city_code"] = city_code  # 添加城市代码
            
            all_data.extend(city_data)
            successful_cities.append(city_name)
        else:
            failed_cities.append(city_name)
        
        # 添加延迟，避免请求频率过高
        if i < len(cities_to_scrape) - 1:  # 不需要在最后一个城市后等待
            print(f"等待 {config['REQUEST_DELAY']} 秒后继续...")
            time.sleep(config['REQUEST_DELAY'])
    
    # 打印爬取结果摘要
    print("\n爬取完成！")
    print(f"成功爬取 {len(successful_cities)}/{len(cities_to_scrape)} 个城市的数据")
    
    if failed_cities:
        print(f"以下城市爬取失败: {', '.join(failed_cities)}")
    
    if all_data:
        print(f"共获取 {len(all_data)} 条花粉数据记录")
    else:
        print("未获取到任何数据")
    
    return all_data, successful_cities, failed_cities

def filter_cities(cities_list, selected_cities):
    """
    根据配置筛选城市
    
    参数:
    - cities_list: 所有可用的城市列表
    - selected_cities: 要筛选的城市代码列表
    
    返回:
    - 筛选后的城市列表
    """
    if not selected_cities:
        return cities_list
    
    return [city for city in cities_list if city["en"] in selected_cities]

def get_city_name(city_code):
    """
    根据城市代码获取城市中文名
    
    参数:
    - city_code: 城市英文代码
    
    返回:
    - 城市中文名，如果找不到则返回None
    """
    for city in CITIES:
        if city["en"] == city_code:
            return city["cn"]
    return None

def get_city_by_name(city_name):
    """
    根据城市中文名获取城市信息
    
    参数:
    - city_name: 城市中文名
    
    返回:
    - 城市信息字典，如果找不到则返回None
    """
    for city in CITIES:
        if city["cn"] == city_name:
            return city
    return None 