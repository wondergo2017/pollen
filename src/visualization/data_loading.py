#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据加载模块
此模块提供了加载和预处理花粉数据的功能
"""

import os
import pandas as pd
import datetime

def load_data(file_path):
    """
    加载花粉数据文件
    
    参数:
        file_path (str): 数据文件的路径
        
    返回:
        pandas.DataFrame: 加载的数据
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"数据文件不存在: {file_path}")
    
    try:
        # 尝试加载CSV文件
        df = pd.read_csv(file_path)
        
        # 检查是否包含必要的列
        required_columns = ['日期', '城市']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"数据文件缺少必要的列: {', '.join(missing_columns)}")
        
        # 处理日期列
        if '日期' in df.columns:
            # 确保日期列是datetime类型
            df['日期'] = pd.to_datetime(df['日期'])
        
        return df
        
    except Exception as e:
        raise Exception(f"加载数据文件时出错: {str(e)}")

def filter_data(df, cities=None, start_date=None, end_date=None):
    """
    根据城市和日期范围筛选数据
    
    参数:
        df (pandas.DataFrame): 原始数据框
        cities (list): 城市列表，如果为None则不筛选城市
        start_date (str or datetime): 开始日期，如果为None则不筛选开始日期
        end_date (str or datetime): 结束日期，如果为None则不筛选结束日期
        
    返回:
        pandas.DataFrame: 筛选后的数据
    """
    if df.empty:
        return df
    
    # 复制数据框以避免修改原始数据
    filtered_df = df.copy()
    
    # 筛选城市
    if cities and '城市' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['城市'].isin(cities)]
    
    # 筛选日期范围
    if '日期' in filtered_df.columns:
        # 确保日期列是datetime类型
        if not pd.api.types.is_datetime64_dtype(filtered_df['日期']):
            filtered_df['日期'] = pd.to_datetime(filtered_df['日期'])
        
        # 筛选开始日期
        if start_date:
            if isinstance(start_date, str):
                start_date = pd.to_datetime(start_date)
            filtered_df = filtered_df[filtered_df['日期'] >= start_date]
        
        # 筛选结束日期
        if end_date:
            if isinstance(end_date, str):
                end_date = pd.to_datetime(end_date)
            filtered_df = filtered_df[filtered_df['日期'] <= end_date]
    
    return filtered_df

def prepare_data_for_visualization(df):
    """
    准备用于可视化的数据
    
    参数:
        df (pandas.DataFrame): 原始数据框
        
    返回:
        pandas.DataFrame: 处理后的用于可视化的数据
    """
    if df.empty:
        return df
    
    # 复制数据框以避免修改原始数据
    viz_df = df.copy()
    
    # 确保日期列是datetime类型
    if '日期' in viz_df.columns and not pd.api.types.is_datetime64_dtype(viz_df['日期']):
        viz_df['日期'] = pd.to_datetime(viz_df['日期'])
    
    # 按日期排序
    if '日期' in viz_df.columns:
        viz_df = viz_df.sort_values('日期')
    
    # 填充可能的缺失值
    if '花粉指数' in viz_df.columns:
        viz_df['花粉指数'] = viz_df['花粉指数'].fillna(0).astype(float)
    
    # 确保城市列是字符串类型
    if '城市' in viz_df.columns:
        viz_df['城市'] = viz_df['城市'].astype(str)
    
    return viz_df 