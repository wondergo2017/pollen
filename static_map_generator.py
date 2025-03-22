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
import re
from datetime import datetime
from pyecharts import options as opts
from pyecharts.charts import Map, Geo, EffectScatter, Grid
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
import tempfile
import csv
import random
import shutil
from pathlib import Path

# 添加调试信息
print("脚本开始执行...")
print(f"命令行参数: {sys.argv}")

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
        script_dir = os.path.dirname(os.path.abspath(__file__))
        coord_file = os.path.join(script_dir, 'city_coordinates.json')
        
        if os.path.exists(coord_file):
            with open(coord_file, 'r', encoding='utf-8') as f:
                city_coordinates = json.load(f)
            print(f"已加载 {len(city_coordinates)} 个城市坐标")
        else:
            print("城市坐标文件不存在，将使用默认中国城市坐标")
            # 创建一个默认的坐标文件，仅包含基本城市坐标
            city_coordinates = {
                "北京": [116.407526, 39.90403],
                "上海": [121.473701, 31.230416],
                "广州": [113.264385, 23.129112],
                "深圳": [114.057868, 22.543099],
                "杭州": [120.15507, 30.274084],
                "南京": [118.796877, 32.060255],
                "武汉": [114.305393, 30.593099],
                "成都": [104.065735, 30.659462],
                "重庆": [106.551557, 29.563009],
                "西安": [108.946609, 34.347861],
                "天津": [117.190182, 39.125596],
                "苏州": [120.585315, 31.298886],
                "沈阳": [123.429092, 41.796768],
                "哈尔滨": [126.642464, 45.756967],
                "长春": [125.323544, 43.817072],
                "长沙": [112.938814, 28.228209],
                "福州": [119.306239, 26.075302],
                "郑州": [113.665412, 34.757975],
                "济南": [117.000923, 36.675807],
                "青岛": [120.379477, 36.066328]
            }
            # 保存基本坐标到文件
            with open(coord_file, 'w', encoding='utf-8') as f:
                json.dump(city_coordinates, f, ensure_ascii=False, indent=4)
            print(f"已创建默认城市坐标文件，包含 {len(city_coordinates)} 个城市")
    except Exception as e:
        print(f"加载城市坐标时出错: {str(e)}")
        city_coordinates = {}

