#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉趋势可视化模块
提供生成花粉趋势图的功能
"""

import os
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import seaborn as sns
import warnings

# 抑制所有与字体相关的警告
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib.font_manager")
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib.backends")
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib.text")

from ..config.visualization_config import (
    configure_matplotlib_fonts,
    POLLEN_LEVEL_COLORS,
    LEVEL_COLORS,
    CHART_CONFIG,
    get_default_output_dir
)

def visualize_pollen_trends(df, output_dir=None, filename=None):
    """
    生成花粉趋势图
    
    参数:
        df (pandas.DataFrame): 包含花粉数据的DataFrame
        output_dir (str): 输出目录路径
        filename (str): 输出文件名
        
    返回:
        str: 保存的图表文件路径
    """
    # 检查数据是否为空
    if df.empty:
        print("警告: 数据为空，无法生成趋势图")
        return None
    
    # 配置matplotlib字体
    configure_matplotlib_fonts()
    
    # 尝试获取一个可用的字体属性对象
    try:
        import matplotlib.font_manager as fm
        # 直接创建字体属性对象，优先使用sans-serif字体族
        font_prop = fm.FontProperties(family='sans-serif')
    except Exception:
        font_prop = None
    
    # 设置输出目录
    if output_dir is None:
        output_dir = get_default_output_dir()
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 获取唯一城市列表
    cities = df['城市'].unique().tolist()
    city_count = len(cities)
    
    # 设置图表尺寸，根据城市数量调整
    fig_width = CHART_CONFIG['fig_width']
    fig_height = CHART_CONFIG['fig_height'] + 0.5 * max(0, city_count - 5)  # 根据城市数量调整高度
    
    # 创建图表
    plt.figure(figsize=(fig_width, fig_height))
    
    # 设置背景颜色
    plt.gcf().patch.set_facecolor('#f8f9fa')
    plt.gca().set_facecolor('#ffffff')
    
    # 添加网格
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 设置标题 - 使用字体属性
    if font_prop:
        plt.title("城市花粉趋势图", fontsize=CHART_CONFIG['title_size'], pad=20, fontproperties=font_prop)
    else:
        plt.title("城市花粉趋势图", fontsize=CHART_CONFIG['title_size'], pad=20)
    
    # 增加兼容性处理
    # 检查是否存在'花粉指数'列，否则使用'花粉等级'作为数值
    if '花粉指数' in df.columns:
        pollen_value_column = '花粉指数'
    else:
        pollen_value_column = '花粉等级'
        
    # 检查是否存在'花粉等级'列，如果没有则尝试从花粉指数估算
    if '花粉等级' not in df.columns and '花粉指数' in df.columns:
        def get_level(value):
            if value < 10:
                return 0  # 未检测
            elif value < 30:
                return 1  # 很低
            elif value < 50:
                return 2  # 较低
            elif value < 70:
                return 3  # 偏高
            elif value < 90:
                return 4  # 较高
            else:
                return 5  # 很高
        
        df['花粉等级'] = df['花粉指数'].apply(get_level)
    
    # 绘制每个城市的趋势线
    for i, city in enumerate(cities):
        city_data = df[df['城市'] == city].sort_values('日期')
        
        # 确保日期是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(city_data['日期']):
            city_data['日期'] = pd.to_datetime(city_data['日期'])
        
        # 绘制趋势线
        plt.plot(
            city_data['日期'], 
            city_data[pollen_value_column], 
            marker='o', 
            markersize=CHART_CONFIG['marker_size'],
            linewidth=CHART_CONFIG['line_width'],
            linestyle=CHART_CONFIG['line_style'],
            label=city
        )
    
    # 解决x轴日期标签的中文显示问题
    fig = plt.gcf()
    ax = plt.gca()
    
    # 设置x轴格式，使用自定义日期格式器
    date_formatter = mdates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(date_formatter)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    
    # 确保所有标签使用正确的字体
    if font_prop:
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontproperties(font_prop)
    
    # 设置y轴标签
    if font_prop:
        plt.ylabel("花粉指数", fontsize=CHART_CONFIG['axes_size'], fontproperties=font_prop)
    else:
        plt.ylabel("花粉指数", fontsize=CHART_CONFIG['axes_size'])
    
    # 自动旋转日期标签，避免重叠
    fig.autofmt_xdate(rotation=45)
    
    # 添加图例
    if city_count > 10:
        # 如果城市数量过多，调整图例位置和列数
        legend = plt.legend(
            loc='upper center', 
            bbox_to_anchor=(0.5, -0.15),
            ncol=min(5, city_count),
            fontsize=CHART_CONFIG['legend_size']
        )
    else:
        legend = plt.legend(loc='best', fontsize=CHART_CONFIG['legend_size'])
    
    # 为图例文本设置字体
    if font_prop and legend:
        for text in legend.get_texts():
            text.set_fontproperties(font_prop)
    
    # 设置刻度字体大小
    plt.xticks(fontsize=CHART_CONFIG['tick_size'])
    plt.yticks(fontsize=CHART_CONFIG['tick_size'])
    
    # 生成时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 设置输出文件名
    if filename is None:
        filename = f"pollen_trends_{timestamp}.{CHART_CONFIG['format']}"
    elif not filename.endswith(f".{CHART_CONFIG['format']}"):
        filename = f"{filename}.{CHART_CONFIG['format']}"
    
    # 保存图表
    output_path = os.path.join(output_dir, filename)
    plt.savefig(output_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight', format=CHART_CONFIG['format'])
    plt.close()
    
    print(f"花粉趋势图已保存到: {output_path}")
    return output_path 