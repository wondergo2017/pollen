#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉可视化工具模块
此模块提供了花粉可视化的辅助工具函数
"""

import os
import glob
import pandas as pd
import datetime

from ..config.visualization_config import get_default_data_dir, get_default_output_dir

def find_data_files(data_dir=None, pattern="*.csv"):
    """
    在指定目录中查找数据文件
    
    参数:
        data_dir (str): 数据目录，如果为None则使用默认目录
        pattern (str): 文件匹配模式，默认为"*.csv"
        
    返回:
        list: 找到的数据文件列表
    """
    if data_dir is None:
        data_dir = get_default_data_dir()
    
    # 确保目录存在
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        return []
    
    # 查找匹配的文件
    search_path = os.path.join(data_dir, pattern)
    files = glob.glob(search_path)
    
    # 按修改时间排序
    files.sort(key=os.path.getmtime, reverse=True)
    
    return files

def display_available_data_files(data_dir=None):
    """
    显示可用的数据文件
    
    参数:
        data_dir (str): 数据目录，如果为None则使用默认目录
        
    返回:
        list: 找到的数据文件列表
    """
    if data_dir is None:
        data_dir = get_default_data_dir()
    
    files = find_data_files(data_dir)
    
    if not files:
        print(f"在目录 {data_dir} 中没有找到数据文件。")
        return []
    
    print(f"找到 {len(files)} 个数据文件:")
    for i, file_path in enumerate(files):
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / 1024  # KB
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        
        print(f"{i+1}. {file_name} ({file_size:.1f} KB, {file_time})")
    
    return files

def ensure_output_dir(output_dir=None):
    """
    确保输出目录存在
    
    参数:
        output_dir (str): 输出目录，如果为None则使用默认目录
        
    返回:
        str: 输出目录路径
    """
    if output_dir is None:
        output_dir = get_default_output_dir()
    
    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir

def generate_output_filename(prefix, format="png"):
    """
    生成带有时间戳的输出文件名
    
    参数:
        prefix (str): 文件名前缀
        format (str): 文件格式，默认为"png"
        
    返回:
        str: 生成的文件名
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{format}" 