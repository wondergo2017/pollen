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
            '暂无': 0, '很低': 1, '低': 2, '较低': 3, '中': 4,
            '偏高': 5, '高': 6, '较高': 7, '很高': 8, '极高': 9
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
    
    # 创建初始化选项 - 直接使用pyecharts
    from pyecharts import options as opts
    from pyecharts.charts import Map, Geo, Grid
    from pyecharts.globals import ThemeType
    from pyecharts.commons.utils import JsCode
    
    init_opts = opts.InitOpts(
        width="1000px", 
        height="800px",
        theme=ThemeType.LIGHT,
        page_title=f"全国花粉分布地图 - {date_str}"
    )
    
    # 创建地图实例
    map_chart = Map(init_opts=init_opts)
    
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
    
    # 设置全局选项
    map_chart.set_global_opts(
        title_opts=opts.TitleOpts(
            title=f"全国花粉分布地图 - {date_str}",  # 添加标题
            subtitle="",
            pos_left="center",
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=24,
                color="#333333"
            )
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="item"
        )
    )
    
    # 创建散点图实例
    scatter = Geo(init_opts=init_opts)
    
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
                formatter=JsCode(
                    """function(params) {
                        var levelMap = {
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
                        };
                        var value = params.value[2];
                        var levelText = levelMap[value] || '未知';
                        return params.name + '<br/>花粉等级: ' + levelText;
                    }"""
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
    grid = Grid(init_opts=init_opts)
    grid.add(map_chart, grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_top="10%", pos_bottom="10%"))
    grid.add(scatter, grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_top="10%", pos_bottom="10%"))
    
    return grid

def create_index_html(output_dir):
    """创建GitHub Pages适用的主页HTML"""
    index_content = """
<!DOCTYPE html>
<html>
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
        .footer {
            margin-top: 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
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
            var defaultDate = document.getElementById('dateSelect').value;
            if (defaultDate) {
                document.getElementById('mapFrame').src = './maps/map_' + defaultDate + '.html';
            }
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
            # 添加favicon链接到HTML内容
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
            
            # 写入最终HTML文件
            with open(map_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 删除临时文件
            os.remove(temp_path)
            
            generated_maps.append(map_file_path)
            print(f"已生成地图: {map_file_path}")
    
    # 生成主页 - 确保主页是在地图文件生成后生成的
    create_index_html(output_dir)
    
    # 创建README.md文件，方便在GitHub上显示项目信息
    readme_content = f"""# 全国花粉分布地图

这是一个静态的花粉分布地图网站，可以在GitHub Pages上访问。

## 数据信息

- 数据源文件: {os.path.basename(file_path)}
- 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 包含日期数量: {len(available_dates)}

## 如何访问

访问 https://[您的用户名].github.io/[仓库名]/ 即可查看花粉分布地图。

## 本地预览

克隆本仓库后，直接打开 index.html 文件即可本地预览。
"""
    
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"已创建README文件: {readme_path}")
    
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
    
    # 创建临时测试数据文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as tmp:
        test_data_file = tmp.name
        writer = csv.writer(tmp)
        
        # 写入表头
        writer.writerow(['日期', '城市', '花粉等级'])
        
        # 生成测试数据
        test_cities = [
            ('北京', '很低'), ('上海', '低'), ('广州', '较低'), ('深圳', '中'),
            ('杭州', '偏高'), ('南京', '高'), ('武汉', '较高'), ('成都', '很高'),
            ('重庆', '极高'), ('西安', '暂无'), ('天津', '很低'), ('苏州', '低'),
            ('沈阳', '较低'), ('哈尔滨', '中'), ('长春', '偏高'), ('长沙', '高'),
            ('福州', '较高'), ('郑州', '很高'), ('济南', '极高'), ('青岛', '暂无')
        ]
        
        # 生成两个测试日期的数据
        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        
        for city, level in test_cities:
            writer.writerow([today, city, level])
            writer.writerow([tomorrow, city, level])
        
    print(f"已生成测试数据文件: {test_data_file}")
    print(f"包含 {len(test_cities)} 个城市，每个城市 2 个日期的数据")
    
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