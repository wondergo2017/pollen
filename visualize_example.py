#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta
import argparse
from pollen_visualization import visualize_pollen_trends

def generate_sample_data(num_cities=5, days=30):
    """生成示例花粉数据"""
    # 城市列表
    cities = [
        {"cn": "北京", "en": "beijing", "id": 101010100},
        {"cn": "上海", "en": "shanghai", "id": 101020100},
        {"cn": "广州", "en": "guangzhou", "id": 101280101},
        {"cn": "成都", "en": "chengdu", "id": 101270101},
        {"cn": "西安", "en": "xian", "id": 101110101},
        {"cn": "杭州", "en": "hangzhou", "id": 101210101},
        {"cn": "武汉", "en": "wuhan", "id": 101200101},
        {"cn": "南京", "en": "nanjing", "id": 101190101}
    ]
    
    # 选择城市
    selected_cities = cities[:min(num_cities, len(cities))]
    
    # 花粉等级和颜色
    levels = ["未检测", "很低", "较低", "偏高", "较高", "很高", "极高"]
    colors = ["#999999", "#81CB31", "#A1FF3D", "#F5EE32", "#FFAF13", "#FF2319", "#AD075D"]
    
    # 等级对应的提示信息
    level_msgs = {
        "未检测": "无花粉",
        "很低": "不易引发过敏反应。",
        "较低": "对极敏感人群可能引发过敏反应。",
        "偏高": "易引发过敏，加强防护，对症用药。",
        "较高": "易引发过敏，加强防护，规范用药。",
        "很高": "极易引发过敏，减少外出，持续规范用药。",
        "极高": "极易引发过敏，建议足不出户，规范用药。"
    }
    
    # 日期范围 (使用春季的日期，因为春季是花粉高发期)
    end_date = datetime(2023, 5, 15)
    start_date = end_date - timedelta(days=days-1)
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    
    # 生成数据
    data = []
    
    for city in selected_cities:
        # 为每个城市生成一个基本趋势
        # 春季通常是花粉逐渐升高然后下降的过程
        base_trend = np.concatenate([
            np.linspace(0, 4, days // 3),  # 前1/3时间花粉等级逐渐升高
            np.linspace(4, 5, days // 3),  # 中间1/3时间花粉等级维持高位
            np.linspace(5, 1, days - 2*(days // 3))  # 最后1/3时间花粉等级逐渐下降
        ])
        
        # 添加随机波动
        random_fluctuation = np.random.uniform(-0.5, 0.5, days)
        trend = base_trend + random_fluctuation
        
        # 确保值在有效范围内
        trend = np.clip(trend, 0, len(levels) - 1)
        
        # 生成每一天的记录
        for i, date in enumerate(date_range):
            # 确定当天的花粉等级
            level_idx = int(round(trend[i]))
            level = levels[level_idx]
            color = colors[level_idx]
            
            # 创建记录
            record = {
                "city": city["cn"],
                "cityCode": city["en"],
                "city_id": city["id"],
                "addTime": date.strftime("%Y-%m-%d"),
                "week": ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][date.weekday()],
                "level": level,
                "levelCode": level_idx,
                "color": color,
                "elenum": np.random.randint(1, 100),
                "levelMsg": level_msgs.get(level, ""),
                "eletype": "花粉"
            }
            
            data.append(record)
    
    # 转换为DataFrame
    df = pd.DataFrame(data)
    return df

def save_sample_data(df, output_file="sample_pollen_data.csv"):
    """保存示例数据到CSV文件"""
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"示例数据已保存到 {output_file}")
    return output_file

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='花粉等级数据可视化示例')
    parser.add_argument('--cities', type=int, default=5, help='要生成的城市数量')
    parser.add_argument('--days', type=int, default=30, help='要生成的天数')
    parser.add_argument('--data_file', help='已有的花粉数据文件路径')
    parser.add_argument('--output', help='输出图表文件名')
    parser.add_argument('--output_dir', default='visualization_output', help='输出目录')
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    # 如果提供了数据文件，使用该文件，否则生成示例数据
    if args.data_file and os.path.exists(args.data_file):
        print(f"使用已有的数据文件: {args.data_file}")
        df = pd.read_csv(args.data_file)
    else:
        print(f"生成示例数据 ({args.cities} 个城市, {args.days} 天)...")
        df = generate_sample_data(args.cities, args.days)
        save_sample_data(df, "sample_pollen_data.csv")
    
    # 确保日期列是日期时间类型
    if 'addTime' in df.columns:
        df['addTime'] = pd.to_datetime(df['addTime'])
    
    # 添加数值化等级列
    if 'level_numeric' not in df.columns and 'level' in df.columns:
        level_map = {
            "未检测": 0, "很低": 1, "较低": 2, "偏高": 3, 
            "较高": 4, "很高": 5, "极高": 6, "暂无": -1
        }
        df['level_numeric'] = df['level'].apply(lambda x: level_map.get(x, -1))
    
    # 可视化数据
    print("生成可视化图表...")
    output_path = visualize_pollen_trends(df, args.output_dir, args.output)
    print(f"可视化完成！图表已保存至: {output_path}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 