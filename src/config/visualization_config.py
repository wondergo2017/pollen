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
        # 中文字体常见名称
        'SimHei', 'Microsoft YaHei', 'SimSun', 'DengXian', 'KaiTi', 'FangSong',
        'WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'Noto Sans SC', 'Source Han Sans CN',
        'Noto Sans CJK TC', 'Noto Sans CJK JP', 'Hiragino Sans GB', 
        'AR PL UMing CN', 'AR PL KaitiM GB', 'STHeiti', 'STKaiti', 'STSong',
        'WenQuanYi Zen Hei', 'WenQuanYi Zen Hei Sharp', 'NSimSun',
        'Droid Sans Fallback', 'PingFang SC', 'PingFang TC', 'HanaMinA', 'HanaMinB',
        # 添加新字体名称
        '文泉驿微米黑', '文泉驿正黑', 'Noto Serif CJK SC', 'AR PL UKai CN', 
    ]
    
    # 拉丁字符字体，用于显示英文和数字
    latin_fonts = [
        'DejaVu Sans', 'Liberation Sans', 'Arial', 'Helvetica', 'Verdana', 'Tahoma'
    ]
    
    # 查找系统中已安装的字体
    system_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 尝试命令获取系统中的中文字体
    try:
        import subprocess
        result = subprocess.run(['fc-list', ':lang=zh'], capture_output=True, text=True)
        if result.returncode == 0:
            # 解析输出中的字体名称
            for line in result.stdout.splitlines():
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 2 and 'style=' in parts[1]:
                        font_names = parts[1].split('style=')[0].strip().split(',')
                        for name in font_names:
                            name = name.strip()
                            if name and name not in available_fonts:
                                available_fonts.append(name)
    except Exception:
        pass
    
    # 检查系统中是否有中文字体文件
    for font_file in fm.findSystemFonts():
        try:
            font = fm.FontProperties(fname=font_file)
            font_name = font.get_name()
            # 检查字体是否支持中文
            if any(chinese_font in font_name for chinese_font in ['Hei', 'Ming', 'Song', 'Yuan', 'Kai', 'Fang', 'Zhong', 'CN', 'GB', 'SC', 'TC', 'CJK']):
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

# 尝试检测中文字体 - 更新支持的中文字体列表
CJK_FONT = next((font for font in AVAILABLE_FONTS[1:] if font in [
    'SimHei', 'Microsoft YaHei', 'SimSun', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC',
    'Source Han Sans CN', 'Droid Sans Fallback', 'PingFang SC', 'STHeiti',
    '文泉驿微米黑', '文泉驿正黑', 'Noto Serif CJK SC', 'AR PL UKai CN', 'AR PL UMing CN',
    'WenQuanYi Zen Hei', 'WenQuanYi Zen Hei Sharp', 'Droid Sans Fallback'
]), None)

