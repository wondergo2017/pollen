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
        print("警告：未获取到任何原始数据！")
        return pd.DataFrame()
    
    print(f"处理{len(raw_data)}条原始数据记录...")
    
    # 转换为DataFrame
    df = pd.DataFrame(raw_data)
    
    print(f"原始数据列: {list(df.columns)}")
    
    # 创建一个干净的DataFrame用于存储处理后的数据
    processed_df = pd.DataFrame()
    
    # 处理日期列
    if 'addTime' in df.columns:
        processed_df['日期'] = pd.to_datetime(df['addTime']).dt.strftime('%Y-%m-%d')
    elif 'date' in df.columns:
        processed_df['日期'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    else:
        print("警告: 未找到日期列！尝试其他可能的日期字段")
        date_fields = ['time', 'dateTime', 'createDate']
        for field in date_fields:
            if field in df.columns:
                print(f"找到可能的日期字段: {field}")
                processed_df['日期'] = pd.to_datetime(df[field]).dt.strftime('%Y-%m-%d')
                break
        
        if '日期' not in processed_df.columns:
            print("错误: 无法找到有效的日期列")
            return pd.DataFrame()
    
    # 处理城市列
    if 'city' in df.columns:
        processed_df['城市'] = df['city'].astype(str)
    elif 'city_name' in df.columns:
        processed_df['城市'] = df['city_name'].astype(str)
    else:
        print("警告: 未找到城市列！")
        processed_df['城市'] = None
    
    # 确保城市列有正确的值
    # 如果缺失，则使用city_code或city_id对应的城市名称
    if 'city_code' in df.columns and any(pd.isna(processed_df['城市']) | (processed_df['城市'] == "")):
        for i, row in processed_df.iterrows():
            if pd.isna(row['城市']) or row['城市'] == "":
                city_code = df.loc[i, 'city_code']
                # 从raw_data中查找此city_code对应的其他记录的city值
                matching_rows = df[df['city_code'] == city_code]
                if not matching_rows.empty and 'city_name' in matching_rows.columns:
                    city_name = matching_rows['city_name'].iloc[0]
                    if not pd.isna(city_name) and city_name != "":
                        processed_df.loc[i, '城市'] = city_name
                else:
                    # 使用固定的映射关系
                    from .constants import CITIES
                    for city in CITIES:
                        if city['en'] == city_code:
                            processed_df.loc[i, '城市'] = city['cn']
                            break
    
    # 处理花粉等级
    if 'level' in df.columns:
        processed_df['花粉等级'] = df['level']
    else:
        print("警告: 未找到花粉等级列！")
        processed_df['花粉等级'] = None
    
    # 处理其他列
    if 'levelMsg' in df.columns:
        processed_df['等级描述'] = df['levelMsg']
    
    if 'color' in df.columns:
        processed_df['颜色代码'] = df['color']
    elif 'levelColor' in df.columns:
        processed_df['颜色代码'] = df['levelColor']
    
    if 'index' in df.columns:
        processed_df['花粉指数'] = pd.to_numeric(df['index'], errors='coerce')
    
    if 'city_id' in df.columns:
        processed_df['城市ID'] = df['city_id']
    
    if 'cityCode' in df.columns:
        processed_df['城市代码'] = df['cityCode']
    elif 'city_code' in df.columns:
        processed_df['城市代码'] = df['city_code']
    
    # 确保没有NaN值的城市列
    processed_df['城市'] = processed_df['城市'].fillna("")
    processed_df = processed_df[processed_df['城市'] != "nan"]
    processed_df = processed_df[processed_df['城市'] != "None"]
    
    # 最后检查城市列，对于空值使用城市代码映射
    for i, row in processed_df.iterrows():
        if row['城市'] == "":
            if '城市代码' in processed_df.columns and not pd.isna(row['城市代码']):
                city_code = row['城市代码']
                # 使用常量中的映射关系
                from .constants import CITIES
                for city in CITIES:
                    if city['en'] == city_code:
                        processed_df.loc[i, '城市'] = city['cn']
                        break
    
    # 确保必需的列存在
    required_columns = ['日期', '城市', '花粉等级']
    for col in required_columns:
        if col not in processed_df.columns:
            print(f"错误: 缺少必需的列 '{col}'")
            return pd.DataFrame()
    
    print(f"处理后的列: {list(processed_df.columns)}")
    print(f"最终处理结果: {len(processed_df)}条记录")
    
    return processed_df

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
    
    print(f"准备保存数据: {len(df)}条记录")
    if city_name:
        print(f"保存城市: {city_name}的数据")
    
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
    
    # 确保数据目录存在
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # 根据配置选择保存格式
    if config["OUTPUT_FORMAT"].lower() == "csv":
        filename = os.path.join(data_dir, f"{base_filename}.csv")
        print(f"保存CSV文件: {filename}")
        df.to_csv(filename, index=False, encoding=config["OUTPUT_ENCODING"])
    elif config["OUTPUT_FORMAT"].lower() == "excel":
        filename = os.path.join(data_dir, f"{base_filename}.xlsx")
        print(f"保存Excel文件: {filename}")
        df.to_excel(filename, index=False, engine="openpyxl")
    else:
        print(f"不支持的文件格式: {config['OUTPUT_FORMAT']}，将使用CSV格式")
        filename = os.path.join(data_dir, f"{base_filename}.csv")
        print(f"保存CSV文件(默认): {filename}")
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