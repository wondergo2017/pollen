#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据可视化核心模块
此模块提供了花粉数据可视化的核心功能，包括数据加载、处理和生成可视化图表。
"""

import os
import sys
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 获取项目根目录
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# 导入配置模块
sys.path.insert(0, PROJECT_ROOT)
from src.config.visualization_config import (
    configure_matplotlib_fonts, 
    POLLEN_LEVEL_COLORS,
    POLLEN_LEVEL_NAMES,
    POLLEN_LEVEL_DESCRIPTIONS,
    CHART_CONFIG,
    get_default_output_dir,
    get_default_data_dir
)

# 配置matplotlib中文字体
configure_matplotlib_fonts()

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
        
        # 检查必要的列是否存在
        required_columns = ['日期', '城市', '花粉等级']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"数据文件缺少必要的列: {', '.join(missing_columns)}")
        
        return df
    
    except Exception as e:
        print(f"加载数据文件出错: {e}")
        raise

def filter_data(df, cities=None, start_date=None, end_date=None):
    """
    根据条件过滤数据
    
    参数:
        df (pandas.DataFrame): 要过滤的数据
        cities (list): 要包含的城市列表
        start_date (str): 开始日期，格式 'YYYY-MM-DD'
        end_date (str): 结束日期，格式 'YYYY-MM-DD'
        
    返回:
        pandas.DataFrame: 过滤后的数据
    """
    filtered_df = df.copy()
    
    # 按城市过滤
    if cities:
        filtered_df = filtered_df[filtered_df['城市'].isin(cities)]
    
    # 转换日期列为日期类型以便进行过滤
    filtered_df['日期'] = pd.to_datetime(filtered_df['日期'])
    
    # 按日期范围过滤
    if start_date:
        filtered_df = filtered_df[filtered_df['日期'] >= pd.to_datetime(start_date)]
    
    if end_date:
        filtered_df = filtered_df[filtered_df['日期'] <= pd.to_datetime(end_date)]
    
    # 如果过滤后没有数据，给出警告
    if len(filtered_df) == 0:
        print("警告: 过滤后没有剩余数据")
    
    return filtered_df

def prepare_data_for_visualization(df):
    """
    为可视化准备数据，包括日期转换和值的标准化
    
    参数:
        df (pandas.DataFrame): 要处理的数据
        
    返回:
        pandas.DataFrame: 处理后的数据
    """
    prepared_df = df.copy()
    
    # 确保日期列是日期类型
    prepared_df['日期'] = pd.to_datetime(prepared_df['日期'])
    
    # 确保花粉等级是数值类型
    if '花粉等级' in prepared_df.columns:
        prepared_df['花粉等级'] = pd.to_numeric(prepared_df['花粉等级'], errors='coerce')
    
    # 确保花粉浓度是数值类型
    if '花粉浓度' in prepared_df.columns:
        prepared_df['花粉浓度'] = pd.to_numeric(prepared_df['花粉浓度'], errors='coerce')
    
    # 按日期和城市排序
    prepared_df = prepared_df.sort_values(['城市', '日期'])
    
    return prepared_df

def visualize_pollen_trends(df, output_dir=None, filename=None):
    """
    生成花粉等级趋势图
    
    参数:
        df (pandas.DataFrame): 包含花粉数据的DataFrame
        output_dir (str): 输出目录路径
        filename (str): 输出文件名
        
    返回:
        str: 输出文件的完整路径
    """
    # 配置输出
    if output_dir is None:
        output_dir = get_default_output_dir()
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pollen_trends_{timestamp}.png"
    
    output_path = os.path.join(output_dir, filename)
    
    # 确保日期列是日期时间类型
    if not pd.api.types.is_datetime64_dtype(df['日期']):
        df = prepare_data_for_visualization(df)
    
    # 获取数据中的城市列表
    cities = df['城市'].unique()
    num_cities = len(cities)
    
    # 设置图表尺寸
    fig_width = CHART_CONFIG['figure_size'][0]
    fig_height = max(CHART_CONFIG['figure_size'][1], num_cities * 1.0)
    plt.figure(figsize=(fig_width, fig_height))
    
    # 创建颜色映射
    color_map = {}
    for level, color in POLLEN_LEVEL_COLORS.items():
        try:
            color_map[int(level)] = color
        except ValueError:
            # 如果键不是数字，则跳过
            pass
    
    # 计算绘图区域
    left_margin = 0.12
    right_margin = 0.88
    top_margin = 0.92
    bottom_margin = 0.1
    
    # 添加图表标题
    date_range = f"{df['日期'].min().strftime('%Y-%m-%d')} 至 {df['日期'].max().strftime('%Y-%m-%d')}"
    plt.suptitle(f"花粉等级趋势图 ({date_range})", 
                fontsize=CHART_CONFIG['title_size'],
                y=0.98)
    
    # 为每个城市创建子图
    for i, city in enumerate(cities):
        city_data = df[df['城市'] == city]
        
        # 创建子图
        ax_height = (top_margin - bottom_margin) / num_cities
        ax_position = [left_margin, 
                      bottom_margin + (num_cities - i - 1) * ax_height, 
                      right_margin - left_margin, 
                      ax_height * 0.8]
        ax = plt.axes(ax_position)
        
        # 绘制花粉等级趋势线
        x = city_data['日期']
        y = city_data['花粉等级']
        
        # 绘制线图
        ax.plot(x, y, '-o', markersize=4, linewidth=2, color='#205AA7', alpha=0.8)
        
        # 为每个点添加颜色标记
        for j, (date, level) in enumerate(zip(x, y)):
            if pd.notna(level) and int(level) in color_map:
                marker_color = color_map[int(level)]
                ax.plot(date, level, 'o', markersize=8, color=marker_color)
        
        # 设置y轴范围和标签
        ax.set_ylim(-0.5, 5.5)
        ax.set_yticks(range(6))
        ax.set_yticklabels([POLLEN_LEVEL_NAMES.get(str(i), str(i)) for i in range(6)], 
                           fontsize=CHART_CONFIG['tick_size'])
        
        # 设置x轴日期格式
        max_ticks = 15
        step_size = max(1, len(x) // max_ticks)
        
        # 选择日期作为刻度
        if len(x) <= max_ticks:
            tick_dates = x
        else:
            tick_dates = [date for i, date in enumerate(x) if i % step_size == 0]
        
        ax.set_xticks(tick_dates)
        ax.set_xticklabels([date.strftime('%m-%d') for date in tick_dates], 
                          rotation=45, ha='right', fontsize=CHART_CONFIG['tick_size'])
        
        # 设置网格线
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # 设置城市标签
        ax.set_ylabel(city, fontsize=CHART_CONFIG['axes_size'], rotation=0, 
                    ha='right', va='center', labelpad=10)
        
        # 如果不是最下面的子图，不显示x轴标签
        if i < num_cities - 1:
            ax.set_xticklabels([])
            ax.set_xlabel('')
        else:
            ax.set_xlabel('日期', fontsize=CHART_CONFIG['axes_size'])
        
        # 添加花粉类型信息（如果存在）
        if '花粉类型' in city_data.columns:
            pollen_types = city_data['花粉类型'].unique()
            if len(pollen_types) > 0 and not pd.isna(pollen_types[0]):
                pollen_type = pollen_types[0]
                ax.text(0.99, 0.95, f"类型: {pollen_type}", 
                       transform=ax.transAxes, ha='right', va='top',
                       fontsize=CHART_CONFIG['annotation_size'],
                       bbox=dict(boxstyle="round,pad=0.3", fc="#f0f0f0", ec="gray", alpha=0.8))
    
    # 添加花粉等级说明
    legend_elements = []
    for level, name in POLLEN_LEVEL_NAMES.items():
        if level in color_map:
            patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color_map[int(level)],
                              markersize=10, label=f"{level}级: {name}")
            legend_elements.append(patch)
    
    # 只有当有图例元素时才添加图例
    if legend_elements:
        plt.figlegend(handles=legend_elements, loc='center', bbox_to_anchor=(0.5, 0.02),
                     ncol=min(3, len(legend_elements)), fontsize=CHART_CONFIG['legend_size'])
    
    # 保存图表
    plt.savefig(output_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight', format=CHART_CONFIG['format'])
    plt.close()
    
    return output_path

def visualize_pollen_distribution(df, output_dir=None, filename=None):
    """
    生成花粉等级分布图
    
    参数:
        df (pandas.DataFrame): 包含花粉数据的DataFrame
        output_dir (str): 输出目录路径
        filename (str): 输出文件名
        
    返回:
        str: 输出文件的完整路径
    """
    # 配置输出
    if output_dir is None:
        output_dir = get_default_output_dir()
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pollen_distribution_{timestamp}.png"
    
    output_path = os.path.join(output_dir, filename)
    
    # 确保日期列是日期时间类型
    if not pd.api.types.is_datetime64_dtype(df['日期']):
        df = prepare_data_for_visualization(df)
    
    # 获取数据中的城市列表
    cities = sorted(df['城市'].unique())
    num_cities = len(cities)
    
    # 设置图表风格
    sns.set_style("whitegrid")
    
    # 创建图表
    fig, axes = plt.subplots(2, 1, figsize=(10, 12))
    
    # 1. 花粉等级分布条形图
    ax1 = axes[0]
    
    # 为每个城市计算不同花粉等级的分布
    distribution_data = []
    for city in cities:
        city_data = df[df['城市'] == city]
        for level in range(6):
            count = len(city_data[city_data['花粉等级'] == level])
            percentage = count / len(city_data) * 100 if len(city_data) > 0 else 0
            distribution_data.append({
                '城市': city,
                '花粉等级': level,
                '天数': count,
                '百分比': percentage
            })
    
    distribution_df = pd.DataFrame(distribution_data)
    
    # 绘制条形图
    city_order = cities
    level_order = list(range(6))
    
    for i, level in enumerate(level_order):
        level_data = distribution_df[distribution_df['花粉等级'] == level]
        bottom = np.zeros(len(city_order))
        
        # 如果有之前的层，获取累积高度
        if i > 0:
            for prev_level in range(i):
                prev_data = distribution_df[distribution_df['花粉等级'] == prev_level]
                for j, city in enumerate(city_order):
                    city_prev_data = prev_data[prev_data['城市'] == city]
                    if not city_prev_data.empty:
                        bottom[j] += city_prev_data.iloc[0]['百分比']
        
        # 获取颜色
        bar_color = POLLEN_LEVEL_COLORS.get(str(level), '#999999')
        
        # 绘制当前层的条形
        bars = ax1.bar(city_order, 
                     level_data.set_index('城市').loc[city_order]['百分比'].values, 
                     bottom=bottom, 
                     color=bar_color, 
                     alpha=0.8,
                     label=POLLEN_LEVEL_NAMES.get(str(level), f'{level}级'))
        
        # 在条形上添加百分比标签（仅当百分比大于5%时）
        for j, (city, bar) in enumerate(zip(city_order, bars)):
            city_level_data = level_data[level_data['城市'] == city]
            if not city_level_data.empty:
                percentage = city_level_data.iloc[0]['百分比']
                if percentage >= 5:  # 仅显示大于5%的标签
                    ax1.text(j, bottom[j] + percentage/2, 
                           f"{percentage:.0f}%", 
                           ha='center', va='center',
                           fontsize=CHART_CONFIG['annotation_size']-1,
                           color='black' if percentage >= 20 else 'white')
    
    # 设置图表属性
    ax1.set_title("各城市花粉等级分布", fontsize=CHART_CONFIG['title_size'])
    ax1.set_xlabel("城市", fontsize=CHART_CONFIG['axes_size'])
    ax1.set_ylabel("比例 (%)", fontsize=CHART_CONFIG['axes_size'])
    ax1.set_ylim(0, 100)
    ax1.set_yticks(range(0, 101, 10))
    ax1.legend(fontsize=CHART_CONFIG['legend_size'], title="花粉等级", 
              title_fontsize=CHART_CONFIG['legend_size'])
    
    # 2. 平均花粉等级热力图
    ax2 = axes[1]
    
    # 创建每个城市每天的花粉等级数据
    pivot_df = df.pivot_table(
        index='城市', 
        columns=df['日期'].dt.date, 
        values='花粉等级',
        aggfunc='mean'
    )
    
    # 设置颜色映射
    level_cmap = plt.cm.get_cmap('YlOrRd', 6)
    
    # 绘制热力图
    sns.heatmap(pivot_df, 
               cmap=level_cmap, 
               vmin=0, 
               vmax=5,
               linewidths=0.5,
               cbar_kws={'label': '花粉等级'},
               ax=ax2)
    
    # 设置图表属性
    ax2.set_title("各城市花粉等级变化热力图", fontsize=CHART_CONFIG['title_size'])
    ax2.set_xlabel("日期", fontsize=CHART_CONFIG['axes_size'])
    ax2.set_ylabel("城市", fontsize=CHART_CONFIG['axes_size'])
    
    # 设置日期标签
    # 如果日期过多，选择部分日期显示
    date_cols = pivot_df.columns
    max_ticks = 15
    
    if len(date_cols) > max_ticks:
        step_size = len(date_cols) // max_ticks
        tick_positions = list(range(0, len(date_cols), step_size))
        tick_labels = [date_cols[i].strftime('%m-%d') for i in tick_positions]
        
        ax2.set_xticks(tick_positions)
        ax2.set_xticklabels(tick_labels, rotation=45, ha='right')
    else:
        ax2.set_xticklabels([date.strftime('%m-%d') for date in date_cols], 
                          rotation=45, ha='right')
    
    # 调整布局
    plt.tight_layout()
    fig.subplots_adjust(hspace=0.3)
    
    # 保存图表
    plt.savefig(output_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight', format=CHART_CONFIG['format'])
    plt.close()
    
    return output_path

def generate_all_visualizations(df, output_dir=None):
    """
    为数据生成所有可视化图表
    
    参数:
        df (pandas.DataFrame): 包含花粉数据的DataFrame
        output_dir (str): 输出目录路径
        
    返回:
        list: 所有输出文件的路径列表
    """
    # 配置输出
    if output_dir is None:
        output_dir = get_default_output_dir()
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 准备数据
    prepared_df = prepare_data_for_visualization(df)
    
    # 生成输出文件路径列表
    output_files = []
    
    # 1. 所有城市的花粉趋势图
    trend_file = visualize_pollen_trends(
        prepared_df, 
        output_dir=output_dir,
        filename="all_cities_pollen_trends.png"
    )
    output_files.append(trend_file)
    
    # 2. 花粉等级分布图
    dist_file = visualize_pollen_distribution(
        prepared_df, 
        output_dir=output_dir,
        filename="pollen_distribution.png"
    )
    output_files.append(dist_file)
    
    # 3. 如果有3个或更多城市，为每个城市生成单独的趋势图
    cities = prepared_df['城市'].unique()
    if len(cities) >= 3:
        for city in cities:
            city_df = prepared_df[prepared_df['城市'] == city]
            city_file = visualize_pollen_trends(
                city_df, 
                output_dir=output_dir,
                filename=f"{city}_pollen_trend.png"
            )
            output_files.append(city_file)
    
    return output_files

# 如果直接运行此脚本，执行示例可视化
if __name__ == "__main__":
    # 尝试加载数据目录中的数据文件
    data_dir = get_default_data_dir()
    sample_file = os.path.join(data_dir, "sample_pollen_data.csv")
    
    if os.path.exists(sample_file):
        # 加载数据并生成可视化
        print(f"加载样本数据: {sample_file}")
        sample_df = load_data(sample_file)
        
        print("生成可视化...")
        output_files = generate_all_visualizations(sample_df)
        
        print("可视化完成！输出文件:")
        for file_path in output_files:
            print(f"- {file_path}")
    else:
        print(f"样本数据文件不存在: {sample_file}")
        print("请先运行示例脚本生成示例数据: python examples/visualize_example.py") 