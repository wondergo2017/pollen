#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据可视化示例脚本
此脚本展示了如何使用花粉数据可视化模块
"""

import os
import sys
import pandas as pd

# 添加项目根目录到系统路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# 导入可视化模块
from src.visualization import pollen_visualization as pv
from src.config.visualization_config import (
    configure_matplotlib_fonts, 
    get_default_data_dir,
    get_default_output_dir
)

def generate_sample_data(output_file=None):
    """生成示例数据文件"""
    if output_file is None:
        data_dir = get_default_data_dir()
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        output_file = os.path.join(data_dir, 'sample_pollen_data.csv')
    
    # 创建示例数据
    print(f"生成示例数据文件: {output_file}")
    
    # 检查文件是否已存在
    if os.path.exists(output_file):
        print(f"示例数据文件已存在: {output_file}")
        return output_file
    
    # 城市列表
    cities = ['北京', '上海', '广州', '成都', '武汉', '西安']
    # 花粉类型
    pollen_types = {
        '北京': '杨树花粉',
        '上海': '梧桐花粉',
        '广州': '草本花粉',
        '成都': '松树花粉',
        '武汉': '柏树花粉',
        '西安': '柳树花粉'
    }
    
    # 创建日期范围 (2025年3月1日到3月31日)
    dates = pd.date_range(start='2025-03-01', end='2025-03-31')
    
    # 准备数据列表
    data = []
    
    import random
    random.seed(42)  # 确保结果可重复
    
    for city in cities:
        # 每个城市的花粉等级初始值 (0-5)
        level = random.randint(0, 2)
        
        for date in dates:
            # 花粉等级有一定的连续性，在前一天的基础上小幅变化
            change = random.choice([-1, -1, 0, 0, 0, 1, 1])
            level = max(0, min(5, level + change))  # 限制在0-5范围内
            
            # 根据等级生成相应的花粉浓度值
            if level == 0:
                concentration = random.randint(0, 10)
            elif level == 1:
                concentration = random.randint(10, 20)
            elif level == 2:
                concentration = random.randint(20, 40)
            elif level == 3:
                concentration = random.randint(40, 80)
            elif level == 4:
                concentration = random.randint(80, 120)
            else:  # level == 5
                concentration = random.randint(120, 200)
            
            # 添加记录
            data.append({
                '日期': date.strftime('%Y-%m-%d'),
                '城市': city,
                '花粉等级': level,
                '花粉浓度': concentration,
                '花粉类型': pollen_types[city]
            })
    
    # 创建DataFrame并保存
    df = pd.DataFrame(data)
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 保存为CSV
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"已生成示例数据，共 {len(df)} 条记录")
    
    return output_file

def run_visualization_examples():
    """运行可视化示例"""
    # 配置matplotlib字体
    configure_matplotlib_fonts()
    
    # 获取示例数据
    data_file = generate_sample_data()
    
    # 加载数据
    print(f"\n加载数据: {data_file}")
    df = pv.load_data(data_file)
    print(f"成功加载 {len(df)} 条记录")
    
    # 获取数据概览
    print("\n数据概览:")
    print(f"- 城市列表: {', '.join(df['城市'].unique())}")
    print(f"- 日期范围: {df['日期'].min()} 至 {df['日期'].max()}")
    print(f"- 花粉等级范围: {df['花粉等级'].min()} 至 {df['花粉等级'].max()}")
    
    # 准备输出目录
    output_dir = get_default_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    
    # 示例1: 所有城市的花粉趋势图
    print("\n示例1: 生成所有城市的花粉趋势图")
    prepared_df = pv.prepare_data_for_visualization(df)
    output_path = pv.visualize_pollen_trends(prepared_df, output_dir=output_dir)
    print(f"输出文件: {output_path}")
    
    # 示例2: 仅展示部分城市的花粉趋势图
    print("\n示例2: 生成北京和上海的花粉趋势图")
    filtered_df = pv.filter_data(df, cities=['北京', '上海'])
    prepared_df = pv.prepare_data_for_visualization(filtered_df)
    output_path = pv.visualize_pollen_trends(
        prepared_df, 
        output_dir=output_dir,
        filename="beijing_shanghai_trends.png"
    )
    print(f"输出文件: {output_path}")
    
    # 示例3: 花粉分布图
    print("\n示例3: 生成花粉分布图")
    output_path = pv.visualize_pollen_distribution(prepared_df, output_dir=output_dir)
    print(f"输出文件: {output_path}")
    
    # 示例4: 特定日期范围的趋势图
    print("\n示例4: 生成特定日期范围 (3月10日至3月20日) 的花粉趋势图")
    date_filtered_df = pv.filter_data(df, start_date='2025-03-10', end_date='2025-03-20')
    prepared_df = pv.prepare_data_for_visualization(date_filtered_df)
    output_path = pv.visualize_pollen_trends(
        prepared_df, 
        output_dir=output_dir,
        filename="pollen_trends_mar10_20.png"
    )
    print(f"输出文件: {output_path}")
    
    print("\n所有示例已完成。可视化结果保存在: " + output_dir)

if __name__ == "__main__":
    try:
        run_visualization_examples()
    except Exception as e:
        print(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 