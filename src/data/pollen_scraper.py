#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import sys

# 导入配置文件
try:
    import config
except ImportError:
    print("未找到配置文件 config.py，将使用默认配置")
    # 默认配置
    class config:
        USE_RELATIVE_DATES = True
        DAYS_TO_FETCH = 30
        START_DATE = "2023-03-01"
        END_DATE = "2023-05-31"
        REQUEST_DELAY = 2
        REQUEST_TIMEOUT = 10
        MAX_RETRIES = 3
        OUTPUT_FORMAT = "csv"
        ADD_DATE_TO_FILENAME = True
        FILENAME_PREFIX = "pollen_data"
        OUTPUT_ENCODING = "utf-8-sig"
        SELECTED_CITIES = []

# 城市列表，从JavaScript文件中提取
CITIES = [
    {"en": "beijing", "cn": "北京", "id": 101010100},
    {"en": "yinchuan", "cn": "银川", "id": 101170101},
    {"en": "lanzhou", "cn": "兰州", "id": 101160101},
    {"en": "changchun", "cn": "长春", "id": 101060101},
    {"en": "xian", "cn": "西安", "id": 101110101},
    {"en": "taiyuan", "cn": "太原", "id": 101100101},
    {"en": "shenyang", "cn": "沈阳", "id": 101070101},
    {"en": "wulumuqi", "cn": "乌鲁木齐", "id": 101130101},
    {"en": "huhehaote", "cn": "呼和浩特", "id": 101080101},
    {"en": "liaocheng", "cn": "聊城", "id": 101121701},
    {"en": "zibo", "cn": "淄博", "id": 101120301},
    {"en": "chengde", "cn": "承德", "id": 101090402},
    {"en": "baotou", "cn": "包头", "id": 101080201},
    {"en": "eerduosi", "cn": "鄂尔多斯", "id": 101080701},
    {"en": "haerbin", "cn": "哈尔滨", "id": 101050101},
    {"en": "wulanhaote", "cn": "乌兰浩特", "id": 101081101},
    {"en": "haikou", "cn": "海口", "id": 101310101},
    {"en": "tianjin", "cn": "天津", "id": 101030100},
    {"en": "xining", "cn": "西宁", "id": 101150101},
    {"en": "cangzhou", "cn": "沧州", "id": 101090701},
    {"en": "chongqing", "cn": "重庆", "id": 101040100},
    {"en": "wuhan", "cn": "武汉", "id": 101200101},
    {"en": "shijiazhuang", "cn": "石家庄", "id": 101090101},
    {"en": "kunming", "cn": "昆明市", "id": 101290101},
    {"en": "botou", "cn": "泊头", "id": 101090711},
    {"en": "dalian", "cn": "大连", "id": 101070201},
    {"en": "jinan", "cn": "济南", "id": 101120101},
    {"en": "hangzhou", "cn": "杭州", "id": 101210101},
    {"en": "wuhai", "cn": "乌海市", "id": 101080301},
    {"en": "yantai", "cn": "烟台", "id": 101120501},
    {"en": "guangzhou", "cn": "广州", "id": 101280101},
    {"en": "baoding", "cn": "保定", "id": 101090201},
    {"en": "yangzhou", "cn": "扬州", "id": 101190601},
    {"en": "nanchong", "cn": "南充", "id": 101270501},
    {"en": "wuxi", "cn": "无锡", "id": 101190201},
    {"en": "fuzhou", "cn": "福州", "id": 101230101},
    {"en": "hefei", "cn": "合肥", "id": 101220101},
    {"en": "nanning", "cn": "南宁", "id": 101300101},
    {"en": "lasa", "cn": "拉萨", "id": 101140101},
    {"en": "guiyang", "cn": "贵阳", "id": 101260101},
    {"en": "nanchang", "cn": "南昌", "id": 101240101},
    {"en": "changsha", "cn": "长沙", "id": 101250101},
    {"en": "yanan", "cn": "延安", "id": 101110300},
    {"en": "liupanshui", "cn": "六盘水", "id": 101260803},
    {"en": "xianyang", "cn": "咸阳", "id": 101110200},
    {"en": "chengdu", "cn": "成都", "id": 101270101},
    {"en": "shanghai", "cn": "上海", "id": 101020100},
    {"en": "yulin", "cn": "榆林", "id": 101110401},
    {"en": "zhengzhou", "cn": "郑州", "id": 101180101}
]

