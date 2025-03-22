#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据处理模块
此模块提供了花粉数据的处理、清洗和保存功能
"""

import os
import pandas as pd
from datetime import datetime, timedelta
import random

def process_pollen_data(raw_data):
    """
    处理原始花粉数据，转换为结构化数据
    
    参数:
    - raw_data: 原始花粉数据列表
    
    返回:
    - 处理后的DataFrame
    """
    if not raw_data:
        return pd.DataFrame()
    
    # 转换为DataFrame
    df = pd.DataFrame(raw_data)
    
    # 重命名列名
    if 'date' in df.columns:
        df.rename(columns={
            'date': '日期',
            'index': '花粉指数',
            'level': '花粉等级',
            'levelColor': '颜色代码',
            'levelMsg': '等级描述',
            'city_name': '城市',
            'city_id': '城市ID',
            'city_code': '城市代码'
        }, inplace=True)
    
    # 处理日期格式
    if '日期' in df.columns:
        df['日期'] = pd.to_datetime(df['日期'])
        df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')
    
    # 对数值列进行转换
    if '花粉指数' in df.columns:
        df['花粉指数'] = pd.to_numeric(df['花粉指数'], errors='coerce')
    
    # 如果存在预测标记，则添加一个新列
    if 'predictFlag' in df.columns:
        df['是否预测'] = df['predictFlag'].apply(lambda x: '是' if x == 1 else '否')
        df.drop('predictFlag', axis=1, inplace=True)
    
    # 选择需要的列
    columns_to_keep = ['日期', '城市', '花粉等级', '花粉指数', '等级描述', '颜色代码', 
                      '城市ID', '城市代码']
    columns_to_keep = [col for col in columns_to_keep if col in df.columns]
    
    return df[columns_to_keep]

def save_data(df, config, city_name=None):
    """
    保存数据到文件
    
    参数:
    - df: 要保存的DataFrame
    - config: 配置字典
    - city_name: 城市名称，如果指定，则只保存该城市的数据
    
    返回:
    - 保存的文件名
    """
    if df.empty:
        print("没有数据可保存")
        return None
    
    now = datetime.now().strftime("%Y-%m-%d")
    
    # 构建文件名
    if city_name:
        if config["ADD_DATE_TO_FILENAME"]:
            base_filename = f"{config['FILENAME_PREFIX']}_{city_name}_{now}"
        else:
            base_filename = f"{config['FILENAME_PREFIX']}_{city_name}"
    else:
        if config["ADD_DATE_TO_FILENAME"]:
            base_filename = f"{config['FILENAME_PREFIX']}_{now}"
        else:
            base_filename = config["FILENAME_PREFIX"]
    
    # 根据配置选择保存格式
    if config["OUTPUT_FORMAT"].lower() == "csv":
        filename = f"{base_filename}.csv"
        df.to_csv(filename, index=False, encoding=config["OUTPUT_ENCODING"])
    elif config["OUTPUT_FORMAT"].lower() == "excel":
        filename = f"{base_filename}.xlsx"
        df.to_excel(filename, index=False, engine="openpyxl")
    else:
        print(f"不支持的文件格式: {config['OUTPUT_FORMAT']}，将使用CSV格式")
        filename = f"{base_filename}.csv"
        df.to_csv(filename, index=False, encoding=config["OUTPUT_ENCODING"])
    
    print(f"\n成功将花粉数据保存到文件 {filename}")
    return filename

def create_sample_data(num_cities=5, num_days=30):
    """
    创建示例数据，用于测试和演示
    
    参数:
    - num_cities: 城市数量
    - num_days: 天数
    
    返回:
    - 示例数据DataFrame
    """
    from .constants import CITIES, POLLEN_LEVELS
    
    print(f"正在生成 {num_cities} 个城市 {num_days} 天的示例数据...")
    
    # 选择城市
    selected_cities = random.sample(CITIES, min(num_cities, len(CITIES)))
    
    # 生成日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=num_days-1)
    
    # 生成数据
    data = []
    for city in selected_cities:
        current_date = start_date
        while current_date <= end_date:
            # 随机选择花粉等级
            level_index = random.randint(0, len(POLLEN_LEVELS)-1)
            level_info = POLLEN_LEVELS[level_index]
            
            # 生成随机指数 (0-100)
            index_value = random.randint(0, 100)
            
            data.append({
                '日期': current_date.strftime("%Y-%m-%d"),
                '城市': city['cn'],
                '城市ID': city['id'],
                '城市代码': city['en'],
                '花粉等级': level_info['level'],
                '花粉指数': index_value,
                '等级描述': level_info['message'],
                '颜色代码': level_info['color']
            })
            
            current_date += timedelta(days=1)
    
    # 转换为DataFrame
    df = pd.DataFrame(data)
    
    print(f"已生成 {len(df)} 条示例数据记录")
    return df

def split_city_data(df, city_name):
    """
    从数据中提取指定城市的数据
    
    参数:
    - df: 包含所有城市数据的DataFrame
    - city_name: 要提取的城市名称
    
    返回:
    - 筛选后的DataFrame
    """
    if df.empty or '城市' not in df.columns:
        return pd.DataFrame()
    
    return df[df['城市'] == city_name] 