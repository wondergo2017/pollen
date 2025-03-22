#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉可视化主模块
此模块整合了所有花粉可视化功能，提供统一的API接口
"""

import os
import pandas as pd
import warnings

# 抑制所有与字体相关的警告
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib.font_manager")
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib.backends")
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib.text")

from .data_loading import load_data, filter_data, prepare_data_for_visualization
from .trend_visualization import visualize_pollen_trends
from .distribution_visualization import visualize_pollen_distribution
from .utils import find_data_files, display_available_data_files, ensure_output_dir

from ..config.visualization_config import (
    configure_matplotlib_fonts, 
    get_default_data_dir,
    get_default_output_dir
)

def generate_trend_visualization(data_file=None, cities=None, start_date=None, end_date=None, 
                                output_dir=None, filename=None):
    """
    生成花粉趋势图
    
    参数:
        data_file (str): 数据文件路径，如果为None则尝试查找最新的数据文件
        cities (list): 要显示的城市列表，如果为None则显示所有城市
        start_date (str): 开始日期，如果为None则不筛选开始日期
        end_date (str): 结束日期，如果为None则不筛选结束日期
        output_dir (str): 输出目录，如果为None则使用默认目录
        filename (str): 输出文件名，如果为None则自动生成
        
    返回:
        str: 保存的图表文件路径
    """
    # 配置字体
    configure_matplotlib_fonts()
    
    # 如果没有提供数据文件，尝试查找最新的数据文件
    if data_file is None:
        data_files = find_data_files()
        if not data_files:
            raise FileNotFoundError("找不到数据文件，请提供数据文件路径")
        data_file = data_files[0]
    
    # 加载数据
    df = load_data(data_file)
    
    # 筛选数据
    filtered_df = filter_data(df, cities, start_date, end_date)
    
    # 准备数据
    viz_df = prepare_data_for_visualization(filtered_df)
    
    # 生成趋势图
    return visualize_pollen_trends(viz_df, output_dir, filename)

def generate_distribution_visualization(data_file=None, cities=None, output_dir=None, filename=None):
    """
    生成花粉分布图
    
    参数:
        data_file (str): 数据文件路径，如果为None则尝试查找最新的数据文件
        cities (list): 要显示的城市列表，如果为None则显示所有城市
        output_dir (str): 输出目录，如果为None则使用默认目录
        filename (str): 输出文件名，如果为None则自动生成
        
    返回:
        str: 保存的图表文件路径
    """
    # 配置字体
    configure_matplotlib_fonts()
    
    # 如果没有提供数据文件，尝试查找最新的数据文件
    if data_file is None:
        data_files = find_data_files()
        if not data_files:
            raise FileNotFoundError("找不到数据文件，请提供数据文件路径")
        data_file = data_files[0]
    
    # 加载数据
    df = load_data(data_file)
    
    # 筛选数据
    filtered_df = filter_data(df, cities)
    
    # 准备数据
    viz_df = prepare_data_for_visualization(filtered_df)
    
    # 生成分布图
    return visualize_pollen_distribution(viz_df, output_dir, filename)

def generate_all_visualizations(data_file=None, cities=None, start_date=None, end_date=None, output_dir=None):
    """
    生成所有可视化图表
    
    参数:
        data_file (str): 数据文件路径，如果为None则尝试查找最新的数据文件
        cities (list): 要显示的城市列表，如果为None则显示所有城市
        start_date (str): 开始日期，如果为None则不筛选开始日期
        end_date (str): 结束日期，如果为None则不筛选结束日期
        output_dir (str): 输出目录，如果为None则使用默认目录
        
    返回:
        list: 保存的图表文件路径列表
    """
    # 配置字体
    configure_matplotlib_fonts()
    
    # 如果没有提供数据文件，尝试查找最新的数据文件
    if data_file is None:
        data_files = find_data_files()
        if not data_files:
            raise FileNotFoundError("找不到数据文件，请提供数据文件路径")
        data_file = data_files[0]
    
    # 确保输出目录存在
    output_dir = ensure_output_dir(output_dir)
    
    # 加载数据
    df = load_data(data_file)
    
    # 筛选数据
    filtered_df = filter_data(df, cities, start_date, end_date)
    
    # 准备数据
    viz_df = prepare_data_for_visualization(filtered_df)
    
    # 生成并保存图表
    output_files = []
    
    # 生成趋势图
    trend_file = visualize_pollen_trends(viz_df, output_dir)
    if trend_file:
        output_files.append(trend_file)
    
    # 生成分布图
    dist_file = visualize_pollen_distribution(viz_df, output_dir)
    if dist_file:
        output_files.append(dist_file)
    
    return output_files

def get_available_cities(data_file=None):
    """
    获取数据文件中的可用城市列表
    
    参数:
        data_file (str): 数据文件路径，如果为None则尝试查找最新的数据文件
        
    返回:
        list: 可用城市列表
    """
    # 如果没有提供数据文件，尝试查找最新的数据文件
    if data_file is None:
        data_files = find_data_files()
        if not data_files:
            return []
        data_file = data_files[0]
    
    # 加载数据
    try:
        df = load_data(data_file)
        if '城市' in df.columns:
            return sorted(df['城市'].unique().tolist())
        return []
    except Exception:
        return [] 