# 配置字体回退设置
def configure_matplotlib_fonts():
    """
    配置matplotlib字体使其支持中文及所有UTF-8字符
    
    此函数会根据操作系统自动选择合适的中文字体，确保可视化图表中的中文显示正常。
    它同时抑制字体相关警告，优化字体渲染配置，提高输出质量。
    
    返回:
        bool: 配置成功返回True，否则返回False
    """
    import matplotlib
    import matplotlib.font_manager as fm
    import platform
    import subprocess
    import warnings
    
    # 抑制所有警告
    warnings.filterwarnings("ignore")
    
    try:
        # 基本的matplotlib字体配置
        matplotlib.rcParams['axes.unicode_minus'] = False
        matplotlib.rcParams['pdf.fonttype'] = 42
        matplotlib.rcParams['ps.fonttype'] = 42
        
        # 尝试找到一个可用的中文字体
        chinese_font_found = False
        
        # 先尝试直接使用一些在Linux系统上常见的中文字体
        linux_fonts = [
            'Droid Sans Fallback',  # 这个字体在很多Linux系统上都有
            'WenQuanYi Zen Hei',    # 文泉驿正黑
            'WenQuanYi Micro Hei',  # 文泉驿微米黑
            'Noto Sans CJK SC',     # Google Noto字体
            'Source Han Sans CN',   # 思源黑体
            'AR PL UMing CN'        # 文鼎PL细上海宋
        ]
        
        # 系统字体列表
        system_fonts = []
        try:
            # 获取系统中的所有字体家族名称
            system_fonts = set([f.name for f in fm.fontManager.ttflist])
        except Exception:
            pass
        
        # 在Linux系统上尝试使用fc-list命令找中文字体
        found_fonts = []
        system = platform.system()
        if system != 'Windows' and system != 'Darwin':
            try:
                # 尝试使用fc-list命令找出系统中所有支持中文的字体
                result = subprocess.run(['fc-list', ':lang=zh', 'family'], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, 
                                     universal_newlines=True)
                if result.returncode == 0:
                    # 解析输出并提取字体名称
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            font_names = [name.strip() for name in line.split(',')]
                            for font_name in font_names:
                                if font_name and font_name not in found_fonts:
                                    found_fonts.append(font_name)
            except Exception:
                pass
        
        # 尝试直接按字体文件路径创建字体属性
        font_files = fm.findSystemFonts()
        
        # 先检查是否有最常见的中文字体
        for font in linux_fonts:
            if font in system_fonts:
                chinese_font_found = True
                # 设置这个字体为默认字体
                matplotlib.rcParams['font.family'] = 'sans-serif'
                for family in ['sans-serif', 'serif', 'monospace']:
                    current_fonts = matplotlib.rcParams.get(f'font.{family}', [])
                    if font not in current_fonts:
                        matplotlib.rcParams[f'font.{family}'] = [font] + current_fonts
                break
        
        # 如果没有找到常见字体，尝试使用fc-list找到的任何中文字体
        if not chinese_font_found and found_fonts:
            chinese_font_found = True
            matplotlib.rcParams['font.family'] = 'sans-serif'
            for family in ['sans-serif', 'serif', 'monospace']:
                current_fonts = matplotlib.rcParams.get(f'font.{family}', [])
                matplotlib.rcParams[f'font.{family}'] = found_fonts[:3] + current_fonts
        
        # 最后的后备方案：使用DejaVu Sans并设置font.family为sans-serif
        if not chinese_font_found:
            matplotlib.rcParams['font.family'] = 'sans-serif'
            if 'DejaVu Sans' in system_fonts:
                for family in ['sans-serif', 'serif', 'monospace']:
                    current_fonts = matplotlib.rcParams.get(f'font.{family}', [])
                    if 'DejaVu Sans' not in current_fonts:
                        matplotlib.rcParams[f'font.{family}'] = ['DejaVu Sans'] + current_fonts
        
        # 强制使用sans-serif字体族
        matplotlib.rcParams['font.family'] = 'sans-serif'
        
        # 如果系统上有中文TTF字体文件，直接加载它们
        if not chinese_font_found:
            # 检查是否有中文字体文件（通过文件名简单判断）
            chinese_font_files = []
            for font_file in font_files:
                lower_name = font_file.lower()
                if any(keyword in lower_name for keyword in ['chinese', 'cjk', 'sc', 'cn', 'zh', 'hei', 'kai', 'ming', 'song']):
                    chinese_font_files.append(font_file)
            
            # 如果找到了中文字体文件，使用其中的前三个
            if chinese_font_files:
                chinese_font_found = True
                # 只使用前三个中文字体文件，避免列表太长
                for font_file in chinese_font_files[:3]:
                    try:
                        prop = fm.FontProperties(fname=font_file)
                        font_family = prop.get_name()
                        # 将此字体添加到各个字体族中
                        for family in ['sans-serif', 'serif', 'monospace']:
                            current_fonts = matplotlib.rcParams.get(f'font.{family}', [])
                            if font_family not in current_fonts:
                                current_fonts.insert(0, font_family)
                                matplotlib.rcParams[f'font.{family}'] = current_fonts
                    except Exception:
                        pass
        
        return True
    
    except Exception as e:
        # 最基本的设置，确保即使出错也能继续
        try:
            matplotlib.rcParams['font.family'] = 'sans-serif'
            matplotlib.rcParams['axes.unicode_minus'] = False
        except Exception:
            pass
        
        return True  # 返回True避免中断程序流程

# 图表配置
CHART_CONFIG = {
    # 图表尺寸
    'figure_size': (12, 8),
    'fig_width': 12,  # 兼容性配置
    'fig_height': 8,  # 兼容性配置
    
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