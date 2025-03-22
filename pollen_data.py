#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据爬虫工具
用于从中国天气网爬取花粉等级数据
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import sys
import argparse

# 城市列表
CITIES = [
    {"en": "beijing", "cn": "北京", "id": 101010100},
    {"en": "yinchuan", "cn": "银川", "id": 101170101},
    {"en": "lanzhou", "cn": "兰州", "id": 101160101},
    {"en": "changchun", "cn": "长春", "id": 101060101},
    {"en": "xian", "cn": "西安", "id": 101110101},
    {"en": "taiyuan", "cn": "太原", "id": 101100101},
    {"en": "shenyang", "cn": "沈阳", "id": 101070101},
    {"en": "wulumuqi", "cn": "乌鲁木齐", "id": 101130101},
    {"en": "huhehaote", "cn": "呼和浩特", "id": 101080101},
    {"en": "liaocheng", "cn": "聊城", "id": 101121701},
    {"en": "zibo", "cn": "淄博", "id": 101120301},
    {"en": "chengde", "cn": "承德", "id": 101090402},
    {"en": "baotou", "cn": "包头", "id": 101080201},
    {"en": "eerduosi", "cn": "鄂尔多斯", "id": 101080701},
    {"en": "haerbin", "cn": "哈尔滨", "id": 101050101},
    {"en": "wulanhaote", "cn": "乌兰浩特", "id": 101081101},
    {"en": "haikou", "cn": "海口", "id": 101310101},
    {"en": "tianjin", "cn": "天津", "id": 101030100},
    {"en": "xining", "cn": "西宁", "id": 101150101},
    {"en": "cangzhou", "cn": "沧州", "id": 101090701},
    {"en": "chongqing", "cn": "重庆", "id": 101040100},
    {"en": "wuhan", "cn": "武汉", "id": 101200101},
    {"en": "shijiazhuang", "cn": "石家庄", "id": 101090101},
    {"en": "kunming", "cn": "昆明市", "id": 101290101},
    {"en": "botou", "cn": "泊头", "id": 101090711},
    {"en": "dalian", "cn": "大连", "id": 101070201},
    {"en": "jinan", "cn": "济南", "id": 101120101},
    {"en": "hangzhou", "cn": "杭州", "id": 101210101},
    {"en": "wuhai", "cn": "乌海市", "id": 101080301},
    {"en": "yantai", "cn": "烟台", "id": 101120501},
    {"en": "guangzhou", "cn": "广州", "id": 101280101},
    {"en": "baoding", "cn": "保定", "id": 101090201},
    {"en": "yangzhou", "cn": "扬州", "id": 101190601},
    {"en": "nanchong", "cn": "南充", "id": 101270501},
    {"en": "wuxi", "cn": "无锡", "id": 101190201},
    {"en": "fuzhou", "cn": "福州", "id": 101230101},
    {"en": "hefei", "cn": "合肥", "id": 101220101},
    {"en": "nanning", "cn": "南宁", "id": 101300101},
    {"en": "lasa", "cn": "拉萨", "id": 101140101},
    {"en": "guiyang", "cn": "贵阳", "id": 101260101},
    {"en": "nanchang", "cn": "南昌", "id": 101240101},
    {"en": "changsha", "cn": "长沙", "id": 101250101},
    {"en": "yanan", "cn": "延安", "id": 101110300},
    {"en": "liupanshui", "cn": "六盘水", "id": 101260803},
    {"en": "xianyang", "cn": "咸阳", "id": 101110200},
    {"en": "chengdu", "cn": "成都", "id": 101270101},
    {"en": "shanghai", "cn": "上海", "id": 101020100},
    {"en": "yulin", "cn": "榆林", "id": 101110401},
    {"en": "zhengzhou", "cn": "郑州", "id": 101180101}
]

# 默认配置
DEFAULT_CONFIG = {
    "USE_RELATIVE_DATES": True,
    "DAYS_TO_FETCH": 30,
    "START_DATE": "2023-03-01",
    "END_DATE": "2023-05-31",
    "REQUEST_DELAY": 2,
    "REQUEST_TIMEOUT": 10,
    "MAX_RETRIES": 3,
    "OUTPUT_FORMAT": "csv",
    "ADD_DATE_TO_FILENAME": True,
    "FILENAME_PREFIX": "pollen_data",
    "OUTPUT_ENCODING": "utf-8-sig",
    "SELECTED_CITIES": []
}

