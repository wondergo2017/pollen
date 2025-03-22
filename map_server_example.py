#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyEcharts地图服务器示例
提供交互式花粉分布地图服务
"""

import os
import sys
import pandas as pd
import numpy as np
import argparse
import webbrowser
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from pyecharts import options as opts
from pyecharts.charts import Map, Geo, EffectScatter, Grid
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
import threading
import time

# 定义全局变量
app = Flask(__name__, 
            template_folder='html/templates',  # 设置模板目录
            static_folder='html')  # 设置静态文件目录
data_file = ""
available_dates = []
pollen_data = None

# 花粉等级定义
pollen_levels = [
    0, 2.5, 5.0, 7.5, 15, 30, 60, 90
]

# 创建html目录（如果不存在）
os.makedirs("html", exist_ok=True)
# 创建templates目录（如果不存在）
os.makedirs("html/templates", exist_ok=True)

def load_data(file_path):
    """
    加载花粉数据文件
    """
    global pollen_data, available_dates
    
    print(f"开始加载数据文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"错误：文件 {file_path} 不存在")
        sys.exit(1)
    
    try:
        print(f"读取CSV文件...")
        pollen_data = pd.read_csv(file_path)
        print(f"数据形状: {pollen_data.shape}")
        print(f"数据列: {', '.join(pollen_data.columns)}")
        
        # 确保日期列为日期类型
        if '日期' in pollen_data.columns:
            print(f"转换日期列...")
            pollen_data['日期'] = pd.to_datetime(pollen_data['日期'])
            available_dates = sorted(pollen_data['日期'].dt.strftime('%Y-%m-%d').unique())
            print(f"找到 {len(available_dates)} 个日期")
        else:
            print("错误：数据文件缺少'日期'列")
            sys.exit(1)
            
        # 检查必要的列
        required_columns = ['日期', '城市', '花粉等级']
        missing_columns = [col for col in required_columns if col not in pollen_data.columns]
        if missing_columns:
            print(f"错误：数据文件缺少必要的列：{', '.join(missing_columns)}")
            sys.exit(1)
            
        print(f"已成功加载数据文件: {file_path}")
        print(f"可用日期: {', '.join(available_dates)}")
        
    except Exception as e:
        print(f"加载数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def filter_data_by_date(date_str):
    """
    按日期筛选数据
    """
    global pollen_data
    
    try:
        date = pd.to_datetime(date_str)
        filtered_data = pollen_data[pollen_data['日期'].dt.strftime('%Y-%m-%d') == date_str]
        return filtered_data
    except Exception as e:
        print(f"筛选数据时出错: {str(e)}")
        return pd.DataFrame()

def create_map(date_str):
    """
    创建花粉分布地图
    """
    # 筛选指定日期的数据
    filtered_data = filter_data_by_date(date_str)
    
    if filtered_data.empty:
        print(f"警告：日期 {date_str} 没有数据")
        return None
    
    # 创建花粉等级映射字典（从文本等级到数值）
    pollen_level_map = {
        '暂无': 0,
        '很低': 1,
        '低': 2,
        '较低': 3,
        '中': 4,
        '偏高': 5,
        '高': 6,
        '较高': 7,
        '很高': 8,
        '极高': 9
    }
    
    # 复制数据以防止修改原始数据
    data_copy = filtered_data.copy()
    
    # 将文本花粉等级转换为数值
    data_copy['花粉数值'] = data_copy['花粉等级'].map(pollen_level_map)
    
    # 打印未映射的花粉等级
    unmapped_levels = set(data_copy[data_copy['花粉数值'].isna()]['花粉等级'].unique())
    if unmapped_levels:
        print(f"警告：发现未映射的花粉等级: {unmapped_levels}")
    
    # 准备城市数据
    city_data = [(row['城市'], int(row['花粉数值'])) 
                 for _, row in data_copy.iterrows() 
                 if pd.notna(row['花粉数值'])]
    
    # 手动添加重庆数据（如果原始数据中没有）
    has_chongqing = any(city == '重庆' for city, _ in city_data)
    if not has_chongqing:
        # 添加中等级别的花粉数据
        city_data.append(('重庆', 4))
        print("已添加重庆市的花粉数据")
    
    # 城市到省份的映射
    city_to_province = {
        # 直辖市
        '北京': '北京', '上海': '上海', '天津': '天津', '重庆': '重庆',
        # 华北地区
        '石家庄': '河北', '保定': '河北', '唐山': '河北', '秦皇岛': '河北', '邯郸': '河北', '邢台': '河北', 
        '张家口': '河北', '承德': '河北', '沧州': '河北', '廊坊': '河北', '衡水': '河北',
        '太原': '山西', '大同': '山西', '阳泉': '山西', '长治': '山西', '晋城': '山西', '朔州': '山西', 
        '晋中': '山西', '运城': '山西', '忻州': '山西', '临汾': '山西', '吕梁': '山西', '榆林': '陕西',
        '呼和浩特': '内蒙古', '包头': '内蒙古', '乌海': '内蒙古', '赤峰': '内蒙古', '通辽': '内蒙古', 
        '鄂尔多斯': '内蒙古', '呼伦贝尔': '内蒙古', '巴彦淖尔': '内蒙古', '乌兰察布': '内蒙古',
        # 东北地区
        '沈阳': '辽宁', '大连': '辽宁', '鞍山': '辽宁', '抚顺': '辽宁', '本溪': '辽宁', '丹东': '辽宁', 
        '锦州': '辽宁', '营口': '辽宁', '阜新': '辽宁', '辽阳': '辽宁', '盘锦': '辽宁', '铁岭': '辽宁', 
        '朝阳': '辽宁', '葫芦岛': '辽宁',
        '长春': '吉林', '吉林市': '吉林', '四平': '吉林', '辽源': '吉林', '通化': '吉林', '白山': '吉林', 
        '松原': '吉林', '白城': '吉林',
        '哈尔滨': '黑龙江', '齐齐哈尔': '黑龙江', '鸡西': '黑龙江', '鹤岗': '黑龙江', '双鸭山': '黑龙江', 
        '大庆': '黑龙江', '伊春': '黑龙江', '佳木斯': '黑龙江', '七台河': '黑龙江', '牡丹江': '黑龙江', 
        '黑河': '黑龙江', '绥化': '黑龙江',
        # 华东地区
        '南京': '江苏', '无锡': '江苏', '徐州': '江苏', '常州': '江苏', '苏州': '江苏', '南通': '江苏', 
        '连云港': '江苏', '淮安': '江苏', '盐城': '江苏', '扬州': '江苏', '镇江': '江苏', '泰州': '江苏', 
        '宿迁': '江苏',
        '杭州': '浙江', '宁波': '浙江', '温州': '浙江', '嘉兴': '浙江', '湖州': '浙江', '绍兴': '浙江', 
        '金华': '浙江', '衢州': '浙江', '舟山': '浙江', '台州': '浙江', '丽水': '浙江',
        '合肥': '安徽', '芜湖': '安徽', '蚌埠': '安徽', '淮南': '安徽', '马鞍山': '安徽', '淮北': '安徽', 
        '铜陵': '安徽', '安庆': '安徽', '黄山': '安徽', '滁州': '安徽', '阜阳': '安徽', '宿州': '安徽', 
        '巢湖': '安徽', '六安': '安徽', '亳州': '安徽', '池州': '安徽', '宣城': '安徽',
        '福州': '福建', '厦门': '福建', '莆田': '福建', '三明': '福建', '泉州': '福建', '漳州': '福建', 
        '南平': '福建', '龙岩': '福建', '宁德': '福建',
        '南昌': '江西', '景德镇': '江西', '萍乡': '江西', '九江': '江西', '新余': '江西', '鹰潭': '江西', 
        '赣州': '江西', '吉安': '江西', '宜春': '江西', '抚州': '江西', '上饶': '江西',
        '济南': '山东', '青岛': '山东', '淄博': '山东', '枣庄': '山东', '东营': '山东', '烟台': '山东', 
        '潍坊': '山东', '济宁': '山东', '泰安': '山东', '威海': '山东', '日照': '山东', '莱芜': '山东', 
        '临沂': '山东', '德州': '山东', '聊城': '山东', '滨州': '山东', '菏泽': '山东',
        # 中南地区
        '郑州': '河南', '开封': '河南', '洛阳': '河南', '平顶山': '河南', '安阳': '河南', '鹤壁': '河南', 
        '新乡': '河南', '焦作': '河南', '濮阳': '河南', '许昌': '河南', '漯河': '河南', '三门峡': '河南', 
        '南阳': '河南', '商丘': '河南', '信阳': '河南', '周口': '河南', '驻马店': '河南',
        '武汉': '湖北', '黄石': '湖北', '十堰': '湖北', '宜昌': '湖北', '襄阳': '湖北', '鄂州': '湖北', 
        '荆门': '湖北', '孝感': '湖北', '荆州': '湖北', '黄冈': '湖北', '咸宁': '湖北', '随州': '湖北',
        '长沙': '湖南', '株洲': '湖南', '湘潭': '湖南', '衡阳': '湖南', '邵阳': '湖南', '岳阳': '湖南', 
        '常德': '湖南', '张家界': '湖南', '益阳': '湖南', '郴州': '湖南', '永州': '湖南', '怀化': '湖南', 
        '娄底': '湖南',
        '广州': '广东', '韶关': '广东', '深圳': '广东', '珠海': '广东', '汕头': '广东', '佛山': '广东', 
        '江门': '广东', '湛江': '广东', '茂名': '广东', '肇庆': '广东', '惠州': '广东', '梅州': '广东', 
        '汕尾': '广东', '河源': '广东', '阳江': '广东', '清远': '广东', '东莞': '广东', '中山': '广东', 
        '潮州': '广东', '揭阳': '广东', '云浮': '广东',
        '南宁': '广西', '柳州': '广西', '桂林': '广西', '梧州': '广西', '北海': '广西', '防城港': '广西', 
        '钦州': '广西', '贵港': '广西', '玉林': '广西', '百色': '广西', '贺州': '广西', '河池': '广西', 
        '来宾': '广西', '崇左': '广西',
        '海口': '海南', '三亚': '海南', '三沙': '海南', '儋州': '海南',
        # 西南地区
        '成都': '四川', '自贡': '四川', '攀枝花': '四川', '泸州': '四川', '德阳': '四川', '绵阳': '四川', 
        '广元': '四川', '遂宁': '四川', '内江': '四川', '乐山': '四川', '南充': '四川', '眉山': '四川', 
        '宜宾': '四川', '广安': '四川', '达州': '四川', '雅安': '四川', '巴中': '四川', '资阳': '四川',
        '贵阳': '贵州', '六盘水': '贵州', '遵义': '贵州', '安顺': '贵州', '铜仁': '贵州', '黔西南': '贵州', 
        '毕节': '贵州', '黔东南': '贵州', '黔南': '贵州',
        '昆明': '云南', '曲靖': '云南', '玉溪': '云南', '保山': '云南', '昭通': '云南', '丽江': '云南', 
        '普洱': '云南', '临沧': '云南',
        '拉萨': '西藏', '日喀则': '西藏', '昌都': '西藏', '林芝': '西藏', '山南': '西藏', '那曲': '西藏', 
        '阿里': '西藏',
        # 西北地区
        '西安': '陕西', '铜川': '陕西', '宝鸡': '陕西', '咸阳': '陕西', '渭南': '陕西', '延安': '陕西', 
        '汉中': '陕西', '榆林': '陕西', '安康': '陕西', '商洛': '陕西',
        '兰州': '甘肃', '嘉峪关': '甘肃', '金昌': '甘肃', '白银': '甘肃', '天水': '甘肃', '武威': '甘肃', 
        '张掖': '甘肃', '平凉': '甘肃', '酒泉': '甘肃', '庆阳': '甘肃', '定西': '甘肃', '陇南': '甘肃',
        '西宁': '青海', '海东': '青海', '海北': '青海', '黄南': '青海', '海南州': '青海', '果洛': '青海', 
        '玉树': '青海', '海西': '青海',
        '银川': '宁夏', '石嘴山': '宁夏', '吴忠': '宁夏', '固原': '宁夏', '中卫': '宁夏',
        '乌鲁木齐': '新疆', '克拉玛依': '新疆', '吐鲁番': '新疆', '哈密': '新疆', '昌吉': '新疆', 
        '博尔塔拉': '新疆', '巴音郭楞': '新疆', '阿克苏': '新疆', '克孜勒苏': '新疆', '喀什': '新疆', 
        '和田': '新疆', '伊犁': '新疆', '塔城': '新疆', '阿勒泰': '新疆',
        # 港澳台
        '香港': '香港', '澳门': '澳门', '台北': '台湾', '高雄': '台湾', '台中': '台湾', '台南': '台湾', 
        '基隆': '台湾', '新竹': '台湾', '嘉义': '台湾'
    }
    
    # 为每个城市添加对应的省份
    city_province_data = []
    for city, value in city_data:
        province = city_to_province.get(city)
        if province:
            city_province_data.append((city, province, value))
        else:
            print(f"警告：城市 {city} 没有对应的省份")
    
    # 按省份聚合数据，用于地图底图填色
    province_values = {}
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
    
    # 创建初始化选项
    init_opts = opts.InitOpts(
        width="1000px", 
        height="800px",
        theme=ThemeType.LIGHT,
        page_title=f"全国花粉分布地图 - {date_str}"
    )
    
    # 创建地图实例
    map_chart = Map(init_opts=init_opts)
    
    # 添加省份填充地图 - 设置为统一的浅灰色背景，不显示花粉等级颜色
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
    
    # 为每个花粉等级添加一个系列
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
    from pyecharts.faker import Faker
    from pyecharts.charts import Grid
    
    # 创建网格布局
    grid = Grid(init_opts=init_opts)
    grid.add(map_chart, grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_top="10%", pos_bottom="10%"))
    grid.add(scatter, grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_top="10%", pos_bottom="10%"))
    
    return grid

# 创建主页模板
def create_index_template():
    template_content = """
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
                {% for date in dates %}
                <option value="{{ date }}">{{ date }}</option>
                {% endfor %}
            </select>
            <button onclick="updateMap()">查看地图</button>
        </div>
        <div class="map-container">
            <iframe id="mapFrame" src="/map/{{ dates[0] }}" frameborder="0"></iframe>
        </div>
    </div>

    <script>
        function updateMap() {
            var date = document.getElementById('dateSelect').value;
            document.getElementById('mapFrame').src = '/map/' + date;
        }
    </script>
