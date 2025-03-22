#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据命令行工具
提供简单的命令行接口，用于获取和处理花粉数据，并将结果保存到固定文件
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import traceback
import pandas as pd
import time

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入数据模块
from src.data.constants import DEFAULT_CONFIG, CITIES
from src.data.crawler import filter_cities, scrape_cities_data, get_pollen_data
from src.data.processor import process_pollen_data, save_data, create_sample_data

# 固定数据文件路径
DEFAULT_OUTPUT_FILE = "data/pollen_data_latest.csv"

def print_color(text, color_code):
    """使用ANSI颜色代码打印彩色文本"""
    print(f"\033[{color_code}m{text}\033[0m")

def print_success(text):
    """打印成功消息"""
    print_color(f"✓ {text}", "1;32")  # 绿色加粗

def print_error(text):
    """打印错误消息"""
    print_color(f"✗ {text}", "1;31")  # 红色加粗

def print_warning(text):
    """打印警告消息"""
    print_color(f"! {text}", "1;33")  # 黄色加粗

def print_info(text):
    """打印信息消息"""
    print_color(f"i {text}", "1;36")  # 青色加粗

def load_existing_data(output_file):
    """
    加载已有的数据文件
    
    参数:
        output_file: 输出文件路径
    
    返回:
        DataFrame 或 None (如果文件不存在或读取失败)
    """
    if not os.path.exists(output_file):
        print_info(f"数据文件 {output_file} 不存在，将创建新文件")
        return None
    
    try:
        print_info(f"正在读取现有数据文件: {output_file}")
        df = pd.read_csv(output_file, encoding='utf-8')
        
        # 检查必要的列是否存在
        required_cols = ['日期', '城市']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print_warning(f"现有数据文件缺少必要的列: {', '.join(missing_cols)}，将视为无效数据")
            return None
        
        print_success(f"成功读取现有数据: {len(df)} 条记录")
        return df
    except Exception as e:
        print_warning(f"读取现有数据文件出错: {str(e)}，将创建新文件")
        return None

def get_cities_dates_to_fetch(existing_df, cities_to_fetch, start_date, end_date):
    """
    确定需要爬取的城市和日期
    
    参数:
        existing_df: 现有数据 DataFrame
        cities_to_fetch: 要爬取的城市列表
        start_date: 开始日期字符串
        end_date: 结束日期字符串
    
    返回:
        需要爬取的城市和日期组合字典 {城市: [缺失的日期列表]}
    """
    if existing_df is None or existing_df.empty:
        # 如果没有现有数据，则所有城市和日期都需要爬取
        print_info("没有现有数据，将爬取所有城市和日期的数据")
        fetch_all = {}
        
        # 生成日期范围
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        date_range = [(start_dt + timedelta(days=i)).strftime('%Y-%m-%d')
                     for i in range((end_dt - start_dt).days + 1)]
        
        for city in cities_to_fetch:
            fetch_all[city['cn']] = {
                'info': city,
                'dates': date_range
            }
        return fetch_all
    
    # 转换日期类型确保一致性
    existing_df['日期'] = pd.to_datetime(existing_df['日期']).dt.strftime('%Y-%m-%d')
    
    # 生成完整的日期范围
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    all_dates = [(start_dt + timedelta(days=i)).strftime('%Y-%m-%d')
                 for i in range((end_dt - start_dt).days + 1)]
    
    # 存储需要爬取的城市和日期
    to_fetch = {}
    
    for city in cities_to_fetch:
        city_name = city['cn']
        
        # 获取此城市现有的日期数据
        city_data = existing_df[existing_df['城市'] == city_name]
        existing_dates = set(city_data['日期'].tolist())
        
        # 计算缺失的日期
        missing_dates = [date for date in all_dates if date not in existing_dates]
        
        if missing_dates:
            print_info(f"城市 {city_name} 缺少 {len(missing_dates)}/{len(all_dates)} 天的数据")
            to_fetch[city_name] = {
                'info': city,
                'dates': missing_dates
            }
        else:
            print_success(f"城市 {city_name} 的数据已完整 ({len(existing_dates)} 天)")
    
    return to_fetch

