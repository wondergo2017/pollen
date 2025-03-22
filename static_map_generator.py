#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉分布静态地图生成器
生成可部署到GitHub Pages的静态HTML文件
"""

import os
import sys
import pandas as pd
import numpy as np
import argparse
import json
from datetime import datetime
from pyecharts import options as opts
from pyecharts.charts import Map, Geo, EffectScatter, Grid
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
import re

# 花粉等级定义
pollen_levels = [
    0, 2.5, 5.0, 7.5, 15, 30, 60, 90
]

# 城市坐标缓存
city_coordinates = {}

# 全局数据变量
available_dates = []
pollen_data = None

def load_city_coordinates():
    """加载城市坐标数据"""
    global city_coordinates
    try:
        # 尝试从项目中加载城市坐标数据
        # 这里假设城市坐标在同一目录下的city_coordinates.json文件中
        # 如果文件不存在，将使用一个空字典
        if os.path.exists('city_coordinates.json'):
            with open('city_coordinates.json', 'r', encoding='utf-8') as f:
                city_coordinates = json.load(f)
            print(f"已加载 {len(city_coordinates)} 个城市坐标")
        else:
            print("城市坐标文件不存在，将创建默认文件")
            # 默认坐标为空字典
            city_coordinates = {}
    except Exception as e:
        print(f"加载城市坐标时出错: {str(e)}")
        city_coordinates = {}

def get_city_coordinates(city_name):
    """获取城市坐标"""
    # 直接从缓存中获取
    if city_name in city_coordinates:
        return city_coordinates[city_name]
    
    # 如果找不到，返回None
    return None

def load_data(file_path):
    """加载花粉数据"""
    global available_dates
    global pollen_data
    
    try:
        print(f"正在加载数据文件: {file_path}")
        
        # 读取CSV数据
        df = pd.read_csv(file_path)
        
        # 确保日期列存在
        if '日期' not in df.columns:
            print("错误：数据文件缺少'日期'列")
            return False
        
        # 确保城市列存在
        if '城市' not in df.columns:
            print("错误：数据文件缺少'城市'列")
            return False
        
        # 确保花粉等级列存在
        if '花粉等级' not in df.columns:
            print("错误：数据文件缺少'花粉等级'列")
            return False
        
        # 转换日期格式
        try:
            df['日期'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"转换日期格式时出错: {str(e)}")
            return False
        
        # 提取可用日期
        available_dates = sorted(df['日期'].unique())
        
        print(f"发现 {len(available_dates)} 个可用日期")
        for date in available_dates[:5]:
            print(f"  - {date}")
        if len(available_dates) > 5:
            print(f"  ... 以及 {len(available_dates) - 5} 个其他日期")
        
        # 保存数据
        pollen_data = df
        
        return True
    except Exception as e:
        print(f"加载数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def filter_data_by_date(date_str):
    """按日期筛选数据"""
    if pollen_data is None:
        return None
    
    if date_str not in available_dates:
        print(f"错误：无效的日期 {date_str}")
        return None
    
    # 筛选指定日期的数据
    filtered_data = pollen_data[pollen_data['日期'] == date_str]
    
    print(f"为日期 {date_str} 筛选出 {len(filtered_data)} 条数据")
    
    return filtered_data

def create_map(date_str):
    """创建花粉分布地图"""
    # 获取该日期的数据
    data = filter_data_by_date(date_str)
    if data is None or len(data) == 0:
        print(f"错误：日期 {date_str} 没有可用数据")
        return None
    
    print(f"为日期 {date_str} 创建地图...")
    
    # 从数据中提取城市、省份和花粉值
    city_data = []  # 格式：[(城市, 花粉数值), ...]
    city_province_data = []  # 格式：[(城市, 省份, 花粉数值), ...]
    province_values = {}  # 按省份存储最大花粉值
    
    # 使用自定义CDN
    # 修改PyEcharts的JS_HOST配置，使用更可靠的CDN
    CUSTOM_JS_HOSTS = {
        "echarts": "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js",
        "china_js": "https://cdn.jsdelivr.net/npm/echarts@5/map/js/china.js"
    }
    
    for _, row in data.iterrows():
        city_name = row['城市']
        level = row['花粉等级']
        
        # 将花粉等级映射为数值
        if level == '暂无':
            level_value = 0
        elif level == '很低':
            level_value = 1
        elif level == '低':
            level_value = 2
        elif level == '较低':
            level_value = 3
        elif level == '中':
            level_value = 4
        elif level == '偏高':
            level_value = 5
        elif level == '高':
            level_value = 6
        elif level == '较高':
            level_value = 7
        elif level == '很高':
            level_value = 8
        elif level == '极高':
            level_value = 9
        else:
            level_value = 0
        
        # 简单处理：提取省份名（前两个字符）
        province_name = city_name[:2]
        if province_name.endswith(('市', '省', '区')):
            province_name = province_name[:-1]
        
        # 城市到省份的映射（完整映射请参考原代码）
        city_to_province = {
            '北京': '北京', '上海': '上海', '天津': '天津', '重庆': '重庆',
            # 这里只列举了部分城市-省份映射，完整版请参考原代码
        }
        
        # 如果城市在映射中，使用映射指定的省份
        if city_name in city_to_province:
            province_name = city_to_province[city_name]
        
        city_data.append((city_name, level_value))
        city_province_data.append((city_name, province_name, level_value))
    
    # 计算每个省份的最大花粉值
    for city, province, value in city_province_data:
        if province in province_values:
            province_values[province] = max(province_values[province], value)
        else:
            province_values[province] = value
    
    # 转换为地图所需格式
    province_data = [(province, value) for province, value in province_values.items()]
    
    print(f"已准备 {len(city_data)} 个城市的数据")
    for city, value in city_data[:5]:
        print(f"示例数据: 城市: {city}, 花粉数值: {value}")
    
    # 创建地图
    china_map = (
        Map(init_opts=opts.InitOpts(
            width="1000px", 
            height="800px", 
            theme=ThemeType.LIGHT,
            # 使用自定义CDN
            js_host="",  # 使用空字符串，因为我们会在HTML中直接指定JS文件
        ))
        .add(
            "花粉指数",  # 这是系列名称
            data_pair=[(p, 0) for p, _ in province_data],  # 所有省份使用相同的值
            maptype="china",
            is_roam=True,  # 允许缩放和平移
            label_opts=opts.LabelOpts(
                is_show=True,  # 显示省份名称
                font_size=10,
                color="#000000"
            ),
            itemstyle_opts=opts.ItemStyleOpts(
                color="#F7F7F7",  # 统一的浅灰色背景
                border_width=0.5,
                border_color="#DDDDDD",
            ),
            emphasis_itemstyle_opts=opts.ItemStyleOpts(
                border_width=1,
                border_color="#000000",
                opacity=0.9
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=False  # 不显示省份的悬浮提示
            )
        )
    )
    
    # 设置全局选项
    china_map.set_global_opts(
        title_opts=opts.TitleOpts(
            title="",  # 删除主标题
            subtitle="",  # 子标题已删除
            pos_left="center",
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=24,
                color="#333333"
            ),
            subtitle_textstyle_opts=opts.TextStyleOpts(
                font_size=16,
                color="#666666"
            )
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="item"
        )
    )
    
    # 创建散点图实例
    scatter = Geo(init_opts=opts.InitOpts(
        width="1000px", 
        height="800px",
        theme=ThemeType.LIGHT,
        js_host="",  # 使用空字符串，因为我们会在HTML中直接指定JS文件
    ))
    
    # 添加基础地图
    scatter.add_schema(
        maptype="china",
        itemstyle_opts=opts.ItemStyleOpts(
            color="rgba(255, 255, 255, 0)",  # 透明背景
            border_color="rgba(255, 255, 255, 0)",  # 透明边界
        ),
        label_opts=opts.LabelOpts(is_show=False)  # 不显示标签
    )
    
    # 颜色映射
    color_map = {
        0: "#C4A39F",  # 暂无
        1: "#81CB31",  # 很低
        2: "#A1FF3D",  # 低
        3: "#C9FF76",  # 较低
        4: "#F5EE32",  # 中
        5: "#FFD429",  # 偏高
        6: "#FF642E",  # 高
        7: "#FFAF13",  # 较高
        8: "#FF2319",  # 很高
        9: "#CC0000"   # 极高
    }
    
    # 等级文本映射
    level_map = {
        0: '暂无',
        1: '很低',
        2: '低',
        3: '较低',
        4: '中',
        5: '偏高',
        6: '高',
        7: '较高',
        8: '很高',
        9: '极高'
    }
    
    # 按等级分组城市数据
    level_data_dict = {}
    for city, province, value in city_province_data:
        if value not in level_data_dict:
            level_data_dict[value] = []
        level_data_dict[value].append((city, value))
    
    # 为每个等级创建散点图
    for level, data in level_data_dict.items():
        city_level_data = [(city, value) for city, value in data]
        # 添加散点
        scatter.add(
            series_name=level_map.get(level, '未知'),
            data_pair=city_level_data,
            symbol_size=18,  # 散点大小
            color=color_map.get(level, "#999999"),  # 散点颜色
            label_opts=opts.LabelOpts(
                is_show=False  # 不显示标签
            ),
            effect_opts=opts.EffectOpts(
                is_show=False  # 关闭涟漪效果
            ),
            tooltip_opts=opts.TooltipOpts(
                formatter=lambda params: (
                    f"{params.name}<br/>"
                    f"花粉等级: {level_map.get(params.value[2], '暂无')}"
                )
            )
        )
    
    # 添加图例
    scatter.set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            is_show=True,
            type_="piecewise",  # 使用分段型视觉映射
            pieces=[
                {"min": 0, "max": 0, "label": "暂无", "color": "#C4A39F"},
                {"min": 1, "max": 1, "label": "很低", "color": "#81CB31"},
                {"min": 2, "max": 2, "label": "低", "color": "#A1FF3D"},
                {"min": 3, "max": 3, "label": "较低", "color": "#C9FF76"},
                {"min": 4, "max": 4, "label": "中", "color": "#F5EE32"},
                {"min": 5, "max": 5, "label": "偏高", "color": "#FFD429"},
                {"min": 6, "max": 6, "label": "高", "color": "#FF642E"},
                {"min": 7, "max": 7, "label": "较高", "color": "#FFAF13"},
                {"min": 8, "max": 8, "label": "很高", "color": "#FF2319"},
                {"min": 9, "max": 9, "label": "极高", "color": "#CC0000"}
            ],
            pos_left="2%",  # 调整到左侧
            pos_top="middle",  # 垂直居中
            orient="vertical",  # 确保纵向显示
            item_width=20,
            item_height=15,  # 减小高度使图例更紧凑
            textstyle_opts=opts.TextStyleOpts(
                font_size=12,
                color="#333333"
            )
        )
    )
    
    # 合并地图和散点图
    from pyecharts.faker import Faker
    from pyecharts.charts import Grid
    
    # 创建网格布局
    grid = Grid(init_opts=opts.InitOpts(
        width="1000px", 
        height="800px",
        theme=ThemeType.LIGHT,
        js_host="",  # 使用空字符串，因为我们会在HTML中直接指定JS文件
    ))
    grid.add(china_map, grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_top="10%", pos_bottom="10%"))
    grid.add(scatter, grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_top="10%", pos_bottom="10%"))
    
    # 渲染地图
    # 修改输出HTML，使用自定义CDN
    html_content = grid.render_embed(template_name="simple_chart.html")
    
    # 替换CDN链接
    html_content = html_content.replace(
        '<script type="text/javascript" src="https://assets.pyecharts.org/assets/v5/echarts.min.js"></script>',
        f'<script type="text/javascript" src="{CUSTOM_JS_HOSTS["echarts"]}"></script>'
    )
    html_content = html_content.replace(
        '<script type="text/javascript" src="https://assets.pyecharts.org/assets/v5/maps/china.js"></script>',
        f'<script type="text/javascript" src="{CUSTOM_JS_HOSTS["china_js"]}"></script>'
    )
    
    # 添加页面标题
    html_content = html_content.replace(
        '<title>Awesome-pyecharts</title>',
        f'<title>全国花粉分布地图 - {date_str}</title>'
    )
    
    return html_content

def create_index_html(output_dir):
    """创建GitHub Pages适用的主页HTML"""
    index_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>花粉分布地图服务</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .controls {
            margin-bottom: 20px;
            text-align: center;
        }
        select, button {
            padding: 8px 16px;
            font-size: 16px;
            border-radius: 4px;
        }
        select {
            margin-right: 10px;
            border: 1px solid #ccc;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .map-container {
            margin-top: 20px;
            text-align: center;
        }
        iframe {
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 100%;
            height: 800px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>全国花粉分布地图服务</h1>
        <div class="controls">
            <select id="dateSelect">
"""
    
    # 添加日期选项
    for date in available_dates:
        index_content += f'                <option value="{date}">{date}</option>\n'
    
    index_content += """
            </select>
            <button onclick="updateMap()">查看地图</button>
        </div>
        <div class="map-container">
            <iframe id="mapFrame" src="maps/map_PLACEHOLDER.html" frameborder="0"></iframe>
        </div>
    </div>

    <script>
        function updateMap() {
            var date = document.getElementById('dateSelect').value;
            document.getElementById('mapFrame').src = 'maps/map_' + date + '.html';
        }
        
        // 初始化默认地图
        window.onload = function() {
            var defaultDate = document.getElementById('dateSelect').value;
            document.getElementById('mapFrame').src = 'maps/map_' + defaultDate + '.html';
        }
    </script>
</body>
</html>
"""
    
    # 替换占位符为第一个日期
    first_date = available_dates[0] if available_dates else "PLACEHOLDER"
    index_content = index_content.replace("PLACEHOLDER", first_date)
    
    # 写入index.html
    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"已创建主页: {index_path}")
    
    # 如果生成的index.html文件已经存在，检查是否需要修复iframe的src属性
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            index_html = f.read()
        
        # 检查iframe的src属性是否指向存在的地图文件
        iframe_src_match = re.search(r'<iframe id="mapFrame" src="maps/map_([^"]+)\.html"', index_html)
        if iframe_src_match:
            current_date = iframe_src_match.group(1)
            # 检查地图文件是否存在
            map_file = os.path.join(output_dir, f"maps/map_{current_date}.html")
            if not os.path.exists(map_file) and available_dates:
                # 如果文件不存在但有可用日期，修复iframe的src
                new_index_html = re.sub(
                    r'<iframe id="mapFrame" src="maps/map_[^"]+\.html"',
                    f'<iframe id="mapFrame" src="maps/map_{first_date}.html"',
                    index_html
                )
                # 保存修复后的index.html
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(new_index_html)
                print(f"已修复iframe src属性，指向首个可用日期: {first_date}")
    
    return index_path