def get_pollen_data(city_info, start_date, end_date, config, retry_count=0):
    """
    获取指定城市的花粉数据
    
    参数:
    - city_info: 城市信息字典
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    - config: 配置字典
    - retry_count: 当前重试次数
    
    返回:
    - 花粉数据列表
    """
    url = f"https://graph.weatherdt.com/ty/pollen/v2/hfindex.html"
    params = {
        "eletype": 1,
        "city": city_info["en"],
        "start": start_date,
        "end": end_date,
        "predictFlag": "true"
    }
    
    # 更全面的请求头，模拟浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Referer": "https://www.weather.com.cn/forecast/hf_index.shtml?id=101010100",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Host": "graph.weatherdt.com"
    }
    
    try:
        response = requests.get(
            url, 
            params=params, 
            headers=headers, 
            timeout=config["REQUEST_TIMEOUT"]
        )
        
        # 响应内容不是标准的JSON格式，需要处理
        if response.status_code == 200:
            # 尝试直接解析为JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                # 如果失败，尝试手动解析文本
                text = response.text
                if text.startswith("(") and text.endswith(")"):
                    text = text[1:-1]  # 移除括号
                
                try:
                    data = json.loads(text)
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {str(e)}")
                    return []
            
            # 根据实际返回数据结构调整 - 使用'dataList'字段而非'data'
            if "dataList" in data:
                print(f"成功获取 {city_info['cn']} 的花粉数据，共 {len(data['dataList'])} 条记录")
                return data["dataList"]
            else:
                print(f"数据格式错误，缺少'dataList'字段")
                return []
        else:
            print(f"请求失败: {response.status_code}")
            
            # 如果请求失败并且未超过最大重试次数，则重试
            if retry_count < config["MAX_RETRIES"]:
                retry_count += 1
                print(f"正在进行第 {retry_count} 次重试...")
                time.sleep(config["REQUEST_DELAY"] * 2)  # 重试前等待更长时间
                return get_pollen_data(city_info, start_date, end_date, config, retry_count)
            
            return []
    except Exception as e:
        print(f"获取 {city_info['cn']} 的花粉数据时出错: {str(e)}")
        
        # 如果请求出错并且未超过最大重试次数，则重试
        if retry_count < config["MAX_RETRIES"]:
            retry_count += 1
            print(f"正在进行第 {retry_count} 次重试...")
            time.sleep(config["REQUEST_DELAY"] * 2)  # 重试前等待更长时间
            return get_pollen_data(city_info, start_date, end_date, config, retry_count)
            
        return []

def save_data(df, config):
    """保存数据到文件"""
    now = datetime.now().strftime("%Y-%m-%d")
    
    if config["ADD_DATE_TO_FILENAME"]:
        base_filename = f"{config['FILENAME_PREFIX']}_{now}"
    else:
        base_filename = config["FILENAME_PREFIX"]
    
    if config["OUTPUT_FORMAT"].lower() == "csv":
        filename = f"{base_filename}.csv"
        df.to_csv(filename, index=False, encoding=config["OUTPUT_ENCODING"])
    elif config["OUTPUT_FORMAT"].lower() == "excel":
        filename = f"{base_filename}.xlsx"
        df.to_excel(filename, index=False, engine="openpyxl")
    else:
        print(f"不支持的文件格式: {config['OUTPUT_FORMAT']}，将使用CSV格式")
        filename = f"{base_filename}.csv"
        df.to_csv(filename, index=False, encoding=config["OUTPUT_ENCODING"])
    
    print(f"\n成功将花粉数据保存到文件 {filename}")
    return filename

def filter_cities(cities_list, selected_cities):
    """根据配置筛选城市"""
    if not selected_cities:
        return cities_list
    
    return [city for city in cities_list if city["en"] in selected_cities]

def get_city_name(city_code):
    """根据城市代码获取城市中文名"""
    for city in CITIES:
        if city["en"] == city_code:
            return city["cn"]
    return None

def get_city_by_name(city_name):
    """根据城市中文名获取城市信息"""
    for city in CITIES:
        if city["cn"] == city_name:
            return city
    return None

