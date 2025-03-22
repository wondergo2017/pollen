#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉可视化命令行工具
提供花粉数据可视化的命令行界面
"""

import os
import sys
import argparse
import traceback
from datetime import datetime

from src.visualization import (
    generate_trend_visualization,
    generate_distribution_visualization,
    generate_all_visualizations,
    get_available_cities,
    display_available_data_files,
    find_data_files
)

from src.config.visualization_config import (
    get_default_output_dir,
    get_default_data_dir
)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='花粉可视化工具')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 查看可用数据文件命令
    list_files_parser = subparsers.add_parser('list-files', help='列出可用的数据文件')
    list_files_parser.add_argument('-d', '--data-dir', help='数据目录路径')
    
    # 查看可用城市命令
    list_cities_parser = subparsers.add_parser('list-cities', help='列出可用的城市')
    list_cities_parser.add_argument('-f', '--file', help='数据文件路径')
    
    # 生成趋势图命令
    trend_parser = subparsers.add_parser('trend', help='生成花粉趋势图')
    trend_parser.add_argument('-f', '--file', help='数据文件路径')
    trend_parser.add_argument('-c', '--cities', help='城市列表，用逗号分隔', default=None)
    trend_parser.add_argument('-s', '--start-date', help='开始日期（格式：YYYY-MM-DD）')
    trend_parser.add_argument('-e', '--end-date', help='结束日期（格式：YYYY-MM-DD）')
    trend_parser.add_argument('-o', '--output-dir', help='输出目录路径')
    trend_parser.add_argument('-n', '--filename', help='输出文件名')
    
    # 生成分布图命令
    dist_parser = subparsers.add_parser('distribution', help='生成花粉分布图')
    dist_parser.add_argument('-f', '--file', help='数据文件路径')
    dist_parser.add_argument('-c', '--cities', help='城市列表，用逗号分隔', default=None)
    dist_parser.add_argument('-o', '--output-dir', help='输出目录路径')
    dist_parser.add_argument('-n', '--filename', help='输出文件名')
    
    # 生成所有图表命令
    all_parser = subparsers.add_parser('all', help='生成所有图表')
    all_parser.add_argument('-f', '--file', help='数据文件路径')
    all_parser.add_argument('-c', '--cities', help='城市列表，用逗号分隔', default=None)
    all_parser.add_argument('-s', '--start-date', help='开始日期（格式：YYYY-MM-DD）')
    all_parser.add_argument('-e', '--end-date', help='结束日期（格式：YYYY-MM-DD）')
    all_parser.add_argument('-o', '--output-dir', help='输出目录路径')
    
    return parser.parse_args()

def process_cities_arg(cities_arg):
    """处理城市参数"""
    if not cities_arg:
        return None
    return [city.strip() for city in cities_arg.split(',') if city.strip()]

def main():
    """主函数"""
    args = parse_args()
    
    # 如果没有指定命令，显示帮助信息
    if not args.command:
        print("错误：需要指定命令")
        print("使用 --help 查看帮助信息")
        return 1
    
    try:
        # 列出可用数据文件
        if args.command == 'list-files':
            data_dir = args.data_dir or get_default_data_dir()
            display_available_data_files(data_dir)
            return 0
        
        # 列出可用城市
        elif args.command == 'list-cities':
            cities = get_available_cities(args.file)
            if not cities:
                print("没有找到可用的城市")
                return 1
            
            print(f"找到 {len(cities)} 个城市:")
            for city in cities:
                print(f"  - {city}")
            return 0
        
        # 生成趋势图
        elif args.command == 'trend':
            cities = process_cities_arg(args.cities)
            output_file = generate_trend_visualization(
                data_file=args.file, 
                cities=cities, 
                start_date=args.start_date, 
                end_date=args.end_date, 
                output_dir=args.output_dir,
                filename=args.filename
            )
            print(f"趋势图已保存到：{output_file}")
            return 0
        
        # 生成分布图
        elif args.command == 'distribution':
            cities = process_cities_arg(args.cities)
            output_file = generate_distribution_visualization(
                data_file=args.file, 
                cities=cities, 
                output_dir=args.output_dir,
                filename=args.filename
            )
            print(f"分布图已保存到：{output_file}")
            return 0
        
        # 生成所有图表
        elif args.command == 'all':
            cities = process_cities_arg(args.cities)
            output_files = generate_all_visualizations(
                data_file=args.file, 
                cities=cities, 
                start_date=args.start_date, 
                end_date=args.end_date, 
                output_dir=args.output_dir
            )
            print(f"已生成 {len(output_files)} 个图表:")
            for file in output_files:
                print(f"  - {file}")
            return 0
        
    except Exception as e:
        print(f"错误: {str(e)}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 