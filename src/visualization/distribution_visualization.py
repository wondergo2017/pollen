#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉分布可视化模块
提供花粉分布图生成功能
"""

import os
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from ..config.visualization_config import (
    configure_matplotlib_fonts,
    POLLEN_LEVEL_COLORS,
    LEVEL_COLORS,
    CHART_CONFIG,
    get_default_output_dir
)

def visualize_pollen_distribution(df, output_dir=None, filename=None):
    """
    生成花粉分布图
    
    参数:
        df (pandas.DataFrame): 包含花粉数据的DataFrame
        output_dir (str): 输出目录路径
        filename (str): 输出文件名
        
    返回:
        str: 保存的图表文件路径
    """
    # 检查数据是否为空
    if df.empty:
        print("警告: 数据为空，无法生成分布图")
        return None
    
    # 配置matplotlib字体
    configure_matplotlib_fonts()
    
    # 设置输出目录
    if output_dir is None:
        output_dir = get_default_output_dir()
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 获取唯一城市列表
    cities = df['城市'].unique().tolist()
    city_count = len(cities)
    
    # 如果数据包含日期列，获取最新日期
    latest_date = None
    if '日期' in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df['日期']):
            df['日期'] = pd.to_datetime(df['日期'])
        latest_date = df['日期'].max().strftime('%Y-%m-%d')
    
    # 设置图表尺寸，根据城市数量调整
    fig_width = CHART_CONFIG['fig_width']
    fig_height = CHART_CONFIG['fig_height']
    
    # 创建图表
    plt.figure(figsize=(fig_width, fig_height))
    
    # 设置背景颜色
    plt.gcf().patch.set_facecolor('#f8f9fa')
    plt.gca().set_facecolor('#ffffff')
    
    # 设置标题
    if latest_date:
        plt.title(f"城市花粉分布图 ({latest_date})", fontsize=CHART_CONFIG['title_size'], pad=20)
    else:
        plt.title("城市花粉分布图", fontsize=CHART_CONFIG['title_size'], pad=20)
    
    # 增加兼容性处理
    # 检查是否存在花粉等级列
    pollen_categorical = False
    
    if '花粉等级' in df.columns:
        # 使用花粉等级分类数据
        pollen_categorical = True
        
        # 准备数据
        # 对于每个城市，计算每个等级的花粉数据数量
        city_level_counts = df.groupby(['城市', '花粉等级']).size().unstack(fill_value=0)
        
        # 如果有多个日期，我们取每个城市最近一天的数据
        if '日期' in df.columns and len(df['日期'].unique()) > 1:
            latest_data = df.loc[df.groupby('城市')['日期'].idxmax()]
            city_levels = latest_data.set_index('城市')['花粉等级']
            
            # 创建一个新的DataFrame仅包含最新数据
            city_level_data = pd.DataFrame(index=cities)
            for city in cities:
                if city in city_levels.index:
                    city_level_data.loc[city, '花粉等级'] = city_levels[city]
                else:
                    city_level_data.loc[city, '花粉等级'] = '未知'
        else:
            # 计算每个城市的平均花粉等级
            city_level_data = df.groupby('城市')['花粉等级'].agg(lambda x: x.value_counts().index[0])
            city_level_data = pd.DataFrame(city_level_data)
        
        # 转换花粉等级为数值进行排序
        level_order = ['未检测', '很低', '较低', '偏高', '较高', '很高', '极高']
        
        # 处理可能出现的未知等级
        for level in df['花粉等级'].unique():
            if level not in level_order and level != '暂无':
                level_order.append(level)
        
        # 将'暂无'放在最后
        if '暂无' in df['花粉等级'].unique():
            level_order.append('暂无')
        
        # 准备颜色映射
        colors = {}
        for level in level_order:
            if level in LEVEL_COLORS:
                colors[level] = LEVEL_COLORS[level]
            else:
                # 对于未知等级使用灰色
                colors[level] = '#CCCCCC'
        
        # 计算每个城市的等级分布百分比
        if city_count > 0:
            level_percentages = {}
            for city in cities:
                city_data = df[df['城市'] == city]
                if not city_data.empty:
                    level_counts = city_data['花粉等级'].value_counts()
                    total = level_counts.sum()
                    level_percentages[city] = {level: count/total*100 for level, count in level_counts.items()}
            
            # 创建堆叠条形图
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            
            # 设置背景
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            # 计算每个城市每个等级的百分比
            levels_data = {}
            for level in level_order:
                levels_data[level] = []
                for city in cities:
                    if city in level_percentages and level in level_percentages[city]:
                        levels_data[level].append(level_percentages[city][level])
                    else:
                        levels_data[level].append(0)
            
            # 绘制堆叠条形图
            bottom = np.zeros(len(cities))
            for level in level_order:
                if level in levels_data:
                    ax.barh(cities, levels_data[level], left=bottom, color=colors[level], label=level)
                    bottom += np.array(levels_data[level])
            
            # 设置图例
            ax.legend(title="花粉等级", loc='lower right', fontsize=CHART_CONFIG['legend_size'])
            
            # 设置标题和标签
            if latest_date:
                ax.set_title(f"城市花粉等级分布 ({latest_date})", fontsize=CHART_CONFIG['title_size'], pad=20)
            else:
                ax.set_title("城市花粉等级分布", fontsize=CHART_CONFIG['title_size'], pad=20)
            
            ax.set_xlabel("百分比 (%)", fontsize=CHART_CONFIG['axes_size'])
            ax.set_ylabel("城市", fontsize=CHART_CONFIG['axes_size'])
            
            # 添加网格线
            ax.grid(True, axis='x', linestyle='--', alpha=0.7)
            
            # 设置百分比刻度
            ax.set_xlim(0, 100)
            
            # 设置刻度标签字体大小
            ax.tick_params(axis='both', labelsize=CHART_CONFIG['tick_size'])
            
            # 添加百分比标签
            for i, city in enumerate(cities):
                ax.text(101, i, f"{city}", va='center', fontsize=CHART_CONFIG['tick_size'])
            
            plt.tight_layout()
            
    else:
        # 使用花粉指数数值数据
        # 检查是否存在'花粉指数'列，如果没有则尝试使用其他列
        if '花粉指数' in df.columns:
            value_column = '花粉指数'
        elif '花粉强度' in df.columns:
            value_column = '花粉强度'
        elif '指数' in df.columns:
            value_column = '指数'
        else:
            # 如果没有找到合适的列，使用第一个数值列
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                value_column = numeric_cols[0]
            else:
                print("错误: 没有找到合适的数值列来绘制花粉分布图")
                return None
        
        # 计算每个城市的平均花粉指数
        city_means = df.groupby('城市')[value_column].mean().sort_values(ascending=False)
        
        # 设置颜色映射
        def get_color(value):
            if value < 10:
                return LEVEL_COLORS.get("未检测", "#999999")
            elif value < 30:
                return LEVEL_COLORS.get("很低", "#81CB31")
            elif value < 50:
                return LEVEL_COLORS.get("较低", "#A1FF3D")
            elif value < 70:
                return LEVEL_COLORS.get("偏高", "#F5EE32")
            elif value < 90:
                return LEVEL_COLORS.get("较高", "#FFAF13")
            else:
                return LEVEL_COLORS.get("很高", "#FF2319")
        
        # 为每个城市分配颜色
        colors = [get_color(value) for value in city_means.values]
        
        # 创建水平条形图
        plt.figure(figsize=(fig_width, fig_height))
        plt.barh(city_means.index, city_means.values, color=colors)
        
        # 设置标题和标签
        if latest_date:
            plt.title(f"城市花粉指数分布 ({latest_date})", fontsize=CHART_CONFIG['title_size'], pad=20)
        else:
            plt.title("城市花粉指数分布", fontsize=CHART_CONFIG['title_size'], pad=20)
        
        plt.xlabel("花粉指数", fontsize=CHART_CONFIG['axes_size'])
        plt.ylabel("城市", fontsize=CHART_CONFIG['axes_size'])
        
        # 添加数值标签
        for i, v in enumerate(city_means.values):
            plt.text(v + 1, i, f"{v:.1f}", va='center', fontsize=CHART_CONFIG['annotation_size'])
        
        # 添加网格线
        plt.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        # 设置刻度标签字体大小
        plt.xticks(fontsize=CHART_CONFIG['tick_size'])
        plt.yticks(fontsize=CHART_CONFIG['tick_size'])
    
    # 生成时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 设置输出文件名
    if filename is None:
        filename = f"pollen_distribution_{timestamp}.{CHART_CONFIG['format']}"
    elif not filename.endswith(f".{CHART_CONFIG['format']}"):
        filename = f"{filename}.{CHART_CONFIG['format']}"
    
    # 保存图表
    output_path = os.path.join(output_dir, filename)
    plt.savefig(output_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight', format=CHART_CONFIG['format'])
    plt.close()
    
    print(f"花粉分布图已保存到: {output_path}")
    return output_path 