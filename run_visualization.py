#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据可视化运行脚本
此脚本提供了一种简单的方式来运行花粉数据可视化
"""

import os
import sys
import argparse
from datetime import datetime
import pandas as pd

# 检查必要的库是否已安装
try:
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("缺少必要的库。请安装以下库：")
    print("pip install matplotlib numpy pandas")
    sys.exit(1)

# 可选库检查
try:
    import seaborn as sns
    has_seaborn = True
except ImportError:
    has_seaborn = False
    print("提示: 安装seaborn库可以启用更多的可视化功能：")
    print("pip install seaborn")

# 配置matplotlib字体以支持中文
def configure_fonts():
    """配置matplotlib字体以支持中文"""
    try:
        # 尝试使用配置文件中的字体设置
        from visualization_config import configure_matplotlib_fonts
        if configure_matplotlib_fonts():
            print("成功配置matplotlib字体设置")
            return True
    except ImportError:
        pass
    
    # 如果导入失败，使用备用方法
    try:
        import matplotlib.font_manager as fm
        import warnings
        
        # 尝试寻找可用的中文字体
        chinese_fonts = [
            'SimHei', 'Microsoft YaHei', 'SimSun', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC',
            'Source Han Sans CN', 'Droid Sans Fallback', 'PingFang SC', 'STHeiti'
        ]
        
        latin_fonts = [
            'DejaVu Sans', 'Liberation Sans', 'Arial', 'Helvetica', 'Verdana', 'Tahoma'
        ]
        
        # 查找可用字体
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        # 先选择拉丁字符字体
        latin_font = next((font for font in latin_fonts if font in available_fonts), 'sans-serif')
        
        # 再选择中文字体
        cjk_font = next((font for font in chinese_fonts if font in available_fonts), None)
        
        # 设置matplotlib全局字体
        plt.rcParams['font.family'] = 'sans-serif'
        if cjk_font:
            plt.rcParams['font.sans-serif'] = [latin_font, cjk_font] + plt.rcParams['font.sans-serif']
            print(f"设置字体成功：主要字体 {latin_font}，中文字体 {cjk_font}")
        else:
            plt.rcParams['font.sans-serif'] = [latin_font] + plt.rcParams['font.sans-serif']
            print(f"设置字体成功：主要字体 {latin_font}，未找到支持中文的字体")
        
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
        # 关闭字体警告
        warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
        
        return True
    except Exception as e:
        print(f"字体配置失败: {str(e)}")
        return False

def check_visualization_module():
    """检查可视化模块是否可用"""
    try:
        import pollen_visualization
        return True
    except ImportError:
        print("错误: 找不到pollen_visualization模块。")
        print("请确保pollen_visualization.py文件在当前目录中。")
        return False

def find_data_files():
    """在当前目录中查找花粉数据文件"""
    data_files = []
    
    # 查找CSV文件
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            if all(col in df.columns for col in ['city', 'addTime', 'level']):
                data_files.append((csv_file, len(df), df['city'].nunique()))
        except:
            pass
    
    # 查找Excel文件
    excel_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls'))]
    for excel_file in excel_files:
        try:
            df = pd.read_excel(excel_file)
            if all(col in df.columns for col in ['city', 'addTime', 'level']):
                data_files.append((excel_file, len(df), df['city'].nunique()))
        except:
            pass
    
    return data_files

def display_available_data_files():
    """显示当前目录中可用的数据文件"""
    data_files = find_data_files()
    
    if not data_files:
        print("没有找到可用的花粉数据文件。")
        print("请确保CSV或Excel文件包含'city'、'addTime'和'level'列。")
        return None
    
    print("找到以下花粉数据文件:")
    for i, (file, records, cities) in enumerate(data_files, 1):
        print(f"{i}. {file} - {records}条记录, {cities}个城市")
    
    while True:
        try:
            choice = input("\n请选择要使用的文件 (输入序号，或按Enter使用第一个): ")
            if not choice:
                return data_files[0][0]
            
            choice = int(choice)
            if 1 <= choice <= len(data_files):
                return data_files[choice-1][0]
            else:
                print(f"无效选择，请输入1到{len(data_files)}之间的数字。")
        except ValueError:
            print("请输入有效的数字。")

def generate_sample_data():
    """生成示例数据（如果找不到现有数据）"""
    try:
        from visualize_example import generate_sample_data, save_sample_data
        print("正在生成示例数据...")
        df = generate_sample_data(num_cities=5, days=30)
        file_path = save_sample_data(df, "sample_pollen_data.csv")
        print(f"已生成示例数据文件: {file_path}")
        return file_path
    except ImportError:
        print("错误: 找不到示例数据生成模块。")
        print("将创建一个简单的示例数据文件...")
        
        # 创建一个简单的示例数据文件
        cities = ["北京", "上海", "广州", "成都", "西安"]
        levels = ["未检测", "很低", "较低", "偏高", "较高", "很高", "极高"]
        
        import random
        from datetime import datetime, timedelta
        
        data = []
        start_date = datetime.now() - timedelta(days=30)
        
        for city in cities:
            for i in range(30):
                date = start_date + timedelta(days=i)
                level = random.choice(levels)
                data.append({
                    "city": city,
                    "addTime": date.strftime("%Y-%m-%d"),
                    "level": level,
                })
        
        df = pd.DataFrame(data)
        file_path = "simple_sample_data.csv"
        df.to_csv(file_path, index=False)
        print(f"已创建简单示例数据: {file_path}")
        return file_path

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='花粉数据可视化运行工具')
    parser.add_argument('--data_file', help='花粉数据文件路径 (CSV或Excel格式)')
    parser.add_argument('--cities', nargs='+', help='要显示的城市列表 (例如: 北京 上海)')
    parser.add_argument('--start_date', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end_date', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--output', help='输出文件名')
    parser.add_argument('--output_dir', default='visualization_output', help='输出目录')
    parser.add_argument('--advanced', action='store_true', help='生成高级图表')
    parser.add_argument('--distribution', action='store_true', help='生成分布统计图表')
    parser.add_argument('--sample', action='store_true', help='使用示例数据')
    
    return parser.parse_args()

def interactive_setup():
    """交互式设置可视化参数"""
    params = {}
    
    # 1. 选择数据文件
    data_file = display_available_data_files()
    if not data_file:
        print("是否生成示例数据进行可视化？")
        if input("输入 'y' 确认, 任意键取消: ").lower() == 'y':
            data_file = generate_sample_data()
        else:
            print("未选择数据文件，退出程序。")
            sys.exit(0)
    
    params['data_file'] = data_file
    
    # 2. 加载数据文件以提供更多信息
    try:
        df = pd.read_csv(data_file) if data_file.endswith('.csv') else pd.read_excel(data_file)
        df['addTime'] = pd.to_datetime(df['addTime'])
        
        # 显示可用的城市
        available_cities = df['city'].unique().tolist()
        print(f"\n可用的城市 ({len(available_cities)}个): {', '.join(available_cities)}")
        
        # 允许选择城市
        city_input = input("请输入要显示的城市 (用空格分隔，或按Enter显示所有城市): ")
        if city_input:
            selected_cities = city_input.split()
            invalid_cities = [city for city in selected_cities if city not in available_cities]
            if invalid_cities:
                print(f"警告: 以下城市不在数据集中: {', '.join(invalid_cities)}")
                selected_cities = [city for city in selected_cities if city in available_cities]
            params['cities'] = selected_cities
        
        # 显示可用的日期范围
        min_date = df['addTime'].min().strftime('%Y-%m-%d')
        max_date = df['addTime'].max().strftime('%Y-%m-%d')
        print(f"\n数据日期范围: {min_date} 至 {max_date}")
        
        # 允许选择日期范围
        start_date = input(f"请输入开始日期 (YYYY-MM-DD，或按Enter使用 {min_date}): ")
        if start_date:
            params['start_date'] = start_date
        
        end_date = input(f"请输入结束日期 (YYYY-MM-DD，或按Enter使用 {max_date}): ")
        if end_date:
            params['end_date'] = end_date
        
    except Exception as e:
        print(f"警告: 读取数据文件时出错: {e}")
    
    # 3. 输出设置
    output_dir = input("请输入输出目录 (按Enter使用默认值 'visualization_output'): ")
    if output_dir:
        params['output_dir'] = output_dir
    
    # 4. 高级选项
    print("\n高级选项:")
    if has_seaborn and input("生成高级图表？(y/n，默认n): ").lower() == 'y':
        params['advanced'] = True
    
    if input("生成分布统计图？(y/n，默认n): ").lower() == 'y':
        params['distribution'] = True
    
    return params

def main():
    """主函数"""
    print("=" * 60)
    print("花粉数据可视化工具")
    print("=" * 60)
    
    # 配置字体
    configure_fonts()
    
    # 检查可视化模块
    if not check_visualization_module():
        sys.exit(1)
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 如果没有提供数据文件，进入交互模式
    if not args.data_file and not args.sample:
        print("\n进入交互模式...")
        params = interactive_setup()
    else:
        # 使用命令行参数
        params = vars(args)
        if args.sample:
            params['data_file'] = generate_sample_data()
    
    # 运行可视化
    try:
        import pollen_visualization as pv
        
        print("\n开始可视化...")
        
        # 加载数据
        df = pv.load_data(params['data_file'])
        print(f"已加载 {len(df)} 条记录，包含 {df['city'].nunique()} 个城市的数据。")
        
        # 过滤数据
        df = pv.filter_data(df, params.get('cities'), params.get('start_date'), params.get('end_date'))
        if len(df) == 0:
            print("过滤后没有剩余数据，请检查过滤条件。")
            return
        
        print(f"过滤后剩余 {len(df)} 条记录，包含 {df['city'].nunique()} 个城市的数据。")
        
        # 准备可视化数据
        df = pv.prepare_data_for_visualization(df)
        
        # 生成主趋势图
        output_path = pv.visualize_pollen_trends(df, params.get('output_dir', 'visualization_output'), params.get('output'))
        print(f"主趋势图已保存为: {output_path}")
        
        # 生成高级图表
        if params.get('advanced'):
            print("\n生成高级图表...")
            pv.create_advanced_charts(df, params.get('output_dir', 'visualization_output'))
        
        # 生成分布统计图
        if params.get('distribution'):
            print("\n生成分布统计图...")
            dist_path = pv.create_distribution_chart(df, params.get('output_dir', 'visualization_output'))
            print(f"分布统计图已保存为: {dist_path}")
        
        print("\n可视化完成！所有图表已保存至目录: {}".format(os.path.abspath(params.get('output_dir', 'visualization_output'))))
        
    except Exception as e:
        print(f"可视化过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
        sys.exit(0) 