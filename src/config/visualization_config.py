#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
可视化配置模块
提供花粉数据可视化配置
"""

import os
import sys
import platform
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import warnings

# 花粉等级颜色映射
POLLEN_LEVEL_COLORS = {
    "0": "#999999",  # 未检测/无 - 灰色
    "1": "#81CB31",  # A级/很低 - 绿色
    "2": "#A1FF3D",  # B级/较低 - 浅绿色
    "3": "#F5EE32",  # C级/偏高 - 黄色
    "4": "#FFAF13",  # D级/较高 - 橙色
    "5": "#FF2319",  # E级/很高 - 红色
}

# 花粉等级的数值映射（用于排序和绘图）
LEVEL_NUMERIC_MAP = {
    "未检测": 0,
    "很低": 1,
    "较低": 2,
    "偏高": 3,
    "较高": 4,
    "很高": 5,
    "极高": 6,
    "暂无": -1
}

# 花粉等级对应的文字说明
LEVEL_DESCRIPTIONS = {
    "未检测": "无花粉",
    "很低": "不易引发过敏反应",
    "较低": "对极敏感人群可能引发过敏反应",
    "偏高": "易引发过敏，加强防护，对症用药",
    "较高": "易引发过敏，加强防护，规范用药",
    "很高": "极易引发过敏，减少外出，持续规范用药",
    "极高": "极易引发过敏，建议足不出户，规范用药",
    "暂无": "暂无数据"
}

# 花粉等级名称映射
POLLEN_LEVEL_NAMES = {
    "0": "无花粉",
    "1": "很低",
    "2": "较低",
    "3": "偏高",
    "4": "较高",
    "5": "很高"
}

# 花粉等级描述
POLLEN_LEVEL_DESCRIPTIONS = {
    "0": "无花粉",
    "1": "不易引发过敏反应。",
    "2": "对极敏感人群可能引发过敏反应。",
    "3": "易引发过敏，加强防护，对症用药。",
    "4": "易引发过敏，加强防护，规范用药。",
    "5": "极易引发过敏，减少外出，持续规范用药。"
}

# 默认图表尺寸
DEFAULT_FIGURE_SIZE = (12, 8)
DEFAULT_SMALL_FIGURE_SIZE = (8, 6)

# 输出配置
DEFAULT_DPI = 300
DEFAULT_FORMAT = 'png'

# 查找系统中可用的字体
def find_available_fonts():
    """查找系统中可用的字体，优先选择中文字体"""
    available_fonts = []
    chinese_fonts = [
        'SimHei', 'Microsoft YaHei', 'SimSun', 'DengXian', 'KaiTi', 'FangSong',
        'WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'Noto Sans SC', 'Source Han Sans CN',
        'Noto Sans CJK TC', 'Noto Sans CJK JP', 'Hiragino Sans GB', 
        'AR PL UMing CN', 'AR PL KaitiM GB', 'STHeiti', 'STKaiti', 'STSong',
        'WenQuanYi Zen Hei', 'WenQuanYi Zen Hei Sharp', 'NSimSun',
        'Droid Sans Fallback', 'PingFang SC', 'PingFang TC', 'HanaMinA', 'HanaMinB'
    ]
    
    # 拉丁字符字体，用于显示英文和数字
    latin_fonts = [
        'DejaVu Sans', 'Liberation Sans', 'Arial', 'Helvetica', 'Verdana', 'Tahoma'
    ]
    
    # 查找系统中已安装的字体
    system_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 检查系统中是否有中文字体文件
    for font_file in fm.findSystemFonts():
        try:
            font = fm.FontProperties(fname=font_file)
            font_name = font.get_name()
            # 检查字体是否支持中文
            if any(chinese_font in font_name for chinese_font in ['Hei', 'Ming', 'Song', 'Yuan', 'Kai', 'Fang', 'Zhong', 'CN', 'GB', 'SC', 'TC']):
                if font_name not in available_fonts:
                    available_fonts.append(font_name)
        except:
            pass
    
    # 优先选择已知的中文字体
    for font in chinese_fonts:
        if font in system_fonts and font not in available_fonts:
            available_fonts.append(font)
    
    # 找到最佳拉丁字体用于混合模式
    latin_font = next((font for font in latin_fonts if font in system_fonts), None)
    if latin_font:
        # 将拉丁字体添加到第一位
        if latin_font in available_fonts:
            available_fonts.remove(latin_font)
        available_fonts.insert(0, latin_font)
    
    # 如果找不到中文字体，使用系统默认字体
    if not available_fonts:
        if 'DejaVu Sans' in system_fonts:
            available_fonts.append('DejaVu Sans')
        elif 'Liberation Sans' in system_fonts:
            available_fonts.append('Liberation Sans')
        else:
            # 使用matplotlib的默认字体
            available_fonts = ['sans-serif']
    
    return available_fonts

def get_system_fonts():
    """获取系统推荐字体"""
    system = platform.system()
    
    # 首选字体列表 - 按系统类型
    if system == 'Windows':
        return ['Microsoft YaHei', 'SimHei', 'SimSun', 'Arial']
    elif system == 'Darwin':  # macOS
        return ['PingFang SC', 'Heiti SC', 'STHeiti', 'Arial Unicode MS', 'Helvetica']
    else:  # Linux 和其他
        return ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'Droid Sans Fallback', 
                'Source Han Sans CN', 'Ubuntu', 'Liberation Sans']

# 自动检测可用字体
AVAILABLE_FONTS = find_available_fonts()
PRIMARY_FONT = AVAILABLE_FONTS[0] if AVAILABLE_FONTS else 'sans-serif'

# 尝试检测中文字体
CJK_FONT = next((font for font in AVAILABLE_FONTS[1:] if font in [
    'SimHei', 'Microsoft YaHei', 'SimSun', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC',
    'Source Han Sans CN', 'Droid Sans Fallback', 'PingFang SC', 'STHeiti'
]), None)

# 配置字体回退设置
def configure_matplotlib_fonts():
    """配置matplotlib字体设置以支持中文和拉丁字符"""
    try:
        # 设置matplotlib全局字体
        plt.rcParams['font.family'] = 'sans-serif'
        
        # 添加字体回退顺序
        if CJK_FONT:
            plt.rcParams['font.sans-serif'] = [PRIMARY_FONT, CJK_FONT] + plt.rcParams['font.sans-serif']
            print(f"设置字体成功：主要字体 {PRIMARY_FONT}，中文字体 {CJK_FONT}")
        else:
            plt.rcParams['font.sans-serif'] = [PRIMARY_FONT] + plt.rcParams['font.sans-serif']
            print(f"设置字体成功：主要字体 {PRIMARY_FONT}，未找到支持中文的字体")
        
        # 用来正常显示负号
        plt.rcParams['axes.unicode_minus'] = False
        
        # 关闭字体警告
        warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
        
        return True
    except Exception as e:
        print(f"配置字体时出错: {str(e)}")
        return False

# 图表配置
CHART_CONFIG = {
    # 图表尺寸
    'figure_size': (12, 8),
    
    # 字体大小
    'title_size': 16,
    'axes_size': 14,
    'tick_size': 12,
    'legend_size': 12,
    'annotation_size': 10,
    
    # 线条样式
    'line_width': 2,
    'line_style': '-',
    'marker_size': 6,
    
    # 输出配置
    'dpi': 300,
    'format': 'png'
}

# 路径配置
def get_default_output_dir():
    """获取默认输出目录"""
    # 在项目根目录下的output/visualization_output目录
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = os.path.join(script_dir, 'output', 'visualization_output')
    
    # 确保目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    return output_dir

def get_default_data_dir():
    """获取默认数据目录"""
    # 在项目根目录下的data目录
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(script_dir, 'data')
    
    # 确保目录存在
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    return data_dir

# 花粉数据可视化配置文件
# 此文件包含了花粉数据可视化所需的配置信息，如颜色映射、标签等

# 花粉等级对应的颜色映射
LEVEL_COLORS = {
    "未检测": "#999999",
    "很低": "#81CB31",
    "较低": "#A1FF3D",
    "偏高": "#F5EE32",
    "较高": "#FFAF13",
    "很高": "#FF2319",
    "极高": "#AD075D",
    "暂无": "#CCCCCC"
}

# 花粉等级对应的文字说明
LEVEL_DESCRIPTIONS = {
    "未检测": "无花粉",
    "很低": "不易引发过敏反应",
    "较低": "对极敏感人群可能引发过敏反应",
    "偏高": "易引发过敏，加强防护，对症用药",
    "较高": "易引发过敏，加强防护，规范用药",
    "很高": "极易引发过敏，减少外出，持续规范用药",
    "极高": "极易引发过敏，建议足不出户，规范用药",
    "暂无": "暂无数据"
}

# 花粉季节周期（月份）
# 这些信息用于展示或告知用户花粉高发季节
POLLEN_SEASONS = {
    "北方": {
        "spring": [3, 4, 5],      # 春季花粉（树木花粉为主）
        "summer": [6, 7, 8],      # 夏季花粉（草本花粉为主）
        "fall": [9, 10]           # 秋季花粉（杂草花粉为主）
    },
    "南方": {
        "spring": [2, 3, 4],      # 南方春季花粉开始更早
        "summer": [5, 6, 7],
        "fall": [8, 9, 10]  
    }
}

# 建议的数据过滤设置
FILTERING_SUGGESTIONS = {
    "min_record_count": 5,        # 每个城市至少需要的记录数
    "max_date_range": 90,         # 日期范围的最大天数（避免图表过于拥挤）
    "preferred_cities_count": 8    # 推荐同时显示的最大城市数量
}

# 数据预处理选项
PREPROCESSING_OPTIONS = {
    "interpolate_missing": True,   # 是否对缺失值进行插值
    "smoothing": False,            # 是否对数据进行平滑处理
    "smoothing_window": 3          # 平滑窗口大小
} 