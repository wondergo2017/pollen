#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据可视化命令行工具
这是一个简单的命令行工具，可以直接执行花粉数据可视化
"""

import os
import sys
import argparse
import pandas as pd

# 添加项目根目录到系统路径
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def print_color(text, color_code):
    """使用ANSI颜色代码打印彩色文本"""
    print(f"\033[{color_code}m{text}\033[0m")

def print_header(text):
    """打印带有装饰的标题"""
    print("\n" + "=" * 60)
    print_color(f" {text}", "1;34")  # 蓝色加粗
    print("=" * 60)

def print_success(text):
    """打印成功消息"""
    print_color(f"✓ {text}", "1;32")  # 绿色加粗

def print_warning(text):
    """打印警告消息"""
    print_color(f"! {text}", "1;33")  # 黄色加粗

def print_error(text):
    """打印错误消息"""
    print_color(f"✗ {text}", "1;31")  # 红色加粗

def print_step(text):
    """打印步骤消息"""
    print_color(f">> {text}", "1;36")  # 青色加粗

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="花粉数据可视化命令行工具")
    parser.add_argument("--data", "-d", help="指定数据文件路径")
    parser.add_argument("--output", "-o", help="指定输出目录")
    parser.add_argument("--cities", "-c", help="城市列表，用逗号分隔")
    parser.add_argument("--start", "-s", help="开始日期，格式为YYYY-MM-DD")
    parser.add_argument("--end", "-e", help="结束日期，格式为YYYY-MM-DD")
    parser.add_argument("--all", "-a", action="store_true", help="生成所有可视化图表")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")

    args = parser.parse_args()
    
    # 启用调试模式
    debug_mode = args.debug
    if debug_mode:
        import logging
        logging.basicConfig(level=logging.DEBUG, 
                           format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger()
        print_warning("调试模式已启用")

    # 导入可视化模块
    print_step("导入可视化模块...")
    try:
        from src.visualization import pollen_visualization as pv
        from src.config.visualization_config import (
            configure_matplotlib_fonts,
            get_default_data_dir,
            get_default_output_dir
        )
    except ImportError as e:
        print_error(f"导入模块失败: {e}")
        print_warning("请确保已安装所有依赖并且项目结构正确")
        sys.exit(1)

    # 配置matplotlib字体
    print_step("配置matplotlib字体...")
    configure_matplotlib_fonts()

    # 确定数据文件
    if args.data:
        data_file = args.data
    else:
        data_dir = get_default_data_dir()
        sample_file = os.path.join(data_dir, "sample_pollen_data.csv")
        if os.path.exists(sample_file):
            data_file = sample_file
            print_step(f"使用示例数据文件: {data_file}")
        else:
            # 如果没有指定数据文件且示例文件不存在，生成示例数据
            print_step("生成示例数据...")
            try:
                from examples.visualize_example import generate_sample_data
                data_file = generate_sample_data()
                print_success(f"已生成示例数据: {data_file}")
            except Exception as e:
                print_error(f"生成示例数据失败: {e}")
                sys.exit(1)

    # 确定输出目录
    output_dir = args.output if args.output else get_default_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    print_step(f"输出目录: {output_dir}")

    # 加载数据
    print_step(f"加载数据: {data_file}")
    try:
        df = pv.load_data(data_file)
        print_success(f"成功加载 {len(df)} 条记录")
    except Exception as e:
        print_error(f"加载数据失败: {e}")
        sys.exit(1)

    # 获取数据概览
    print_header("数据概览")
    print(f"城市列表: {', '.join(df['城市'].unique())}")
    print(f"日期范围: {df['日期'].min()} 至 {df['日期'].max()}")
    print(f"花粉等级范围: {df['花粉等级'].min()} 至 {df['花粉等级'].max()}")

    # 过滤数据
    if args.cities or args.start or args.end:
        print_step("根据条件过滤数据...")
        cities = args.cities.split(',') if args.cities else None
        start_date = args.start
        end_date = args.end
        
        df = pv.filter_data(df, cities=cities, start_date=start_date, end_date=end_date)
        print_success(f"过滤后剩余 {len(df)} 条记录")
        
        if cities:
            print(f"已选择城市: {', '.join(cities)}")
        if start_date:
            print(f"开始日期: {start_date}")
        if end_date:
            print(f"结束日期: {end_date}")

    # 准备数据
    print_step("准备数据...")
    prepared_df = pv.prepare_data_for_visualization(df)

    # 生成可视化
    print_header("生成可视化")
    
    try:
        if args.all:
            # 生成所有可视化
            print_step("生成所有可视化图表...")
            output_files = pv.generate_all_visualizations(prepared_df, output_dir=output_dir)
            
            print_success("所有可视化已完成！")
            print("\n生成的文件:")
            for file_path in output_files:
                print(f"- {file_path}")
        else:
            # 只生成基本可视化
            print_step("生成花粉趋势图...")
            try:
                trend_file = pv.visualize_pollen_trends(prepared_df, output_dir=output_dir)
                print_success(f"趋势图已保存: {trend_file}")
            except Exception as e:
                print_error(f"生成趋势图失败: {e}")
                if debug_mode:
                    import traceback
                    traceback.print_exc()
            
            print_step("生成花粉分布图...")
            try:
                dist_file = pv.visualize_pollen_distribution(prepared_df, output_dir=output_dir)
                print_success(f"分布图已保存: {dist_file}")
            except Exception as e:
                print_error(f"生成分布图失败: {e}")
                if debug_mode:
                    import traceback
                    traceback.print_exc()
    except Exception as e:
        print_error(f"生成可视化过程中出错: {e}")
        if debug_mode:
            import traceback
            traceback.print_exc()
    
    print_header("可视化完成")
    print(f"所有输出文件保存在: {output_dir}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n程序已被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 