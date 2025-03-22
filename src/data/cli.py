#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据命令行工具
提供命令行接口，用于获取和处理花粉数据
"""

import argparse
from datetime import datetime, timedelta
import os
import sys
import pandas as pd

from .constants import CITIES, DEFAULT_CONFIG
from .crawler import filter_cities, scrape_cities_data
from .processor import process_pollen_data, save_data, create_sample_data

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

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="花粉数据爬虫工具")
    
    # 基本参数
    parser.add_argument("--city", "-c", nargs="+", help="需要爬取的城市代码，多个城市用空格分隔")
    parser.add_argument("--days", "-d", type=int, help="相对模式下，需要爬取的天数")
    parser.add_argument("--start", "-s", help="固定日期模式下，开始日期 (YYYY-MM-DD)")
    parser.add_argument("--end", "-e", help="固定日期模式下，结束日期 (YYYY-MM-DD)")
    parser.add_argument("--delay", type=int, help="请求之间的延迟时间（秒）")
    parser.add_argument("--format", "-f", choices=["csv", "excel"], help="输出文件格式")
    parser.add_argument("--prefix", "-p", help="输出文件名前缀")
    
    # 示例数据生成
    parser.add_argument("--sample", action="store_true", help="生成示例数据而不是爬取真实数据")
    parser.add_argument("--sample-cities", type=int, default=5, help="示例数据中的城市数量")
    parser.add_argument("--sample-days", type=int, default=30, help="示例数据中的天数")
    
    # 列出城市列表
    parser.add_argument("--list-cities", action="store_true", help="列出所有可用的城市")
    
    return parser.parse_args()

def list_available_cities():
    """列出所有可用的城市"""
    print_header("可用城市列表")
    print("{:<15} {:<10} {:<15}".format("城市代码", "城市名称", "城市ID"))
    print("-" * 40)
    
    for city in CITIES:
        print("{:<15} {:<10} {:<15}".format(city["en"], city["cn"], city["id"]))

def scrape_data(config):
    """使用配置爬取数据"""
    # 获取日期范围
    if config["USE_RELATIVE_DATES"]:
        # 使用相对日期
        now = datetime.now()
        end_date = now.strftime("%Y-%m-%d")
        start_date = (now - timedelta(days=config["DAYS_TO_FETCH"])).strftime("%Y-%m-%d")
    else:
        # 使用固定日期
        start_date = config["START_DATE"]
        end_date = config["END_DATE"]
    
    # 筛选要爬取的城市
    cities_to_scrape = filter_cities(CITIES, config["SELECTED_CITIES"])
    
    # 获取需要爬取的城市列表
    city_names = [city['cn'] for city in cities_to_scrape]
    
    # 如果没有指定城市（例如城市代码不正确），则直接爬取数据
    if not city_names:
        print("警告：未指定有效的城市代码，将爬取所有城市的数据")
        cities_to_scrape = CITIES
        city_names = [city['cn'] for city in cities_to_scrape]
    
    # 生成需要检查的日期列表
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    date_range = []
    current_dt = start_dt
    while current_dt <= end_dt:
        date_range.append(current_dt.strftime("%Y-%m-%d"))
        current_dt += timedelta(days=1)
    
    print(f"将检查从 {start_date} 到 {end_date} 的花粉等级数据，共 {len(date_range)} 天")
    
    # 数据文件路径
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # 查找所有可能的数据文件
    all_data_files = []
    
    # 查找通用数据文件
    pattern = f"{config['FILENAME_PREFIX']}_*.{config['OUTPUT_FORMAT'].lower()}"
    for filename in os.listdir(data_dir):
        if filename.startswith(f"{config['FILENAME_PREFIX']}_") and filename.endswith(f".{config['OUTPUT_FORMAT'].lower()}"):
            all_data_files.append(os.path.join(data_dir, filename))
    
    # 尝试从所有文件中读取数据
    all_data_df = None
    for file_path in all_data_files:
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                continue
            
            if all_data_df is None:
                all_data_df = df
            else:
                all_data_df = pd.concat([all_data_df, df], ignore_index=True)
        except Exception as e:
            print(f"读取文件 {file_path} 时出错：{str(e)}，将忽略此文件")
    
    # 如果没有读取到任何数据，则直接爬取
    if all_data_df is None or '日期' not in all_data_df.columns or '城市' not in all_data_df.columns or '花粉等级' not in all_data_df.columns:
        print("未在现有数据文件中找到有效的数据，将爬取所有数据")
        
        print_header("开始爬取花粉数据")
        
        # 爬取数据
        raw_data, successful_cities, failed_cities = scrape_cities_data(
            cities_to_scrape, start_date, end_date, config
        )
        
        if not raw_data:
            print("\n未获取到任何数据，程序退出")
            return
        
        # 处理数据
        df = process_pollen_data(raw_data)
        
        # 保存数据
        save_data(df, config)
        
        # 如果只获取了一个城市的数据，则额外保存该城市的单独文件
        if len(successful_cities) == 1:
            city_name = successful_cities[0]
            save_data(df, config, city_name)
        
        print_success("数据处理完成")
        return
    
    # 检查每个日期和城市的数据是否存在
    missing_data = []
    for date in date_range:
        date_data = all_data_df[all_data_df['日期'] == date]
        for city in city_names:
            city_date_data = date_data[date_data['城市'] == city]
            if len(city_date_data) == 0 or pd.isna(city_date_data['花粉等级']).all():
                missing_data.append((date, city))
    
    # 如果所有数据都存在，则不需要爬取
    if not missing_data:
        print_header("检测到数据已存在")
        print(f"在数据文件中已找到从 {start_date} 到 {end_date} 所有日期和城市的花粉等级数据")
        print("跳过爬取过程。")
        return
    
    # 打印缺失数据的信息
    missing_dates = sorted(list(set([date for date, _ in missing_data])))
    print_header("检测到数据不完整")
    print(f"在数据文件中缺少以下日期的花粉等级数据:")
    for date in missing_dates:
        missing_cities_for_date = [city for d, city in missing_data if d == date]
        print(f"  {date}: {len(missing_cities_for_date)}个城市缺少数据")
        if len(missing_cities_for_date) <= 10:  # 只显示少量城市时才列出城市名
            print(f"    缺少的城市: {', '.join(missing_cities_for_date)}")
    
    print("将爬取缺失的数据。")
    
    print_header("开始爬取花粉数据")
    
    # 爬取数据
    raw_data, successful_cities, failed_cities = scrape_cities_data(
        cities_to_scrape, start_date, end_date, config
    )
    
    if not raw_data:
        print("\n未获取到任何数据，程序退出")
        return
    
    # 处理数据
    df = process_pollen_data(raw_data)
    
    # 如果有现有数据，将新数据与现有数据合并
    if all_data_df is not None:
        print(f"将新爬取的数据与现有数据合并")
        
        # 确保两个DataFrame有相同的列
        required_columns = ['日期', '城市', '花粉等级', '等级描述', '颜色代码', '城市ID', '城市代码']
        
        # 只保留共同的列或必要的列
        common_columns = []
        for col in required_columns:
            if col in df.columns and col in all_data_df.columns:
                common_columns.append(col)
        
        # 筛选共同列
        df_filtered = df[common_columns]
        all_data_df_filtered = all_data_df[common_columns]
        
        # 将两个DataFrame合并
        combined_df = pd.concat([all_data_df_filtered, df_filtered], ignore_index=True)
        
        # 去除重复行
        combined_df = combined_df.drop_duplicates(subset=['日期', '城市'], keep='last')
        
        # 按日期和城市排序
        combined_df = combined_df.sort_values(['日期', '城市'])
        
        # 如果合并成功
        if not combined_df.empty:
            # 保存合并后的数据
            save_data(combined_df, config)
            print_success(f"合并后的数据包含 {len(combined_df)} 条记录")
        else:
            # 如果合并失败，则仅保存新数据
            save_data(df, config)
            print_success(f"未能合并数据，仅保存了新爬取的 {len(df)} 条记录")
    else:
        # 保存数据
        save_data(df, config)
    
    # 如果只获取了一个城市的数据，则额外保存该城市的单独文件
    if len(successful_cities) == 1:
        city_name = successful_cities[0]
        save_data(df, config, city_name)
    
    print_success("数据处理完成")

def main():
    """主函数，解析命令行参数并执行爬虫"""
    args = parse_arguments()
    
    # 列出城市列表
    if args.list_cities:
        list_available_cities()
        return
    
    # 生成示例数据
    if args.sample:
        sample_df = create_sample_data(args.sample_cities, args.sample_days)
        # 使用默认配置保存示例数据
        save_data(sample_df, DEFAULT_CONFIG)
        return
    
    # 配置爬虫参数
    config = DEFAULT_CONFIG.copy()
    
    # 更新配置
    if args.city:
        config["SELECTED_CITIES"] = args.city
    
    if args.days:
        config["DAYS_TO_FETCH"] = args.days
    
    if args.start and args.end:
        config["USE_RELATIVE_DATES"] = False
        config["START_DATE"] = args.start
        config["END_DATE"] = args.end
        print(f"使用固定日期模式: 从 {args.start} 到 {args.end}")
    elif args.start:
        # 当只提供start参数时，使用固定日期模式，结束日期设为当前日期
        config["USE_RELATIVE_DATES"] = False
        config["START_DATE"] = args.start
        config["END_DATE"] = datetime.now().strftime("%Y-%m-%d")
        print(f"使用固定日期模式: 从 {args.start} 到 {config['END_DATE']} (当前日期)")
    elif args.end:
        # 当只提供end参数时，使用固定日期模式，开始日期设为结束日期减去默认天数
        config["USE_RELATIVE_DATES"] = False
        end_date = datetime.strptime(args.end, "%Y-%m-%d")
        start_date = end_date - timedelta(days=config["DAYS_TO_FETCH"])
        config["START_DATE"] = start_date.strftime("%Y-%m-%d")
        config["END_DATE"] = args.end
        print(f"使用固定日期模式: 从 {config['START_DATE']} 到 {args.end} (基于默认天数: {config['DAYS_TO_FETCH']}天)")
    else:
        # 使用相对日期模式
        print(f"使用相对日期模式: 最近 {config['DAYS_TO_FETCH']} 天的数据")
    
    if args.delay:
        config["REQUEST_DELAY"] = args.delay
    
    if args.format:
        config["OUTPUT_FORMAT"] = args.format
        
    if args.prefix:
        config["FILENAME_PREFIX"] = args.prefix
    
    # 执行爬虫
    scrape_data(config)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断，程序退出")
    except Exception as e:
        print(f"\n程序执行出错: {str(e)}")
        import traceback
        traceback.print_exc() 