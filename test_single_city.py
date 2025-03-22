#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import pandas as pd
from datetime import datetime, timedelta

def get_pollen_data(city_name, city_code, start_date, end_date):
    """
    获取指定城市的花粉数据
    
    参数:
    - city_name: 城市中文名
    - city_code: 城市英文代码
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    
    返回:
    - 花粉数据列表
    """
    url = f"https://graph.weatherdt.com/ty/pollen/v2/hfindex.html"
    params = {
        "eletype": 1,
        "city": city_code,
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
        print(f"正在请求URL: {url}，参数: {params}")
        response = requests.get(url, params=params, headers=headers)
        print(f"响应状态码: {response.status_code}")
        
        # 添加响应头打印，用于调试
        print(f"响应头: {response.headers}")
        
        # 响应内容不是标准的JSON格式，需要处理
        if response.status_code == 200:
            # 打印响应内容前100个字符，方便调试
            print(f"响应内容前100个字符: {response.text[:100]}")
            
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
                    print(f"文本内容: {text}")
                    return []
            
            # 根据实际返回数据结构调整 - 使用'dataList'字段而非'data'
            if "dataList" in data:
                print(f"成功获取 {city_name} 的花粉数据，共 {len(data['dataList'])} 条记录")
                # 打印数据分级说明
                if "seasonLevel" in data:
                    print("\n花粉等级说明:")
                    for level in data["seasonLevel"]:
                        print(f"等级: {level.get('level', '未知')} - 颜色: {level.get('color', '未知')} - 描述: {level.get('desc', '无')} - 提示: {level.get('levelMsg', '无')}")
                return data["dataList"]
            else:
                print(f"数据格式错误，缺少'dataList'字段")
                print(f"数据内容: {data}")
                return []
        else:
            print(f"请求失败: {response.status_code}")
            # 打印响应文本以便调试
            print(f"响应文本: {response.text}")
            return []
    except Exception as e:
        print(f"获取 {city_name} 的花粉数据时出错: {str(e)}")
        return []

def main():
    # 获取当前日期
    now = datetime.now()
    end_date = now.strftime("%Y-%m-%d")
    
    # 调整日期范围，使用2023年的数据测试，因为当前可能是非花粉季节
    # 春季通常是花粉季节
    test_start_date = "2023-04-01"
    test_end_date = "2023-04-07"
    
    # 测试北京的花粉数据
    city_name = "北京"
    city_code = "beijing"
    
    print(f"测试获取 {city_name} 的花粉数据 (日期范围: {test_start_date} 至 {test_end_date})...")
    data = get_pollen_data(city_name, city_code, test_start_date, test_end_date)
    
    if data:
        # 转换为DataFrame并显示
        df = pd.DataFrame(data)
        
        # 选择要显示的列
        display_columns = ["city", "addTime", "week", "level", "color", "levelMsg"]
        # 确保所有列都存在于DataFrame中
        display_columns = [col for col in display_columns if col in df.columns]
        
        print("\n数据预览:")
        print(df[display_columns].head())
        
        # 保存到CSV文件
        filename = f"pollen_data_{city_name}_{end_date}.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"\n成功将花粉数据保存到文件 {filename}")
    else:
        print("未获取到任何花粉数据")

if __name__ == "__main__":
    main() 