def get_pollen_data(city_info, start_date, end_date, retry_count=0):
    """
    获取指定城市的花粉数据
    
    参数:
    - city_info: 城市信息字典
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
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
            timeout=config.REQUEST_TIMEOUT
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
            if retry_count < config.MAX_RETRIES:
                retry_count += 1
                print(f"正在进行第 {retry_count} 次重试...")
                time.sleep(config.REQUEST_DELAY * 2)  # 重试前等待更长时间
                return get_pollen_data(city_info, start_date, end_date, retry_count)
            
            return []
    except Exception as e:
        print(f"获取 {city_info['cn']} 的花粉数据时出错: {str(e)}")
        
        # 如果请求出错并且未超过最大重试次数，则重试
        if retry_count < config.MAX_RETRIES:
            retry_count += 1
            print(f"正在进行第 {retry_count} 次重试...")
            time.sleep(config.REQUEST_DELAY * 2)  # 重试前等待更长时间
            return get_pollen_data(city_info, start_date, end_date, retry_count)
            
        return []

def save_data(df, format_type, filename_prefix):
    """保存数据到文件"""
    now = datetime.now().strftime("%Y-%m-%d")
    
    if config.ADD_DATE_TO_FILENAME:
        base_filename = f"{filename_prefix}_{now}"
    else:
        base_filename = filename_prefix
    
    if format_type.lower() == "csv":
        filename = f"{base_filename}.csv"
        df.to_csv(filename, index=False, encoding=config.OUTPUT_ENCODING)
    elif format_type.lower() == "excel":
        filename = f"{base_filename}.xlsx"
        df.to_excel(filename, index=False, engine="openpyxl")
    else:
        print(f"不支持的文件格式: {format_type}，将使用CSV格式")
        filename = f"{base_filename}.csv"
        df.to_csv(filename, index=False, encoding=config.OUTPUT_ENCODING)
    
    print(f"\n成功将花粉数据保存到文件 {filename}")
    return filename

def filter_cities(cities_list, selected_cities):
    """根据配置文件筛选城市"""
    if not selected_cities:
        return cities_list
    
    return [city for city in cities_list if city["en"] in selected_cities]

def main():
    """主函数，爬取所有城市的花粉数据"""
    
    # 获取日期范围
    if config.USE_RELATIVE_DATES:
        # 使用相对日期
        now = datetime.now()
        end_date = now.strftime("%Y-%m-%d")
        start_date = (now - timedelta(days=config.DAYS_TO_FETCH)).strftime("%Y-%m-%d")
    else:
        # 使用固定日期
        start_date = config.START_DATE
        end_date = config.END_DATE
    
    print(f"开始爬取花粉数据，日期范围: {start_date} 至 {end_date}")
    
    # 筛选要爬取的城市
    cities_to_scrape = filter_cities(CITIES, config.SELECTED_CITIES)
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
        city_data = get_pollen_data(city, start_date, end_date)
        
        if city_data:
            # 添加额外的城市信息
            for item in city_data:
                item["city_id"] = city_id  # 添加城市ID
            
            all_data.extend(city_data)
            successful_cities.append(city_name)
        else:
            failed_cities.append(city_name)
        
        # 添加延迟，避免请求频率过高
        if i < len(cities_to_scrape) - 1:  # 不需要在最后一个城市后等待
            print(f"等待 {config.REQUEST_DELAY} 秒后继续...")
            time.sleep(config.REQUEST_DELAY)
    
    if all_data:
        # 转换为DataFrame
        df = pd.DataFrame(all_data)
        
        # 调整列的顺序，使重要信息排在前面
        columns_order = [
            'city', 'city_id', 'cityCode', 'addTime', 'week', 
            'level', 'levelCode', 'color', 'elenum', 'levelMsg',
            'eletype', 'uploadUserName', 'createDate'
        ]
        
        # 只保留存在的列
        columns_order = [col for col in columns_order if col in df.columns]
        df = df[columns_order]
        
        # 保存数据
        save_data(df, config.OUTPUT_FORMAT, config.FILENAME_PREFIX)
        
        # 打印数据统计
        print(f"共获取了 {len(all_data)} 条数据，包含 {len(set(df['city']))} 个城市")
        
        # 打印花粉等级分布
        level_count = df["level"].value_counts()
        print("\n花粉等级分布:")
        for level, count in level_count.items():
            print(f"{level}: {count}条")
        
        # 打印成功和失败的城市
        print(f"\n成功获取数据的城市 ({len(successful_cities)}): {', '.join(successful_cities)}")
        if failed_cities:
            print(f"获取数据失败的城市 ({len(failed_cities)}): {', '.join(failed_cities)}")
    else:
        print("未获取到任何花粉数据")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n爬虫已被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        sys.exit(1) 