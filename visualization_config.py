#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据可视化配置文件
此文件包含了花粉数据可视化所需的配置信息，如颜色映射、标签等
"""

import os
import sys
import matplotlib.font_manager as fm

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

# 自动检测可用字体
AVAILABLE_FONTS = find_available_fonts()
PRIMARY_FONT = AVAILABLE_FONTS[0] if AVAILABLE_FONTS else 'sans-serif'

# 尝试检测中文字体
CJK_FONT = next((font for font in AVAILABLE_FONTS[1:] if font in [
    'SimHei', 'Microsoft YaHei', 'SimSun', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC',
    'Source Han Sans CN', 'Droid Sans Fallback', 'PingFang SC', 'STHeiti'
]), None)

print(f"检测到可用字体: {', '.join(AVAILABLE_FONTS) if AVAILABLE_FONTS else '无'}")
print(f"将使用主要字体: {PRIMARY_FONT}" + (f", 中文字体: {CJK_FONT}" if CJK_FONT else ""))

# 配置字体回退设置
def configure_matplotlib_fonts():
    """配置matplotlib字体设置以支持中文和拉丁字符"""
    import matplotlib.pyplot as plt
    import warnings
    
    try:
        # 设置matplotlib全局字体
        plt.rcParams['font.family'] = 'sans-serif'
        
        # 添加字体回退顺序
        if CJK_FONT:
            plt.rcParams['font.sans-serif'] = [PRIMARY_FONT, CJK_FONT] + plt.rcParams['font.sans-serif']
        else:
            plt.rcParams['font.sans-serif'] = [PRIMARY_FONT] + plt.rcParams['font.sans-serif']
        
        # 用来正常显示负号
        plt.rcParams['axes.unicode_minus'] = False
        
        # 关闭字体警告
        warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
        
        return True
    except Exception as e:
        print(f"配置字体时出错: {str(e)}")
        return False

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

# 图表默认设置
CHART_CONFIG = {
    # 图表尺寸
    "figsize": (12, 8),
    
    # 标题
    "title_fontsize": 16,
    "title_style": {
        "fontname": PRIMARY_FONT,
        "fontweight": "bold"
    },
    
    # 坐标轴
    "axis_fontsize": 12,
    "axis_label_style": {
        "fontname": PRIMARY_FONT
    },
    
    # 图例
    "legend_fontsize": 10,
    "legend_style": {
        "fontname": PRIMARY_FONT
    },
    
    # 线条
    "line_width": 2.5,
    "line_style": "-",
    "marker_size": 8,
    "marker_style": "o",
    
    # 网格
    "grid_enabled": True,
    "grid_alpha": 0.3,
    "grid_style": "--",
    
    # 保存设置
    "dpi": 300,
    "bbox_inches": "tight",
    "transparent": False
}

# 默认输出目录
DEFAULT_OUTPUT_DIR = "visualization_output"

# 默认文件名模板
DEFAULT_FILENAME_TEMPLATE = "pollen_trends_{date}.png"

# 日期格式
DATE_FORMAT = "%Y-%m-%d"
DATE_FORMAT_DISPLAY = "%Y-%m-%d"  # 如果没有中文字体，使用标准日期格式

# 中文字体设置（适用于matplotlib）
FONT_FAMILY = PRIMARY_FONT  # 使用自动检测到的可用字体

# 颜色渐变设置
COLORMAP_NAME = "viridis"  # matplotlib 颜色映射名称

# 图表批注设置
ANNOTATION_CONFIG = {
    "fontsize": 9,
    "fontname": PRIMARY_FONT,
    "bbox": {
        "boxstyle": "round,pad=0.3", 
        "fc": "white", 
        "alpha": 0.7,
        "ec": "gray"
    },
    "arrowprops": {
        "arrowstyle": "->",
        "connectionstyle": "arc3,rad=0.2",
        "alpha": 0.7
    }
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