def create_sample_data(num_cities=5, num_days=30):
    """创建示例数据，用于测试和演示"""
    import random
    from datetime import datetime, timedelta
    
    print(f"生成 {num_cities} 个城市 {num_days} 天的示例数据...")
    
    # 选择城市
    selected_cities = random.sample(CITIES, min(num_cities, len(CITIES)))
    
    # 生成日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=num_days-1)
    
    # 花粉等级和颜色映射
    levels = ["未检测", "很低", "较低", "偏高", "较高", "很高", "极高"]
    colors = ["#999999", "#81CB31", "#A1FF3D", "#F5EE32", "#FFAF13", "#FF2319", "#AD075D"]
    level_msgs = [
        "无花粉",
        "不易引发过敏反应",
        "对极敏感人群可能引发过敏反应",
        "易引发过敏，加强防护，对症用药",
        "易引发过敏，加强防护，规范用药",
        "极易引发过敏，减少外出，持续规范用药",
        "极易引发过敏，建议足不出户，规范用药"
    ]
    
    # 生成数据
    data = []
    for city in selected_cities:
        current_date = start_date
        while current_date <= end_date:
            # 随机生成花粉等级，稍微偏向于低等级
            level_idx = min(random.choices(range(7), weights=[1, 3, 3, 2, 2, 1, 0.5])[0], 6)
            level = levels[level_idx]
            
            # 生成一条记录
            record = {
                "city": city["cn"],
                "city_id": city["id"],
                "cityCode": city["en"],
                "addTime": current_date.strftime("%Y-%m-%d"),
                "week": current_date.strftime("%A"),  # 星期
                "level": level,
                "levelCode": level_idx,
                "color": colors[level_idx],
                "elenum": random.randint(1, 100),  # 随机花粉数量
                "levelMsg": level_msgs[level_idx]
            }
            data.append(record)
            
            # 下一天
            current_date += timedelta(days=1)
    
    # 转换为DataFrame
    df = pd.DataFrame(data)
    
    # 保存数据
    sample_filename = "sample_pollen_data.csv"
    df.to_csv(sample_filename, index=False, encoding="utf-8-sig")
    print(f"示例数据已保存到 {sample_filename}")
    
    return df, sample_filename

def scrape_data(config=None):
    """爬取花粉数据的主函数"""
    # 使用传入的配置或默认配置
    if config is None:
        config = DEFAULT_CONFIG
    
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
    
    print(f"开始爬取花粉数据，日期范围: {start_date} 至 {end_date}")
    
    # 筛选要爬取的城市
    cities_to_scrape = filter_cities(CITIES, config["SELECTED_CITIES"])
    print(f"共需爬取 {len(cities_to_scrape)} 个城市的数据")
    
    # 存储所有数据的列表
    all_data = []
    
    # 记录成功和失败的城市
    successful_cities = []
    failed_cities = []
    
    # 遍历所有城市
    for i, city in enumerate(cities_to_scrape):
        city_name = city['cn']
        city_code = city['en']
        city_id = city['id']
        
        print(f"\n[{i+1}/{len(cities_to_scrape)}] 正在获取 {city_name} 的花粉数据...")
        city_data = get_pollen_data(city, start_date, end_date, config)
        
        if city_data:
            # 添加城市信息到每条记录
            for item in city_data:
                item["city"] = city_name
                item["city_id"] = city_id
                item["cityCode"] = city_code
            
            all_data.extend(city_data)
            successful_cities.append(city_name)
        else:
            failed_cities.append(city_name)
        
        # 添加延迟，避免请求频率过高
        if i < len(cities_to_scrape) - 1:  # 不需要在最后一个城市后等待
            print(f"等待 {config['REQUEST_DELAY']} 秒...")
            time.sleep(config["REQUEST_DELAY"])
    
    # 处理爬取结果
    if all_data:
        df = pd.DataFrame(all_data)
        print(f"\n成功爬取 {len(successful_cities)} 个城市的花粉数据，共 {len(df)} 条记录")
        
        # 保存数据
        filename = save_data(df, config)
        
        # 输出爬取统计
        print("\n爬取统计:")
        print(f"- 成功: {len(successful_cities)} 个城市")
        print(f"- 失败: {len(failed_cities)} 个城市")
        if failed_cities:
            print(f"- 失败城市列表: {', '.join(failed_cities)}")
        
        return df, filename
    else:
        print("\n未能获取任何数据，请检查网络连接和城市配置")
        return None, None

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='花粉数据爬虫工具')
    parser.add_argument('--city', nargs='+', help='要爬取的城市英文代码 (例如: beijing shanghai)')
    parser.add_argument('--days', type=int, default=30, help='爬取过去多少天的数据 (默认: 30)')
    parser.add_argument('--start', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--delay', type=float, default=2, help='请求间隔时间(秒) (默认: 2)')
    parser.add_argument('--format', choices=['csv', 'excel'], default='csv', help='输出格式 (默认: csv)')
    parser.add_argument('--prefix', default='pollen_data', help='输出文件名前缀 (默认: pollen_data)')
    parser.add_argument('--sample', action='store_true', help='生成示例数据而不是爬取')
    parser.add_argument('--sample-cities', type=int, default=5, help='示例数据中的城市数量 (默认: 5)')
    parser.add_argument('--sample-days', type=int, default=30, help='示例数据中的天数 (默认: 30)')
    
    return parser.parse_args()

def main():
    """主函数，解析命令行参数并执行爬虫"""
    args = parse_arguments()
    
    # 生成示例数据
    if args.sample:
        create_sample_data(args.sample_cities, args.sample_days)
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