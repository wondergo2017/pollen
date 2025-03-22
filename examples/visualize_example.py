#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉可视化示例脚本
展示如何使用花粉可视化模块生成各种图表
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 添加项目根目录到系统路径
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.visualization import (
    generate_trend_visualization,
    generate_distribution_visualization,
    generate_all_visualizations,
    get_available_cities,
    display_available_data_files,
    find_data_files,
    load_data
)

from src.config.visualization_config import (
    get_default_output_dir,
    get_default_data_dir,
    POLLEN_LEVEL_COLORS
)

def generate_sample_data(num_cities=5, num_days=30, random_seed=42):
    """生成示例数据"""
    print("生成示例数据...")
    
    # 设置随机种子以确保可重复性
    random.seed(random_seed)
    np.random.seed(random_seed)
    
    # 城市列表
    cities = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "西安", "南京", "重庆"]
    cities = cities[:min(num_cities, len(cities))]
    
    # 日期范围
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dates = [(end_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]
    dates.reverse()  # 从过去到现在
    
    # 花粉等级描述
    pollen_level_descriptions = [
        "无花粉", "极少花粉", "少量花粉", "中等花粉", "较多花粉", "大量花粉"
    ]
    
    # 生成数据记录
    records = []
    for city in cities:
        # 为每个城市生成一个花粉趋势基线
        baseline = np.random.uniform(0.5, 3.0)
        trend = np.random.uniform(-0.5, 0.5)
        
        for i, date in enumerate(dates):
            # 生成花粉指数，有一个缓慢的季节性趋势
            seasonal_factor = np.sin(np.pi * i / (len(dates) / 2)) * 2  # 季节性波动
            random_factor = np.random.normal(0, 0.5)  # 随机波动
            
            # 计算花粉指数
            pollen_index = max(0, min(5, baseline + trend * (i / len(dates)) + seasonal_factor + random_factor))
            pollen_level = min(int(pollen_index), 5)  # 花粉等级，0-5
            
            # 创建记录
            record = {
                "日期": date,
                "城市": city,
                "花粉指数": round(pollen_index, 2),
                "花粉等级": pollen_level,
                "花粉等级描述": pollen_level_descriptions[pollen_level]
            }
            records.append(record)
    
    # 创建DataFrame
    df = pd.DataFrame(records)
    
    # 保存到文件
    data_dir = get_default_data_dir()
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, "sample_pollen_data.csv")
    df.to_csv(file_path, index=False, encoding="utf-8")
    
    print(f"示例数据已保存到: {file_path}")
    print(f"生成了 {len(cities)} 个城市 {len(dates)} 天的数据，共 {len(records)} 条记录")
    
    return file_path

def demo_trend_visualization():
    """演示花粉趋势图生成"""
    print("\n==== 演示花粉趋势图生成 ====")
    
    # 确保示例数据存在
    data_file = os.path.join(get_default_data_dir(), "sample_pollen_data.csv")
    if not os.path.exists(data_file):
        data_file = generate_sample_data()
    
    # 获取可用城市
    cities = get_available_cities(data_file)
    print(f"可用城市: {', '.join(cities)}")
    
    # 生成所有城市的趋势图
    output_file = generate_trend_visualization(data_file)
    print(f"所有城市趋势图已保存到: {output_file}")
    
    # 生成部分城市的趋势图
    selected_cities = cities[:3] if len(cities) > 3 else cities
    output_file = generate_trend_visualization(
        data_file, 
        cities=selected_cities,
        filename="selected_cities_trend.png"
    )
    print(f"选定城市趋势图已保存到: {output_file}")

def demo_distribution_visualization():
    """演示花粉分布图生成"""
    print("\n==== 演示花粉分布图生成 ====")
    
    # 确保示例数据存在
    data_file = os.path.join(get_default_data_dir(), "sample_pollen_data.csv")
    if not os.path.exists(data_file):
        data_file = generate_sample_data()
    
    # 生成分布图
    output_file = generate_distribution_visualization(data_file)
    print(f"分布图已保存到: {output_file}")

def demo_all_visualizations():
    """演示生成所有可视化图表"""
    print("\n==== 演示生成所有可视化图表 ====")
    
    # 确保示例数据存在
    data_file = os.path.join(get_default_data_dir(), "sample_pollen_data.csv")
    if not os.path.exists(data_file):
        data_file = generate_sample_data()
    
    # 生成所有图表
    output_files = generate_all_visualizations(data_file)
    print(f"已生成 {len(output_files)} 个图表:")
    for file in output_files:
        print(f"  - {file}")

def print_data_summary(data_file):
    """打印数据摘要"""
    print("\n==== 数据摘要 ====")
    
    try:
        df = load_data(data_file)
        print(f"数据文件: {data_file}")
        print(f"记录数量: {len(df)}")
        print(f"日期范围: {df['日期'].min()} 至 {df['日期'].max()}")
        print(f"城市数量: {df['城市'].nunique()}")
        print(f"城市列表: {', '.join(sorted(df['城市'].unique()))}")
        
        if '花粉等级' in df.columns:
            levels = df['花粉等级'].value_counts().sort_index()
            print("花粉等级分布:")
            for level, count in levels.items():
                percentage = count / len(df) * 100
                print(f"  等级 {level}: {count} 条记录 ({percentage:.1f}%)")
    
    except Exception as e:
        print(f"读取数据文件时出错: {e}")

def main():
    """主函数"""
    print("====== 花粉可视化示例 ======")
    
    # 列出可用数据文件
    print("\n可用数据文件:")
    data_files = find_data_files()
    
    # 如果没有数据文件，生成示例数据
    if not data_files:
        print("未找到数据文件，将生成示例数据")
        data_file = generate_sample_data()
    else:
        # 使用最新的数据文件
        data_file = data_files[0]
        print(f"使用最新的数据文件: {data_file}")
    
    # 打印数据摘要
    print_data_summary(data_file)
    
    # 演示各种可视化功能
    demo_trend_visualization()
    demo_distribution_visualization()
    demo_all_visualizations()
    
    print("\n====== 示例完成 ======")
    print(f"所有输出文件保存在: {get_default_output_dir()}")

if __name__ == "__main__":
    main() 