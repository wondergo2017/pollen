#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据使用示例
演示如何使用模块化的花粉数据功能
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 添加项目根目录到系统路径
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data.main import (
    get_pollen_data_for_city,
    get_pollen_data_for_cities,
    get_sample_data,
    save_pollen_data,
    list_all_cities,
    get_city_info
)

def print_dataframe_info(df, description):
    """打印DataFrame的基本信息"""
    print(f"\n========== {description} ==========")
    if df.empty:
        print("DataFrame 为空")
        return
    
    print(f"形状: {df.shape}")
    print(f"列: {list(df.columns)}")
    print(f"数据示例:")
    print(df.head(5))
    print("=" * (20 + len(description)))

def example_get_city_info():
    """示例：获取城市信息"""
    print("\n示例：获取城市信息")
    
    # 根据城市代码获取信息
    beijing_info = get_city_info("beijing")
    print(f"北京信息: {beijing_info}")
    
    # 根据城市名称获取信息
    shanghai_info = get_city_info("上海")
    print(f"上海信息: {shanghai_info}")

def example_list_cities():
    """示例：列出所有可用城市"""
    print("\n示例：列出所有城市")
    
    cities_df = list_all_cities()
    print_dataframe_info(cities_df, "所有可用城市")

def example_sample_data():
    """示例：生成示例数据"""
    print("\n示例：生成示例数据")
    
    # 生成3个城市最近10天的示例数据
    sample_df = get_sample_data(num_cities=3, num_days=10)
    print_dataframe_info(sample_df, "示例数据")
    
    # 保存示例数据
    output_dir = os.path.join(project_root, "data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "sample_data")
    
    save_pollen_data(sample_df, filename=output_file, format="csv")
    print(f"示例数据已保存到: {output_file}.csv")

def example_get_real_data():
    """示例：获取真实花粉数据（注意：需要联网）"""
    print("\n示例：获取真实花粉数据")
    
    try:
        # 获取北京的花粉数据（最近7天）
        beijing_df = get_pollen_data_for_city("beijing", days=7)
        print_dataframe_info(beijing_df, "北京花粉数据")
        
        # 获取多个城市的花粉数据
        cities_df = get_pollen_data_for_cities(["shanghai", "guangzhou"], days=5)
        print_dataframe_info(cities_df, "上海和广州花粉数据")
    
    except Exception as e:
        print(f"获取真实数据时出错: {str(e)}")
        print("请检查网络连接或使用示例数据进行测试")

def main():
    """主函数，运行所有示例"""
    print("=" * 60)
    print("花粉数据模块使用示例")
    print("=" * 60)
    
    # 运行示例
    example_get_city_info()
    example_list_cities()
    example_sample_data()
    
    # 注意：获取真实数据需要联网
    # 取消下面的注释来测试真实数据获取
    # example_get_real_data()
    
    print("\n示例运行完成！")

if __name__ == "__main__":
    main() 