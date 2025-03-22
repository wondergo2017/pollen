#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉地图示例脚本
直接使用map_visualization模块生成地图并启动服务
"""

import os
import sys
import pandas as pd
from datetime import datetime

# 添加项目根目录到系统路径
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.visualization.map_visualization import run_map_server

def main():
    """主函数"""
    print("=" * 60)
    print("花粉地图示例脚本")
    print("=" * 60)
    
    # 设置数据文件路径
    data_file = os.path.join(project_root, "data", "sample_pyecharts_map_data.csv")
    
    if not os.path.exists(data_file):
        print(f"错误: 数据文件不存在: {data_file}")
        print("请先生成样本数据文件")
        return 1
    
    # 启动地图服务
    print(f"数据文件: {data_file}")
    print("启动地图服务器...")
    
    try:
        # 运行地图服务器
        run_map_server(
            data_file,
            host="127.0.0.1",
            port=8095,
            debug=False,
            open_browser=False
        )
        return 0
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 