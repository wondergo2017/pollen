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