def fetch_missing_data(to_fetch, config):
    """
    爬取缺失的数据
    
    参数:
        to_fetch: 需要爬取的城市和日期 {城市: {info: 城市信息, dates: 日期列表}}
        config: 配置字典
    
    返回:
        爬取的数据列表
    """
    if not to_fetch:
        print_success("所有城市的数据均已是最新，无需爬取")
        return []
    
    # 总共需要爬取的城市数和日期数
    total_cities = len(to_fetch)
    total_dates = sum(len(city_data['dates']) for city_data in to_fetch.values())
    
    print_info(f"\n需要爬取 {total_cities} 个城市共 {total_dates} 天的缺失数据")
    
    # 存储所有爬取的数据
    all_data = []
    successful_cities = []
    failed_cities = []
    
    # 爬取每个城市的缺失数据
    for i, (city_name, city_data) in enumerate(to_fetch.items()):
        city_info = city_data['info']
        missing_dates = city_data['dates']
        
        # 如果日期范围连续，可以一次性爬取
        if len(missing_dates) > 1 and (datetime.strptime(missing_dates[-1], '%Y-%m-%d') - 
                                       datetime.strptime(missing_dates[0], '%Y-%m-%d')).days + 1 == len(missing_dates):
            # 日期是连续的，一次爬取
            print_info(f"\n[{i+1}/{total_cities}] 爬取 {city_name} 的连续日期数据: {missing_dates[0]} 至 {missing_dates[-1]}")
            city_data = get_pollen_data(city_info, missing_dates[0], missing_dates[-1], config)
            
            if city_data:
                # 添加额外的城市信息
                for item in city_data:
                    item["city_id"] = city_info['id']
                    item["city_name"] = city_name
                    item["city_code"] = city_info['en']
                
                all_data.extend(city_data)
                successful_cities.append(city_name)
                print_success(f"成功获取 {city_name} 的 {len(city_data)} 条记录")
            else:
                failed_cities.append(city_name)
                print_error(f"获取 {city_name} 的数据失败")
        else:
            # 日期不连续，分别爬取
            city_success = False
            city_data_count = 0
            
            for date in missing_dates:
                print_info(f"\n[{i+1}/{total_cities}] 爬取 {city_name} 的单日数据: {date}")
                date_data = get_pollen_data(city_info, date, date, config)
                
                if date_data:
                    # 添加额外的城市信息
                    for item in date_data:
                        item["city_id"] = city_info['id']
                        item["city_name"] = city_name
                        item["city_code"] = city_info['en']
                    
                    all_data.extend(date_data)
                    city_success = True
                    city_data_count += len(date_data)
                    print_success(f"成功获取 {city_name} 的 {date} 数据: {len(date_data)} 条记录")
                else:
                    print_error(f"获取 {city_name} 的 {date} 数据失败")
                
                # 添加延迟，避免请求频率过高
                if date != missing_dates[-1]:  # 不需要在最后一个日期后等待
                    print_info(f"等待 {config['REQUEST_DELAY']} 秒后继续...")
                    time.sleep(config['REQUEST_DELAY'])
            
            if city_success:
                successful_cities.append(city_name)
                print_success(f"成功获取 {city_name} 的总计 {city_data_count} 条记录")
            else:
                failed_cities.append(city_name)
                print_error(f"获取 {city_name} 的所有数据均失败")
        
        # 城市间添加延迟
        if i < total_cities - 1:  # 不需要在最后一个城市后等待
            print_info(f"等待 {config['REQUEST_DELAY']} 秒后继续爬取下一个城市...")
            time.sleep(config['REQUEST_DELAY'])
    
    # 打印爬取结果摘要
    print_info("\n爬取完成！")
    print_info(f"成功爬取 {len(successful_cities)}/{total_cities} 个城市的数据")
    
    if failed_cities:
        print_warning(f"以下城市爬取失败: {', '.join(failed_cities)}")
    
    if all_data:
        print_success(f"共获取 {len(all_data)} 条花粉数据记录")
    else:
        print_warning("未获取到任何新数据")
    
    return all_data