def generate_static_maps(file_path, output_dir=None):
    """生成所有静态地图文件"""
    # 确保输出目录存在
    if output_dir is None:
        output_dir = "docs"
    
    print(f"输出目录: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建maps子目录
    maps_dir = os.path.join(output_dir, "maps")
    os.makedirs(maps_dir, exist_ok=True)
    
    # 加载城市坐标
    load_city_coordinates()
    
    # 加载数据
    if not load_data(file_path):
        print("加载数据失败，无法生成地图")
        return False
    
    # 生成主页
    create_index_html(output_dir)
    
    # 为每个日期生成地图
    generated_maps = []
    for date in available_dates:
        print(f"正在为日期 {date} 生成地图...")
        html_content = create_map(date)
        if html_content:
            # 渲染到HTML文件
            map_file_path = os.path.join(maps_dir, f"map_{date}.html")
            with open(map_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            generated_maps.append(map_file_path)
            print(f"已生成地图: {map_file_path}")
    
    print(f"已生成 {len(generated_maps)} 个地图文件")
    print("静态地图网站已准备就绪，可部署到GitHub Pages")
    print(f"本地预览: 打开 {os.path.join(output_dir, 'index.html')}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='花粉分布静态地图生成器')
    parser.add_argument('-f', '--file', required=True, help='花粉数据CSV文件路径')
    parser.add_argument('-o', '--output-dir', default='docs', help='输出目录路径 (默认: docs)')
    
    args = parser.parse_args()
    
    print("============================================================")
    print("花粉分布静态地图生成器")
    print("============================================================")
    print(f"数据文件: {args.file}")
    print(f"输出目录: {args.output_dir}")
    print("============================================================")
    
    # 生成静态地图
    try:
        generate_static_maps(
            file_path=args.file,
            output_dir=args.output_dir
        )
        return 0
    except Exception as e:
        print(f"生成静态地图时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 