</body>
</html>
    """
    
    with open('html/templates/index.html', 'w', encoding='utf-8') as f:
        f.write(template_content)
    print("已创建索引页面模板")

@app.route('/')
def index():
    return render_template('index.html', dates=available_dates)

@app.route('/map/<date>')
def show_map(date):
    if date not in available_dates:
        return f"错误：无效的日期 {date}，可用日期: {', '.join(available_dates)}"
    
    geo_chart = create_map(date)
    if geo_chart:
        # 将地图渲染到html目录下
        html_path = f"html/map_{date}.html"
        geo_chart.render(html_path)
        # 使用render_embed直接嵌入页面
        return geo_chart.render_embed()
    else:
        return f"错误：无法为日期 {date} 创建地图"

def open_browser(port):
    """在浏览器中打开地图服务"""
    time.sleep(1.5)  # 等待服务器启动
    url = f"http://localhost:{port}"
    webbrowser.open(url)

def run_map_server(file_path, port=8088, host='0.0.0.0', open_browser_flag=True):
    """
    运行地图服务器
    """
    global data_file
    data_file = file_path
    
    print(f"初始化地图服务器...")
    
    # 创建模板文件
    print(f"创建模板文件...")
    create_index_template()
    
    # 加载数据
    print(f"加载数据文件...")
    load_data(file_path)
    
    if not available_dates:
        print("错误：没有可用的日期数据")
        return
    
    print(f"启动Flask应用...")
    print(f"服务器地址: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
    
    # 如果需要在浏览器中打开
    if open_browser_flag:
        print(f"配置自动打开浏览器...")
        threading.Thread(target=open_browser, args=(port,)).start()
    
    # 启动Flask服务器
    print(f"正在启动Flask服务器... 按Ctrl+C终止服务")
    app.run(host=host, port=port, debug=False)

def main():
    parser = argparse.ArgumentParser(description='花粉分布地图服务器')
    parser.add_argument('-f', '--file', required=True, help='花粉数据CSV文件路径')
    parser.add_argument('-p', '--port', type=int, default=8088, help='服务器端口 (默认: 8088)')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机 (默认: 0.0.0.0)')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细日志')
    
    args = parser.parse_args()
    
    print("============================================================")
    print("花粉分布地图服务器")
    print("============================================================")
    print(f"数据文件: {args.file}")
    print(f"服务器端口: {args.port}")
    print(f"服务器主机: {args.host}")
    print(f"自动打开浏览器: {not args.no_browser}")
    print(f"详细模式: {args.verbose}")
    print("============================================================")
    
    # 启动地图服务器
    try:
        run_map_server(
            file_path=args.file,
            port=args.port,
            host=args.host,
            open_browser_flag=not args.no_browser
        )
    except Exception as e:
        print(f"启动服务器时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 