def fetch_data(output_file=DEFAULT_OUTPUT_FILE, use_sample=False, days=7, cities=None):
    """
    爬取或生成花粉数据并保存到固定文件
    
    参数:
        output_file: 输出文件路径
        use_sample: 是否使用示例数据
        days: 爬取的天数
        cities: 指定城市列表，为None时使用默认配置
    
    返回:
        成功返回True，失败返回False
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        config = DEFAULT_CONFIG.copy()
        
        # 添加all_cities键，用于城市过滤
        config['all_cities'] = CITIES
        
        # 确保days参数有效
        if days is None or days <= 0:
            days = 7
            print_warning(f"警告: 使用默认天数 {days} 天")
        
        # 更新配置
        config['DAYS_TO_FETCH'] = days
        print_info(f"设置爬取天数: {days} 天")
        
        if cities:
            config['SELECTED_CITIES'] = cities
        elif not config['SELECTED_CITIES']:
            # 如果没有指定城市，默认使用所有城市
            config['SELECTED_CITIES'] = [city['en'] for city in CITIES]
        
        # 设置输出文件
        config['output_file'] = output_file
        config['format'] = 'csv'
        
        print_info(f"将数据保存到文件: {output_file}")
        
        if use_sample:
            # 生成示例数据
            print_info("生成示例数据...")
            sample_data = create_sample_data(
                num_cities=config.get('sample_cities', 10),
                num_days=config.get('sample_days', 30)
            )
            
            # 保存示例数据到CSV文件
            sample_data.to_csv(output_file, index=False, encoding='utf-8')
            print_success(f"示例数据已保存到: {output_file}")
            return True
            
        else:
            # 爬取真实数据
            print_info("开始爬取花粉数据...")
            
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days-1)  # 调整为包含今天在内的天数
            
            # 格式化日期为字符串
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # 保存到配置
            config['start_date'] = start_date_str
            config['end_date'] = end_date_str
            
            print_info(f"爬取日期范围: {start_date_str} 至 {end_date_str} (共 {days} 天)")
            
            # 过滤城市
            selected_cities = config['SELECTED_CITIES']
            filtered_cities = filter_cities(config['all_cities'], selected_cities)
            
            if not filtered_cities:
                print_error("没有匹配的城市！")
                return False
            
            # 加载现有数据
            existing_data = load_existing_data(output_file)
            
            # 确定需要爬取的城市和日期
            to_fetch = get_cities_dates_to_fetch(existing_data, filtered_cities, start_date_str, end_date_str)
            
            # 爬取缺失的数据
            if to_fetch:
                raw_data = fetch_missing_data(to_fetch, config)
                
                # 处理新爬取的数据
                if raw_data:
                    processed_new_data = process_pollen_data(raw_data)
                    
                    if processed_new_data is not None and not processed_new_data.empty:
                        # 合并新数据和现有数据
                        if existing_data is not None and not existing_data.empty:
                            # 确保列名一致性
                            common_cols = list(set(existing_data.columns) & set(processed_new_data.columns))
                            if common_cols:
                                combined_data = pd.concat([
                                    existing_data[common_cols], 
                                    processed_new_data[common_cols]
                                ]).drop_duplicates(['日期', '城市']).reset_index(drop=True)
                            else:
                                print_warning("新旧数据列不匹配，将只保存新数据")
                                combined_data = processed_new_data
                        else:
                            combined_data = processed_new_data
                        
                        # 保存合并后的数据
                        combined_data.to_csv(output_file, index=False, encoding='utf-8')
                        print_success(f"数据已保存到: {output_file}")
                        print_success(f"总计保存记录数: {len(combined_data)} 条 (新增: {len(processed_new_data)} 条)")
                    else:
                        print_error("新爬取的数据处理失败！")
                        if existing_data is not None and not existing_data.empty:
                            print_warning("保留现有数据不变")
                            return True
                        return False
                else:
                    print_warning("没有获取到新数据")
                    return True
            else:
                print_success("所有数据都是最新的，无需更新")
                return True
        
        return True
        
    except Exception as e:
        print_error(f"数据获取失败: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="花粉数据爬取工具")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_FILE, help=f"输出文件路径 (默认: {DEFAULT_OUTPUT_FILE})")
    parser.add_argument("-s", "--sample", action="store_true", help="使用示例数据而不是爬取真实数据")
    parser.add_argument("-d", "--days", type=int, default=7, help="爬取的天数 (默认: 7)")
    parser.add_argument("-c", "--cities", nargs="+", help="需要爬取的城市代码，多个城市用空格分隔")
    parser.add_argument("-f", "--force", action="store_true", help="强制重新爬取所有数据，忽略已有数据")
    
    args = parser.parse_args()
    
    # 如果指定了强制重新爬取，则备份现有文件并创建新文件
    if args.force and os.path.exists(args.output) and not args.sample:
        backup_file = f"{args.output}.bak"
        try:
            os.rename(args.output, backup_file)
            print_info(f"已将现有数据文件备份为: {backup_file}")
        except Exception as e:
            print_warning(f"备份文件失败: {str(e)}，将直接覆盖现有文件")
    
    # 执行数据获取
    if fetch_data(args.output, args.sample, args.days, args.cities):
        return 0
    else:
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n用户中断，程序退出")
        sys.exit(130)
    except Exception as e:
        print_error(f"\n程序执行出错: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 