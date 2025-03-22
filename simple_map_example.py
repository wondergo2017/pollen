#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单的花粉地图示例
直接使用PyEcharts生成地图并保存为HTML文件
"""

import os
import sys
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Map
from pyecharts.globals import ThemeType

# 添加项目根目录到系统路径
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 定义花粉等级
POLLEN_LEVELS = ["暂无", "很低", "低", "较低", "中", "偏高", "高", "较高", "很高", "极高"]

def load_data(file_path):
    """加载花粉数据"""
    data = pd.read_csv(file_path)
    if '日期' in data.columns:
        data['日期'] = pd.to_datetime(data['日期'])
    return data

def get_data_for_date(data, date_str=None):
    """获取指定日期的花粉数据"""
    if data is None or data.empty:
        return pd.DataFrame()
    
    # 获取最新日期
    if date_str is None and '日期' in data.columns:
        date_str = data['日期'].max().strftime('%Y-%m-%d')
    
    # 过滤指定日期的数据
    if date_str and '日期' in data.columns:
        date_obj = pd.to_datetime(date_str)
        filtered_data = data[data['日期'] == date_obj]
        return filtered_data
    
    return data

def create_map(data, output_file="pollen_map.html"):
    """创建花粉分布地图并保存为HTML文件"""
    # 准备地图数据 - 按省份聚合
    province_data = {}
    
    for _, row in data.iterrows():
        city_name = row['城市']
        level = row['花粉等级']
        
        # 将花粉等级映射为数值
        level_value = POLLEN_LEVELS.index(level) * 10 if level in POLLEN_LEVELS else 0
        
        # 提取省份名称（简单处理：取城市名前两个字符，如"北京市"取"北京"）
        province_name = city_name[:2]
        if province_name.endswith(('市', '省', '区')):
            province_name = province_name[:-1]
        
        # 更新省份数据（取同一省份中的最高等级）
        if province_name in province_data:
            if level_value > province_data[province_name]:
                province_data[province_name] = level_value
        else:
            province_data[province_name] = level_value
    
    # 转换为地图所需的数据格式
    map_data = [(province, value) for province, value in province_data.items()]
    
    # 创建地图实例
    map_chart = Map(init_opts=opts.InitOpts(
        width="1000px",  # 增加宽度
        height="800px",  # 增加高度
        theme=ThemeType.LIGHT,
        page_title="全国花粉分布地图"
    ))
    
    # 添加地图数据
    map_chart.add(
        series_name="花粉等级",
        data_pair=map_data,
        maptype="china",
        is_roam=True,  # 允许缩放和平移
        label_opts=opts.LabelOpts(
            is_show=True,  # 显示省份名称
            font_size=14,  # 增加字体大小
            color="#000000",  # 黑色字体
            position="inside"  # 在区域内显示
        ),
        itemstyle_opts=opts.ItemStyleOpts(
            border_width=2,  # 边框宽度
            border_color="#FFFFFF",  # 白色边框
            opacity=0.9  # 透明度
        ),
        emphasis_itemstyle_opts=opts.ItemStyleOpts(
            border_width=3,  # 鼠标悬停时边框更宽
            border_color="#000000",  # 黑色边框
            opacity=1.0  # 不透明
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="item",
            formatter="{b}<br/>花粉等级: {c}"
        )
    )
    
    # 设置全局选项
    map_chart.set_global_opts(
        title_opts=opts.TitleOpts(
            title="全国花粉分布地图",
            pos_left="center",
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=24,  # 增加标题字体大小
                color="#333333"
            )
        ),
        visualmap_opts=opts.VisualMapOpts(
            is_show=True,
            type_="color",
            min_=0,
            max_=90,
            range_text=["高花粉", "低花粉"],  # 更明确的文本
            pos_right="5%",
            pos_bottom="5%",
            item_width=40,  # 增加宽度
            item_height=250,  # 增加高度
            range_color=[
                "#81CB31", "#A1FF3D", "#F5EE32", 
                "#FFAF13", "#FF2319"
            ],
            textstyle_opts=opts.TextStyleOpts(
                font_size=14,  # 增加图例文字大小
                color="#333333"
            )
        )
    )
    
    # 保存为HTML文件
    map_chart.render(output_file)
    print(f"地图已保存至: {output_file}")
    
    return output_file

def main():
    """主函数"""
    print("=" * 60)
    print("简单的花粉地图示例")
    print("=" * 60)
    
    # 设置数据文件路径
    data_file = os.path.join(project_root, "data", "sample_pyecharts_map_data.csv")
    
    if not os.path.exists(data_file):
        print(f"错误: 数据文件不存在: {data_file}")
        return 1
    
    # 加载数据
    print(f"加载数据文件: {data_file}")
    data = load_data(data_file)
    
    # 获取最新日期的数据
    latest_date = data['日期'].max().strftime('%Y-%m-%d') if '日期' in data.columns else None
    print(f"使用日期: {latest_date or '所有日期'}")
    date_data = get_data_for_date(data, latest_date)
    
    # 创建地图
    output_file = os.path.join(project_root, "pollen_map.html")
    create_map(date_data, output_file)
    
    print("\n可以在浏览器中打开HTML文件查看地图:")
    print(f"file://{os.path.abspath(output_file)}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 