def get_city_coordinates(city_name):
    """获取城市坐标"""
    # 直接从缓存中获取
    if city_name in city_coordinates:
        return city_coordinates[city_name]
    
    # 处理特殊情况
    if city_name.endswith(('市', '区', '县')):
        # 尝试去掉后缀
        short_name = city_name[:-1]
        if short_name in city_coordinates:
            return city_coordinates[short_name]
    
    # 如果是直辖市的某个区，直接使用直辖市的坐标
    for prefix in ['北京', '上海', '天津', '重庆']:
        if city_name.startswith(prefix) and prefix in city_coordinates:
            return city_coordinates[prefix]
    
    # 如果找不到，返回None
    print(f"警告: 无法找到城市 '{city_name}' 的坐标")
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
        
        # 过滤出2025年的日期
        df = df[df['日期'].str.startswith('2025')]
        if len(df) == 0:
            print("警告：数据中没有2025年的记录，将使用所有可用日期")
            # 如果没有2025年的记录，恢复使用原始数据
            df = pd.read_csv(file_path)
            df['日期'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        else:
            print("成功过滤出2025年的记录")
        
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
    try:
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
        
        for _, row in data.iterrows():
            city_name = row['城市']
            level = row['花粉等级']
            
            # 将花粉等级映射为数值
            level_map = {
                '暂无': 0, '很低': 1, '低': 2, '中': 3,
                '高': 4, '很高': 5, '极高': 6
            }
            level_value = level_map.get(level, 0)
            
            # 城市到省份的映射（与map_server_example.py保持一致）
            city_to_province = {
                '北京': '北京', '上海': '上海', '天津': '天津', '重庆': '重庆',
                '广州': '广东', '深圳': '广东', '杭州': '浙江', '南京': '江苏', 
                '武汉': '湖北', '成都': '四川', '西安': '陕西', '沈阳': '辽宁', 
                '哈尔滨': '黑龙江', '长春': '吉林', '长沙': '湖南', '福州': '福建', 
                '郑州': '河南', '济南': '山东', '青岛': '山东', '苏州': '江苏'
            }
            
            # 如果城市在映射中，使用映射指定的省份
            province_name = city_to_province.get(city_name)
            if not province_name:
                # 如果没有直接映射，尝试简单提取省份名
                province_name = city_name[:2]
                if province_name.endswith(('市', '省', '区')):
                    province_name = province_name[:-1]
            
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
        
        print("加载pyecharts库...")
        # 创建初始化选项 - 直接使用pyecharts
        from pyecharts import options as opts
        from pyecharts.charts import Map, Geo, Grid
        from pyecharts.globals import ThemeType
        from pyecharts.commons.utils import JsCode
        
        print("创建图表初始化选项...")
        init_opts = opts.InitOpts(
            width="100%", 
            height="600px",
            theme=ThemeType.LIGHT,
            page_title=f"全国花粉分布地图 - {date_str}",
            renderer="canvas"  # 使用canvas渲染器更适合交互
        )
        
        print("创建地图实例...")
        # 创建地图实例
        map_chart = Map(init_opts=init_opts)
        
        print("添加省份填充地图...")
        # 添加省份填充地图 - 设置为统一的浅灰色背景
        map_chart.add(
            series_name="",  # 使用空字符串作为系列名称，这样图例中不会显示省份
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
        
        print("设置地图全局选项...")
        # 设置全局选项 - 删除标题
        map_chart.set_global_opts(
            title_opts=opts.TitleOpts(
                title="",  # 删除标题
                subtitle="",
                pos_left="center"
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item"
            )
        )
        
        print("创建散点图实例...")
        # 创建散点图实例
        scatter = Geo(init_opts=init_opts)
        
        print("添加基础地图...")
        # 添加基础地图
        scatter.add_schema(
            maptype="china",
            itemstyle_opts=opts.ItemStyleOpts(
                color="rgba(255, 255, 255, 0)",  # 透明背景
                border_color="rgba(255, 255, 255, 0)",  # 透明边界
            ),
            label_opts=opts.LabelOpts(is_show=False)  # 不显示标签
        )
        
        # 设置散点图可缩放平移
        scatter.set_global_opts(
            tooltip_opts=opts.TooltipOpts(trigger="item")
        )
        
        # 颜色映射
        color_map = {
            0: "#C4A39F",  # 暂无
            1: "#81CB31",  # 很低 - 冷色
            2: "#A1FF3D",  # 低 - 冷色
            3: "#F5EE32",  # 中 - 中性
            4: "#FF642E",  # 高 - 暖色
            5: "#FF2319",  # 很高 - 暖色
            6: "#CC0000"   # 极高 - 暖色
        }
        
        # 等级文本映射
        level_map = {
            0: '暂无',
            1: '很低',
            2: '低',
            3: '中',
            4: '高',
            5: '很高',
            6: '极高'
        }
        
        print("分组城市数据...")
        # 按等级分组城市数据
        level_data_dict = {}
        for city, province, value in city_province_data:
            if value not in level_data_dict:
                level_data_dict[value] = []
            level_data_dict[value].append((city, value))
        
        print("创建各等级散点图...")
        # 为每个等级创建散点图 - 直接参考map_server_example.py的做法
        for level, data in level_data_dict.items():
            level_name = level_map.get(level, f"等级{level}")
            color = color_map.get(level, "#888888")
            
            scatter.add(
                series_name=level_name,
                data_pair=data,
                type_="effectScatter",
                symbol_size=12,
                color=color,
                effect_opts=opts.EffectOpts(
                    is_show=True,
                    scale=3.5,
                    period=4,
                    color=color,
                    brush_type="stroke"
                ),
                label_opts=opts.LabelOpts(
                    is_show=True,
                    formatter="{b}",
                    position="right",
                    font_size=10,
                    color="#333"
                ),
                itemstyle_opts=opts.ItemStyleOpts(opacity=0.8),
                tooltip_opts=opts.TooltipOpts(
                    formatter=JsCode("""
function(params) {
    var levelMap = {
        0: '暂无',
        1: '很低',
        2: '低',
        3: '中',
        4: '高',
        5: '很高',
        6: '极高'
    };
    var value = params.value[2];
    var levelText = levelMap[value] || '未知';
    
    // 检测是否为移动设备，如果是则添加提示
    var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    var touchTip = isMobile ? '<br/>(点击可放大地图)' : '';
    
    return params.name + '<br/>花粉等级: ' + levelText + touchTip;
}
""")
                )
            )
        
        print("设置图例...")
        # 添加图例
        scatter.set_global_opts(
            visualmap_opts=opts.VisualMapOpts(
                is_show=True,
                type_="piecewise",  # 使用分段型视觉映射
                pieces=[
                    {"min": 0, "max": 0, "label": "暂无", "color": "#C4A39F"},
                    {"min": 1, "max": 1, "label": "很低", "color": "#81CB31"},
                    {"min": 2, "max": 2, "label": "低", "color": "#A1FF3D"},
                    {"min": 3, "max": 3, "label": "中", "color": "#F5EE32"},
                    {"min": 4, "max": 4, "label": "高", "color": "#FF642E"},
                    {"min": 5, "max": 5, "label": "很高", "color": "#FF2319"},
                    {"min": 6, "max": 6, "label": "极高", "color": "#CC0000"}
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
        
        print("合并地图和散点图...")
        # 合并地图和散点图
        grid = Grid(init_opts=init_opts)
        grid.add(map_chart, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="5%", pos_bottom="5%"))
        grid.add(scatter, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="5%", pos_bottom="5%"))
        
        print("添加JS回调函数...")
        # 添加JS回调函数，强制地图和散点保持同步 - 添加更强大的同步逻辑来修复悬停缩放问题
        grid.add_js_funcs("""
        // 修复chart未定义的问题
        document.addEventListener('DOMContentLoaded', function() {
            // 使用DOM加载完成事件确保元素存在
            // 动态查找容器ID - ECharts容器的ID总是在图表渲染时自动生成
            var chartContainer = document.querySelector('div[_echarts_instance_]');
            if (chartContainer) {
                var chart = echarts.getInstanceByDom(chartContainer);
                
                // 初始化chart大小
                function resizeChart() {
                    if (chart) {
                        chart.resize();
                    }
                }
                
                // 监听窗口大小变化
                window.addEventListener('resize', resizeChart);
                
                // 同步两个地图视图的函数，解决悬停缩放位置不一致问题
                function syncMaps() {
                    if (chart) {
                        var option = chart.getOption();
                        
                        // 确保两个地图配置存在
                        if (option.geo && option.geo.length >= 2) {
                            // 获取第一个地图的中心点和缩放级别
                            var center = option.geo[0].center;
                            var zoom = option.geo[0].zoom;
                            
                            // 将这些值同步应用到第二个地图
                            option.geo[1].center = center;
                            option.geo[1].zoom = zoom;
                            
                            // 更新图表，设置notMerge为false以确保只更新变化的部分，不影响其他配置
                            chart.setOption(option, {notMerge: false});
                        }
                    }
                }
                
                // 监听地图缩放和平移事件
                chart.on('georoam', function(params) {
                    syncMaps();
                });
                
                // 监听地图鼠标移入事件，确保悬停时同步
                chart.on('mouseover', function(params) {
                    syncMaps();
                });
                
                // 监听地图鼠标移出事件，确保鼠标移出后同步
                chart.on('mouseout', function(params) {
                    syncMaps();
                });
                
                // 监听地图点击事件，确保点击后同步
                chart.on('click', function(params) {
                    syncMaps();
                });
                
                // 移动设备触摸支持
                chartContainer.addEventListener('touchstart', function(e) {
                    // 阻止浏览器默认行为（如页面滚动）
                    if (e.touches.length > 1) {
                        e.preventDefault();
                    }
                }, { passive: false });
                
                chartContainer.addEventListener('touchmove', function(e) {
                    // 对于多点触摸（缩放），阻止页面滚动
                    if (e.touches.length > 1) {
                        e.preventDefault();
                    }
                }, { passive: false });
                
                // 触摸结束后同步地图
                chartContainer.addEventListener('touchend', function() {
                    syncMaps();
                });
                
                // 特别处理移动设备上的缩放
                var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
                if (isMobile) {
                    // 移动设备上调整图表中的文本大小
                    chart.setOption({
                        series: [{
                            label: { fontSize: 8 }
                        }]
                    }, false);
                }
                
                // 初始调整大小
                setTimeout(resizeChart, 100);
            }
        });
        """)
        
        print("地图创建完成")
        return grid
    except Exception as e:
        import traceback
        print(f"创建地图时发生异常: {e}")
        traceback.print_exc()
        return None

def create_index_html(output_dir):
    """创建GitHub Pages适用的主页HTML"""
    # 扫描maps目录以获取所有存在的地图文件
    maps_dir = os.path.join(output_dir, "maps")
    available_map_dates = []
    
    # 如果目录存在，扫描所有地图文件
    if os.path.exists(maps_dir):
        map_files = [f for f in os.listdir(maps_dir) if f.startswith("map_") and f.endswith(".html")]
        for map_file in map_files:
            # 从文件名中提取日期 (map_2025-03-22.html -> 2025-03-22)
            date_match = re.search(r'map_(\d{4}-\d{2}-\d{2})\.html', map_file)
            if date_match:
                date_str = date_match.group(1)
                if date_str not in available_map_dates:
                    available_map_dates.append(date_str)
    
    # 注意：available_dates是全局变量，包含当前数据文件中的日期
    # 确保我们只显示那些已经生成了地图的日期
    if not available_map_dates:
        print("警告: 没有找到地图文件。将使用当前数据中的日期列表。")
        displayed_dates = available_dates
    else:
        print(f"在maps目录找到了 {len(available_map_dates)} 个日期的地图文件")
        displayed_dates = sorted(available_map_dates)
    
    if not displayed_dates:
        print("错误: 没有可用的日期可以显示。索引页将为空。")
        displayed_dates = []
    
    print(f"索引页将包含 {len(displayed_dates)} 个日期的地图")
    
    index_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>花粉分布地图服务</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="./assets/favicon.svg" type="image/svg+xml">
    <link rel="icon" href="./favicon.ico" type="image/x-icon">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: #fff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 20px;
            font-size: calc(1.5rem + 1vw);
        }
        .controls {
            margin-bottom: 15px;
            text-align: center;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
        }
        select, button {
            padding: 8px 16px;
            font-size: 16px;
            border-radius: 4px;
        }
        select {
            border: 1px solid #ccc;
            flex: 1;
            max-width: 200px;
            min-width: 120px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
            flex: 0 0 auto;
        }
        button:hover {
            background-color: #45a049;
        }
        .map-container {
            margin-top: 15px;
            text-align: center;
            position: relative;
            width: 100%;
            height: 0;
            padding-bottom: 75%; /* 4:3 宽高比 */
            overflow: hidden;
        }
        iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .footer {
            margin-top: 15px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
        
        /* 响应式设计 */
        @media (max-width: 600px) {
            body {
                padding: 5px;
            }
            .container {
                padding: 10px;
            }
            h1 {
                font-size: calc(1.2rem + 1vw);
                margin-bottom: 15px;
            }
            select, button {
                padding: 8px 12px;
                font-size: 14px;
            }
            .map-container {
                padding-bottom: 100%; /* 移动设备上使用1:1比例 */
            }
            .footer {
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>全国花粉分布地图服务</h1>
        <div class="controls">
            <select id="dateSelect">
"""
    
    # 添加日期选项，只使用已确认存在的日期
    for date in displayed_dates:
        index_content += f'                <option value="{date}">{date}</option>\n'
    
    index_content += """
            </select>
            <button onclick="updateMap()">查看地图</button>
        </div>
        <div class="map-container">
            <iframe id="mapFrame" src="" frameborder="0"></iframe>
        </div>
        <div class="footer">
            数据更新时间: TIMESTAMP
        </div>
    </div>

    <script>
        function updateMap() {
            var date = document.getElementById('dateSelect').value;
            document.getElementById('mapFrame').src = './maps/map_' + date + '.html';
        }
        
        // 初始化默认地图
        window.onload = function() {
            // 获取所有选项
            var selectElement = document.getElementById('dateSelect');
            var options = selectElement.options;
            
            // 选择最后一个选项（假设选项是按日期排序的，最后一个是最新的）
            selectElement.selectedIndex = options.length - 1;
            
            // 加载选定日期的地图
            updateMap();
        }
    </script>
</body>
</html>
"""
    
    # 替换时间戳
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    index_content = index_content.replace("TIMESTAMP", timestamp)
    
    # 写入index.html
    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"已创建主页: {index_path}")
    
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
    
    # 创建assets子目录（用于favicon等资源）
    assets_dir = os.path.join(output_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # 创建简单的favicon
    favicon_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" fill="#4CAF50"/>
    <circle cx="50" cy="50" r="30" fill="#FFD700" opacity="0.7"/>
</svg>"""
    
    with open(os.path.join(assets_dir, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(favicon_svg)
    
    # 同时创建ico格式的favicon
    with open(os.path.join(output_dir, "favicon.ico"), "w", encoding="utf-8") as f:
        f.write(favicon_svg)
    
    print("已创建网站图标文件")
    
    # 加载城市坐标
    load_city_coordinates()
    
    # 加载数据
    if not load_data(file_path):
        print("加载数据失败，无法生成地图")
        return False
    
    # 为每个日期生成地图
    generated_maps = []
    for date in available_dates:
        print(f"正在为日期 {date} 生成地图...")
        grid = create_map(date)
        if grid:
            # 渲染到HTML文件
            map_file_path = os.path.join(maps_dir, f"map_{date}.html")
            
            # 先生成原始HTML
            temp_path = os.path.join(maps_dir, f"temp_{date}.html")
            grid.render(temp_path)
            
            # 读取生成的HTML并添加favicon
            with open(temp_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 添加favicon引用（在</head>前插入）
            favicon_tags = """
    <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
    <link rel="icon" href="../favicon.ico" type="image/x-icon">
"""
            html_content = html_content.replace("</head>", favicon_tags + "</head>")
            
            # 添加jQuery支持
            jquery_tag = """
    <script src="https://cdn.bootcdn.net/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
"""
            html_content = html_content.replace("<head>", "<head>" + jquery_tag)
            
            # 添加移动设备响应式支持
            responsive_meta_tag = """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
"""
            html_content = html_content.replace("<head>", "<head>" + responsive_meta_tag)
            
            # 添加响应式样式
            responsive_style = """
    <style>
        @media (max-width: 600px) {
            .chart-container {
                padding: 0 !important;
            }
            #container {
                height: 450px !important;
            }
            /* 增强移动设备上的交互体验 */
            .ec-extension-geo {
                touch-action: pan-x pan-y !important;
            }
            /* 调整文本大小 */
            .ec-legend-item, .ec-legend-item-text {
                font-size: 12px !important;
            }
        }
        /* 防止页面超出屏幕 */
        body {
            overflow-x: hidden;
        }
        /* 增强地图互动性 */
        #container {
            touch-action: manipulation;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }
    </style>
"""
            html_content = html_content.replace("</head>", responsive_style + "</head>")
            
            # 修改formatter函数中的levelMap
            formatted_form = '"formatter": function(params) {\n    var levelMap = {\n        0: \'\\u6682\\u65e0\',\n        1: \'\\u5f88\\u4f4e\',\n        2: \'\\u4f4e\',\n        3: \'\\u4e2d\',\n        4: \'\\u9ad8\',\n        5: \'\\u5f88\\u9ad8\',\n        6: \'\\u6781\\u9ad8\'\n    };\n    var value = params.value[2];\n    var levelText = levelMap[value] || \'\\u672a\\u77e5\';\n    \n    // \\u68c0\\u6d4b\\u662f\\u5426\\u4e3a\\u79fb\\u52a8\\u8bbe\\u5907\\uff0c\\u5982\\u679c\\u662f\\u5219\\u6dfb\\u52a0\\u63d0\\u793a\n    var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);\n    var touchTip = isMobile ? \'<br/>(\\u70b9\\u51fb\\u53ef\\u653e\\u5927\\u5730\\u56fe)\' : \'\';\n    \n    return params.name + \'<br/>\\u82b1\\u7c89\\u7b49\\u7ea7: \' + levelText + touchTip;\n}'
            
            def replace_formatter(match):
                return formatted_form + ','
            
            # 使用更复杂的正则表达式来匹配嵌套的花括号
            html_content = re.sub(
                r'"formatter": function\(params\) \{(?:[^{}]|(?:\{[^{}]*\}))*\},',
                replace_formatter,
                html_content
            )
            
            # 写入最终HTML文件
            with open(map_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 删除临时文件
            try:
                os.remove(temp_path)
            except:
                pass
            
            generated_maps.append(map_file_path)
            print(f"已生成地图: {map_file_path}")
    
    # 确保index.html中的favicon路径正确
    create_index_html(output_dir)
    
    print(f"已生成 {len(generated_maps)} 个地图文件")
    print("静态地图网站已准备就绪，可部署到GitHub Pages")
    print(f"本地预览: 打开 {os.path.join(output_dir, 'index.html')}")
    print("GitHub Pages部署提示: 请确保仓库设置中的GitHub Pages源设置为'docs'文件夹")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='花粉分布静态地图生成器')
    # 使用相对路径作为默认数据文件
    default_data_file = 'data/pollen_data_latest.csv'
    parser.add_argument('-f', '--file', default=default_data_file, help=f'花粉数据CSV文件路径 (默认: {default_data_file})')
    parser.add_argument('-o', '--output-dir', default='docs', help='输出目录路径 (默认: docs)')
    parser.add_argument('--test', action='store_true', help='生成测试数据并验证地图功能')
    parser.add_argument('--github', action='store_true', help='生成适合GitHub Pages部署的文件')
    
    args = parser.parse_args()
    
    print("============================================================")
    print("花粉分布静态地图生成器")
    print("============================================================")
    
    # 测试模式：生成测试数据并验证地图功能
    if args.test:
        return run_test_mode(args.output_dir)
    
    # 正常模式：使用指定的数据文件或默认文件
    print(f"数据文件: {args.file}")
    print(f"输出目录: {args.output_dir}")
    if args.github:
        print("GitHub Pages模式: 启用")
    print("============================================================")
    
    # 检查默认数据文件是否存在
    if not os.path.exists(args.file):
        print(f"错误：找不到数据文件 {args.file}")
        print("请提供正确的数据文件路径，或使用 --test 参数生成测试数据")
        return 1
    
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

def run_test_mode(output_dir):
    """运行测试模式，生成测试数据并验证地图功能"""
    import tempfile
    import csv
    
    print("运行测试模式：生成测试数据并验证地图功能")
    print(f"输出目录: {output_dir}")
    print("============================================================")
    
    # 清理可能存在的多余文件 - 检查是否存在超出数据范围的日期文件
    maps_dir = os.path.join(output_dir, "maps")
    if os.path.exists(maps_dir):
        # 首先查询源数据文件中存在的日期
        data_dates = []
        data_file = 'data/pollen_data_latest.csv'
        if os.path.exists(data_file):
            try:
                df = pd.read_csv(data_file)
                if '日期' in df.columns:
                    data_dates = sorted(df['日期'].unique())
            except Exception as e:
                print(f"警告: 读取数据文件时出错: {str(e)}")
        
        # 如果无法读取数据文件，使用固定的有效日期范围
        if not data_dates:
            data_dates = [
                '2025-03-16', '2025-03-17', '2025-03-18', '2025-03-19',
                '2025-03-20', '2025-03-21', '2025-03-22', '2025-03-23'
            ]
        
        # 找出所有不在有效日期范围内的地图文件
        all_map_files = [f for f in os.listdir(maps_dir) if f.startswith("map_") and f.endswith(".html")]
        extra_files = []
        
        for map_file in all_map_files:
            date_match = re.search(r'map_(\d{4}-\d{2}-\d{2})\.html', map_file)
            if date_match:
                file_date = date_match.group(1)
                if file_date not in data_dates:
                    extra_files.append(map_file)
        
        # 删除多余文件
        for file in extra_files:
            try:
                os.remove(os.path.join(maps_dir, file))
                print(f"已删除多余文件: {file}")
            except Exception as e:
                print(f"删除文件 {file} 失败: {str(e)}")
    
    # 创建临时测试数据文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as tmp:
        test_data_file = tmp.name
        writer = csv.writer(tmp)
        
        # 写入表头
        writer.writerow(['日期', '城市', '花粉等级'])
        
        # 生成测试数据
        test_cities = [
            ('北京', '很高'), ('上海', '低'), ('广州', '较低'), ('深圳', '中'),
            ('杭州', '偏高'), ('南京', '高'), ('武汉', '较高'), ('成都', '很高'),
            ('重庆', '极高'), ('西安', '暂无'), ('天津', '很低'), ('苏州', '低'),
            ('沈阳', '较低'), ('哈尔滨', '中'), ('长春', '偏高'), ('长沙', '高'),
            ('福州', '较高'), ('郑州', '很高'), ('济南', '极高'), ('青岛', '暂无')
        ]
        
        # 使用与实际数据文件匹配的固定日期范围
        test_dates = [
            '2025-03-16', '2025-03-17', '2025-03-18', '2025-03-19',
            '2025-03-20', '2025-03-21', '2025-03-22', '2025-03-23'
        ]
        
        print(f"将为以下日期生成测试数据: {', '.join(test_dates)}")
        
        # 为每个城市在每个测试日期生成数据
        for city, level in test_cities:
            for date in test_dates:
                writer.writerow([date, city, level])
        
    print(f"已生成测试数据文件: {test_data_file}")
    print(f"包含 {len(test_cities)} 个城市，每个城市 {len(test_dates)} 个日期的数据")
    
    # 使用测试数据生成地图
    try:
        generate_static_maps(
            file_path=test_data_file,
            output_dir=output_dir
        )
        print("测试模式运行成功！")
        print(f"请查看输出目录: {output_dir}")
        print(f"请打开 {os.path.join(output_dir, 'index.html')} 预览地图")
        # 不删除临时文件，以便用户查看
        print(f"测试数据文件: {test_data_file}")
        return 0
    except Exception as e:
        print(f"测试模式运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # 记录下临时文件路径，但不删除
        print(f"测试数据文件: {test_data_file}")

if __name__ == "__main__":
    sys.exit(main()) 