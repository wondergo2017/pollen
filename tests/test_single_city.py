#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据可视化单城市测试脚本
用于测试单个城市的数据可视化效果
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入必要的模块
try:
    from src.visualization import pollen_visualization as pv
    from src.config.visualization_config import configure_matplotlib_fonts
    print("成功导入花粉可视化模块")
    
    # 配置matplotlib字体
    configure_matplotlib_fonts()
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保 src/visualization/pollen_visualization.py 文件存在")
    sys.exit(1)

# 测试输出目录
TEST_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'test_output')
if not os.path.exists(TEST_OUTPUT_DIR):
    os.makedirs(TEST_OUTPUT_DIR)

# 抑制不必要的警告
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

def generate_single_city_data(city_name="北京", days=30):
    """生成单个城市的样本数据"""
    levels = ["未检测", "很低", "较低", "偏高", "较高", "很高", "极高"]
    
    # 使用真实的日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days-1)
    
    # 创建日期列表
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    
    # 生成随机趋势（以春季为例，花粉浓度先上升后下降）
    import numpy as np
    
    # 基本趋势：上升-高峰-下降
    base_trend = np.concatenate([
        np.linspace(0, 5, days // 3),  # 上升阶段
        np.linspace(5, 6, days // 3),  # 高峰阶段
        np.linspace(6, 2, days - 2*(days // 3))  # 下降阶段
    ])
    
    # 添加随机波动
    noise = np.random.normal(0, 0.7, days)
    trend = base_trend + noise
    
    # 限制范围在0-6之间
    trend = np.clip(trend, 0, 6)
    
    # 创建数据
    data = []
    for i, date in enumerate(date_range):
        level_idx = int(round(trend[i]))
        level = levels[level_idx]
        
        # 添加记录
        record = {
            "city": city_name,
            "addTime": date.strftime("%Y-%m-%d"),
            "level": level,
            "level_numeric": level_idx
        }
        data.append(record)
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    return df

def test_single_city_plot():
    """测试单个城市的绘图功能"""
    print("\n测试单个城市的可视化...")
    
    # 生成测试数据
    city_name = "北京"
    df = generate_single_city_data(city_name)
    
    # 保存测试数据到文件
    test_data_file = os.path.join(TEST_OUTPUT_DIR, f"test_{city_name}_data.csv")
    df.to_csv(test_data_file, index=False, encoding="utf-8-sig")
    print(f"已生成测试数据并保存到 {test_data_file}")
    
    # 加载数据并准备可视化
    try:
        # 如果pollen_visualization模块有prepare_data_for_visualization函数
        if hasattr(pv, 'prepare_data_for_visualization'):
            df = pv.prepare_data_for_visualization(df)
        
        # 找到正确的绘图函数
        plot_function = None
        if hasattr(pv, 'plot_pollen_trend'):
            plot_function = pv.plot_pollen_trend
        elif hasattr(pv, 'visualize_pollen_trends'):
            plot_function = pv.visualize_pollen_trends
        
        if plot_function is None:
            print("✗ 找不到可用的绘图函数")
            return False
        
        # 执行可视化
        output_file = os.path.join(TEST_OUTPUT_DIR, f"{city_name}_pollen_trend.png")
        print(f"正在生成可视化图表 -> {output_file}")
        
        if plot_function == pv.visualize_pollen_trends:
            output_path = plot_function(df, TEST_OUTPUT_DIR, f"{city_name}_pollen_trend.png")
        else:
            output_path = plot_function(df, None, output_file)
        
        # 检查文件是否生成
        if os.path.exists(output_file):
            print(f"✓ 单城市可视化测试成功，图表已保存到 {output_file}")
            return True
        else:
            print(f"✗ 图表文件未生成")
            return False
    
    except Exception as e:
        print(f"✗ 单城市可视化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_single_city_plot()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 