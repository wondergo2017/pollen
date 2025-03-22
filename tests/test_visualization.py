#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据可视化测试模块
此模块测试花粉数据可视化功能
"""

import os
import sys
import unittest
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
import matplotlib.font_manager as fm
import warnings

# 添加项目根目录到系统路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.visualization import pollen_visualization as pv
from src.config.visualization_config import configure_matplotlib_fonts, PRIMARY_FONT, CJK_FONT

class TestPollenVisualization(unittest.TestCase):
    """测试花粉数据可视化类"""

    def setUp(self):
        """测试前的准备工作"""
        # 配置中文字体
        configure_matplotlib_fonts()
        
        # 测试数据路径
        self.data_file = os.path.join(project_root, 'data', 'sample_pollen_data.csv')
        
        # 测试输出目录
        self.output_dir = os.path.join(project_root, 'tests', 'test_output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 加载测试数据
        try:
            self.df = pd.read_csv(self.data_file)
            self.assertTrue(len(self.df) > 0, "测试数据文件为空")
        except Exception as e:
            self.fail(f"无法加载测试数据: {e}")

    def test_load_data(self):
        """测试数据加载函数"""
        df = pv.load_data(self.data_file)
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        self.assertIn('城市', df.columns)
        self.assertIn('花粉等级', df.columns)
        self.assertIn('花粉浓度', df.columns)
        
    def test_filter_data(self):
        """测试数据过滤函数"""
        # 按城市过滤
        df_city = pv.filter_data(self.df, cities=['北京'])
        self.assertGreater(len(df_city), 0)
        self.assertEqual(len(df_city['城市'].unique()), 1)
        self.assertEqual(df_city['城市'].unique()[0], '北京')
        
        # 按日期过滤
        df_date = pv.filter_data(self.df, start_date='2025-03-03', end_date='2025-03-05')
        self.assertGreater(len(df_date), 0)
        self.assertTrue(all(pd.to_datetime(df_date['日期']) >= pd.to_datetime('2025-03-03')))
        self.assertTrue(all(pd.to_datetime(df_date['日期']) <= pd.to_datetime('2025-03-05')))
        
        # 按城市和日期过滤
        df_both = pv.filter_data(self.df, cities=['上海', '广州'], start_date='2025-03-01', end_date='2025-03-03')
        self.assertGreater(len(df_both), 0)
        self.assertEqual(len(df_both['城市'].unique()), 2)
        self.assertTrue(all(city in ['上海', '广州'] for city in df_both['城市'].unique()))
        self.assertTrue(all(pd.to_datetime(df_both['日期']) >= pd.to_datetime('2025-03-01')))
        self.assertTrue(all(pd.to_datetime(df_both['日期']) <= pd.to_datetime('2025-03-03')))

    def test_prepare_data_for_visualization(self):
        """测试数据准备函数"""
        prepared_df = pv.prepare_data_for_visualization(self.df)
        self.assertIsNotNone(prepared_df)
        self.assertGreater(len(prepared_df), 0)
        # 检查是否已将日期转换为日期类型
        self.assertTrue(pd.api.types.is_datetime64_dtype(prepared_df['日期']))

    def test_visualize_pollen_trends(self):
        """测试花粉趋势可视化函数"""
        prepared_df = pv.prepare_data_for_visualization(self.df)
        output_path = pv.visualize_pollen_trends(prepared_df, output_dir=self.output_dir)
        self.assertIsNotNone(output_path)
        self.assertTrue(os.path.exists(output_path))
        
    def test_visualize_pollen_distribution(self):
        """测试花粉分布可视化函数"""
        prepared_df = pv.prepare_data_for_visualization(self.df)
        output_path = pv.visualize_pollen_distribution(prepared_df, output_dir=self.output_dir)
        self.assertIsNotNone(output_path)
        self.assertTrue(os.path.exists(output_path))
        
    def tearDown(self):
        """测试后的清理工作"""
        plt.close('all')  # 关闭所有图表

if __name__ == '__main__':
    unittest.main() 