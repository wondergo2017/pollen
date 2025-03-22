#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
import sys
import matplotlib.font_manager as fm

# 导入配置文件
try:
    from visualization_config import (
        LEVEL_COLORS, LEVEL_NUMERIC_MAP, LEVEL_DESCRIPTIONS, 
        CHART_CONFIG, DEFAULT_OUTPUT_DIR, DEFAULT_FILENAME_TEMPLATE, 
        DATE_FORMAT, DATE_FORMAT_DISPLAY, FONT_FAMILY, 
        COLORMAP_NAME, ANNOTATION_CONFIG, POLLEN_SEASONS, 
        FILTERING_SUGGESTIONS, PREPROCESSING_OPTIONS,
        AVAILABLE_FONTS, PRIMARY_FONT  # 添加新的自动字体配置变量
    )
    print("已加载可视化配置文件")
except ImportError as e:
    print(f"警告：导入可视化配置文件时出错: {str(e)}")
    print("将使用默认设置")
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
    FONT_FAMILY = PRIMARY_FONT
    
    print(f"检测到可用字体: {', '.join(AVAILABLE_FONTS) if AVAILABLE_FONTS else '无'}")
    print(f"将使用字体: {PRIMARY_FONT}")
    
    # 默认配置
    LEVEL_COLORS = {
        "未检测": "#999999",  # 灰色
        "很低": "#81CB31",    # 绿色
        "较低": "#A1FF3D",    # 浅绿色
        "偏高": "#F5EE32",    # 黄色
        "较高": "#FFAF13",    # 橙色
        "很高": "#FF2319",    # 红色
        "极高": "#AD075D",    # 紫色
        "暂无": "#C4A39F",    # 浅灰色
    }
    
    LEVEL_NUMERIC_MAP = {
        "未检测": 0,
        "很低": 1,
        "较低": 2,
        "偏高": 3,
        "较高": 4,
        "很高": 5,
        "极高": 6,
        "暂无": -1,
    }
    
    CHART_CONFIG = {
        "figsize": (14, 8),
        "title_fontsize": 18,
        "axis_fontsize": 14,
        "legend_fontsize": 12,
        "line_width": 2,
        "marker_size": 8,
        "grid_enabled": True,
        "grid_alpha": 0.7,
        "dpi": 300,
    }
    
    DEFAULT_OUTPUT_DIR = "visualization_output"
    DEFAULT_FILENAME_TEMPLATE = "pollen_trends_{date}.png"
    DATE_FORMAT = "%Y-%m-%d"
    DATE_FORMAT_DISPLAY = "%Y-%m-%d"  # 使用标准日期格式
    PREPROCESSING_OPTIONS = {"interpolate_missing": False}
    FILTERING_SUGGESTIONS = {
        "min_record_count": 5,
        "preferred_cities_count": 8,
        "max_date_range": 90
    }
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
    COLORMAP_NAME = "viridis"
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
    POLLEN_SEASONS = {
        "北方": {
            "spring": [3, 4, 5],
            "summer": [6, 7, 8],
            "fall": [9, 10]
        },
        "南方": {
            "spring": [2, 3, 4],
            "summer": [5, 6, 7],
            "fall": [8, 9, 10]
        }
    }

def create_level_colormap():
    """创建花粉等级对应的颜色映射"""
    # 使用配置中的颜色映射
    return LEVEL_COLORS

def level_to_numeric(level):
    """将花粉等级转换为数值，用于可视化"""
    # 使用配置中的数值映射
    return LEVEL_NUMERIC_MAP.get(level, -1)

def load_data(file_path):
    """加载花粉数据文件"""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("不支持的文件格式，请提供CSV或Excel文件。")
    
    # 确保数据包含必要的列
    required_columns = ['city', 'addTime', 'level']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"数据文件缺少必要的列: {', '.join(missing_columns)}")
    
    # 转换日期列为日期时间类型
    df['addTime'] = pd.to_datetime(df['addTime'])
    
    # 添加数值化等级列
    if 'level_numeric' not in df.columns:
        df['level_numeric'] = df['level'].apply(level_to_numeric)
    
    # 数据预处理
    if 'PREPROCESSING_OPTIONS' in globals() and PREPROCESSING_OPTIONS.get("interpolate_missing", False):
        df = interpolate_missing_data(df)
    
    return df

def interpolate_missing_data(df):
    """对缺失的数据进行插值处理"""
    # 按城市分组
    grouped = df.groupby('city')
    interpolated_dfs = []
    
    for city, city_data in grouped:
        # 按日期排序
        city_data = city_data.sort_values('addTime')
        
        # 如果有缺失值并且配置了插值
        if city_data['level_numeric'].isna().any():
            # 线性插值填充缺失的数值等级
            city_data['level_numeric'] = city_data['level_numeric'].interpolate(method='linear')
            
            # 根据数值等级更新文本等级
            reverse_map = {v: k for k, v in LEVEL_NUMERIC_MAP.items() if v >= 0}
            city_data.loc[city_data['level'].isna(), 'level'] = city_data.loc[
                city_data['level'].isna(), 'level_numeric'
            ].apply(lambda x: reverse_map.get(round(x), '未检测'))
        
        interpolated_dfs.append(city_data)
    
    # 合并处理后的数据
    return pd.concat(interpolated_dfs)

def filter_data(df, cities=None, start_date=None, end_date=None):
    """根据条件过滤数据"""
    # 复制一份数据，避免修改原始数据
    filtered_df = df.copy()
    
    # 过滤城市
    if cities:
        filtered_df = filtered_df[filtered_df['city'].isin(cities)]
    
    # 过滤日期范围
    if start_date:
        start_date = pd.to_datetime(start_date)
        filtered_df = filtered_df[filtered_df['addTime'] >= start_date]
    
    if end_date:
        end_date = pd.to_datetime(end_date)
        filtered_df = filtered_df[filtered_df['addTime'] <= end_date]
    
    # 检查过滤后的数据量
    if len(filtered_df) == 0:
        print("警告：过滤后没有剩余数据，请检查过滤条件。")
    elif 'FILTERING_SUGGESTIONS' in globals() and filtered_df['city'].nunique() > FILTERING_SUGGESTIONS.get("preferred_cities_count", 8):
        print(f"警告：选择的城市数量 ({filtered_df['city'].nunique()}) 较多，图表可能会变得拥挤。")
    
    return filtered_df

def prepare_data_for_visualization(df):
    """准备可视化数据，对每个城市按日期进行排序"""
    # 按城市分组，然后按日期排序
    return df.sort_values(['city', 'addTime'])

def create_advanced_charts(df, output_dir=DEFAULT_OUTPUT_DIR):
    """创建高级图表，包括月度对比、季节分析等"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 获取数据的日期范围
    min_date = df['addTime'].min()
    max_date = df['addTime'].max()
    date_range = (max_date - min_date).days
    
    charts_info = []
    
    # 1. 创建月度对比图（如果日期范围超过60天）
    if date_range >= 60:
        months = pd.DatetimeIndex(df['addTime']).month.unique()
        
        for month in months:
            month_data = df[pd.DatetimeIndex(df['addTime']).month == month]
            month_name = pd.to_datetime(f"2023-{month}-01").strftime("%B")
            
            # 生成月度趋势图
            month_output = os.path.join(output_dir, f"monthly_trend_{month_name}.png")
            visualize_pollen_trends(month_data, output_dir, f"monthly_trend_{month_name}.png")
            charts_info.append({
                "type": "monthly",
                "month": month_name,
                "file": month_output,
                "cities": month_data['city'].nunique(),
                "records": len(month_data)
            })
    
    # 2. 生成城市对比热图
    if df['city'].nunique() >= 3:
        try:
            import seaborn as sns
            heatmap_output = os.path.join(output_dir, "city_comparison_heatmap.png")
            create_city_comparison_heatmap(df, heatmap_output)
            charts_info.append({
                "type": "heatmap",
                "file": heatmap_output,
                "cities": df['city'].nunique()
            })
        except ImportError:
            print("警告：未找到seaborn库，无法创建热图。请安装seaborn库：pip install seaborn")
    
    return charts_info

def create_city_comparison_heatmap(df, output_file):
    """创建城市对比热图"""
    try:
        import seaborn as sns
        
        # 按城市和日期分组，计算平均花粉等级
        pivot_data = df.pivot_table(
            index='city', 
            columns=pd.Grouper(key='addTime', freq='D'),
            values='level_numeric',
            aggfunc='mean'
        )
        
        # 创建热图
        plt.figure(figsize=CHART_CONFIG.get("figsize", (12, 8)))
        
        # 使用配置中的字体设置
        try:
            # 设置全局字体
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = [FONT_FAMILY] + plt.rcParams['font.sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
        except Exception as e:
            print(f"热图字体设置警告: {str(e)}")
        
        # 创建热图
        cmap = sns.color_palette("viridis", as_cmap=True)
        if 'COLORMAP_NAME' in globals():
            try:
                cmap = sns.color_palette(COLORMAP_NAME, as_cmap=True)
            except:
                pass
                
        sns_heatmap = sns.heatmap(
            pivot_data, 
            cmap=cmap,
            linewidths=0.5,
            annot=False,
            fmt=".1f"
        )
        
        plt.title('城市花粉等级热力图对比', 
                 fontsize=CHART_CONFIG.get("title_fontsize", 16))
        plt.xlabel('日期', fontsize=CHART_CONFIG.get("axis_fontsize", 12))
        plt.ylabel('城市', fontsize=CHART_CONFIG.get("axis_fontsize", 12))
        plt.xticks(rotation=45)
        
        # 保存图表
        plt.tight_layout()
        plt.savefig(
            output_file, 
            dpi=CHART_CONFIG.get("dpi", 300),
            bbox_inches='tight'
        )
        plt.close()
        
        return output_file
    except ImportError:
        print("警告：未找到seaborn库，无法创建热图。请安装seaborn库：pip install seaborn")
        return None
    except Exception as e:
        print(f"创建热图时出错: {str(e)}")
        return None

def visualize_pollen_trends(df, output_dir=DEFAULT_OUTPUT_DIR, output_file=None):
    """可视化花粉等级趋势"""
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 获取唯一城市列表
    cities = df['city'].unique()
    
    # 设置中文字体
    try:
        # 导入所需模块
        import warnings
        
        # 尝试寻找更多可用的中文字体
        chinese_fonts = [
            'SimHei', 'Microsoft YaHei', 'SimSun', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC',
            'Source Han Sans CN', 'Droid Sans Fallback', 'PingFang SC', 'Heiti SC', 'STHeiti'
        ]
        
        # 拉丁字符字体
        latin_fonts = [
            'DejaVu Sans', 'Liberation Sans', 'Arial', 'Helvetica', 'Verdana', 'Tahoma'
        ]
        
        # 检查系统中可用的字体
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        # 先选择拉丁字符字体，确保数字和英文字母可正常显示
        latin_font = next((font for font in latin_fonts if font in available_fonts), 'sans-serif')
        
        # 再选择中文字体，确保中文字符可正常显示
        cjk_font = next((font for font in chinese_fonts if font in available_fonts), None)
        
        # 设置matplotlib全局字体
        plt.rcParams['font.family'] = 'sans-serif'
        if cjk_font:
            plt.rcParams['font.sans-serif'] = [latin_font, cjk_font] + plt.rcParams['font.sans-serif']
            print(f"设置字体成功：主要字体 {latin_font}，中文字体 {cjk_font}")
        else:
            plt.rcParams['font.sans-serif'] = [latin_font] + plt.rcParams['font.sans-serif']
            print(f"设置字体成功：主要字体 {latin_font}，未找到合适的中文字体")
            
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
        # 设置自定义字体属性
        if cjk_font:
            # 为中文文本创建一个FontProperties对象
            font_prop = fm.FontProperties(family=[latin_font, cjk_font])
        else:
            font_prop = fm.FontProperties(family=latin_font)
        
        # 关闭字体警告
        warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
    except Exception as e:
        print(f"警告：字体设置遇到问题: {str(e)}")
        print(f"将使用系统默认字体。图表中的中文可能显示为方块。")
        
        # 退回到基本设置
        plt.rcParams['font.family'] = 'sans-serif'
        if 'AVAILABLE_FONTS' in globals() and AVAILABLE_FONTS:
            plt.rcParams['font.sans-serif'] = AVAILABLE_FONTS + plt.rcParams['font.sans-serif']
        
        # 使用默认字体属性
        font_prop = fm.FontProperties()
    
    # 创建图表
    fig, ax = plt.subplots(figsize=CHART_CONFIG.get("figsize", (14, 8)))
    
    # 花粉等级颜色
    level_colors = create_level_colormap()
    
    # 为每个城市绘制一条线
    for i, city in enumerate(cities):
        city_data = df[df['city'] == city].sort_values('addTime')
        
        # 确保数据按日期排序
        dates = city_data['addTime']
        levels = city_data['level_numeric']
        
        # 使用缩写的城市名称以避免图例过长
        short_city_name = city if len(cities) <= 5 else city[:2]
        
        # 画线图
        line = ax.plot(
            dates, levels, 'o-', 
            label=city, 
            linewidth=CHART_CONFIG.get("line_width", 2),
            markersize=CHART_CONFIG.get("marker_size", 8) * 0.5,  # 线上的标记点稍小
        )
        
        # 为每个数据点上色
        for j, (date, level, lvl_str) in enumerate(zip(dates, levels, city_data['level'])):
            if level >= 0 and lvl_str in level_colors:
                ax.plot(date, level, 'o', 
                       color=level_colors[lvl_str], 
                       markersize=CHART_CONFIG.get("marker_size", 8))
    
    # 设置Y轴刻度和标签
    ax.set_yticks(range(7))
    y_labels = ['未检测', '很低', '较低', '偏高', '较高', '很高', '极高']
    ax.set_yticklabels(y_labels, fontproperties=font_prop)
    
    # 设置图表标题和标签
    ax.set_title('各城市花粉等级随时间变化趋势', fontsize=CHART_CONFIG.get("title_fontsize", 18), fontproperties=font_prop)
    ax.set_xlabel('日期', fontsize=CHART_CONFIG.get("axis_fontsize", 14), fontproperties=font_prop)
    ax.set_ylabel('花粉等级', fontsize=CHART_CONFIG.get("axis_fontsize", 14), fontproperties=font_prop)
    
    # 设置日期格式
    ax.xaxis.set_major_formatter(mdates.DateFormatter(DATE_FORMAT))
    fig.autofmt_xdate()  # 自动调整日期标签的旋转角度
    
    # 添加网格
    if CHART_CONFIG.get("grid_enabled", True):
        ax.grid(
            True, 
            linestyle=CHART_CONFIG.get("grid_style", "--"), 
            alpha=CHART_CONFIG.get("grid_alpha", 0.7)
        )
    
    # 添加图例
    ax.legend(loc='upper right', fontsize=CHART_CONFIG.get("legend_fontsize", 12), prop=font_prop)
    
    # 添加花粉等级说明
    if len(cities) <= 3 and 'LEVEL_DESCRIPTIONS' in globals():  # 只在城市较少时添加说明，避免拥挤
        # 添加花粉等级说明文本框
        level_info = "\n".join([
            f"{level}: {LEVEL_DESCRIPTIONS.get(level, '')}"
            for level in ['很低', '偏高', '很高', '极高']
        ])
        
        plt.figtext(
            0.02, 0.02, 
            f"花粉等级说明:\n{level_info}", 
            fontsize=9,
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'),
            verticalalignment='bottom'
        )
    
    # 添加边框
    for spine in ax.spines.values():
        spine.set_visible(True)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    if output_file:
        output_path = os.path.join(output_dir, output_file)
    else:
        # 生成包含当前日期的文件名
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            output_dir, 
            DEFAULT_FILENAME_TEMPLATE.format(date=now)
        )
    
    plt.savefig(
        output_path, 
        dpi=CHART_CONFIG.get("dpi", 300),
        bbox_inches=CHART_CONFIG.get("bbox_inches", 'tight'),
        transparent=CHART_CONFIG.get("transparent", False)
    )
    print(f"图表已保存为: {output_path}")
    
    # 显示图表
    plt.close()
    
    return output_path

def create_distribution_chart(df, output_dir=DEFAULT_OUTPUT_DIR):
    """创建花粉等级分布图表"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 统计各城市不同花粉等级的分布
    city_level_counts = df.groupby(['city', 'level']).size().unstack(fill_value=0)
    
    # 设置图表大小
    plt.figure(figsize=CHART_CONFIG.get("figsize", (12, 8)))
    
    # 设置字体 - 确保使用与主图表相同的字体设置
    try:
        # 导入所需模块
        import warnings
        
        # 与主图表相同的字体设置
        chinese_fonts = [
            'SimHei', 'Microsoft YaHei', 'SimSun', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC',
            'Source Han Sans CN', 'Droid Sans Fallback', 'PingFang SC', 'Heiti SC', 'STHeiti'
        ]
        
        latin_fonts = [
            'DejaVu Sans', 'Liberation Sans', 'Arial', 'Helvetica', 'Verdana', 'Tahoma'
        ]
        
        # 检查系统中可用的字体
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        latin_font = next((font for font in latin_fonts if font in available_fonts), 'sans-serif')
        cjk_font = next((font for font in chinese_fonts if font in available_fonts), None)
        
        # 设置全局字体
        plt.rcParams['font.family'] = 'sans-serif'
        if cjk_font:
            plt.rcParams['font.sans-serif'] = [latin_font, cjk_font] + plt.rcParams['font.sans-serif']
        else:
            plt.rcParams['font.sans-serif'] = [latin_font] + plt.rcParams['font.sans-serif']
            
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
        # 设置自定义字体属性
        if cjk_font:
            font_prop = fm.FontProperties(family=[latin_font, cjk_font])
        else:
            font_prop = fm.FontProperties(family=latin_font)
        
        # 关闭字体警告
        warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
    except Exception as e:
        print(f"分布图字体设置警告: {str(e)}")
        font_prop = fm.FontProperties()
    
    # 绘制柱状图
    city_level_counts.plot(
        kind='bar', 
        stacked=True, 
        width=0.8
    )
    
    # 设置图表标题和标签
    plt.title('各城市花粉等级分布统计', fontsize=CHART_CONFIG.get("title_fontsize", 16))
    plt.xlabel('城市', fontsize=CHART_CONFIG.get("axis_fontsize", 12))
    plt.ylabel('天数', fontsize=CHART_CONFIG.get("axis_fontsize", 12))
    
    # 调整图例
    plt.legend(title='花粉等级', fontsize=CHART_CONFIG.get("legend_fontsize", 10))
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    output_path = os.path.join(output_dir, 'pollen_level_distribution.png')
    plt.savefig(
        output_path,
        dpi=CHART_CONFIG.get("dpi", 300),
        bbox_inches=CHART_CONFIG.get("bbox_inches", 'tight')
    )
    plt.close()
    
    return output_path

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='花粉等级数据可视化工具')
    parser.add_argument('data_file', help='花粉数据文件路径 (CSV或Excel格式)')
    parser.add_argument('--cities', nargs='+', help='要显示的城市列表 (例如: 北京 上海)')
    parser.add_argument('--start_date', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end_date', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--output', help='输出文件名')
    parser.add_argument('--output_dir', default=DEFAULT_OUTPUT_DIR, help='输出目录')
    parser.add_argument('--advanced', action='store_true', help='生成高级图表')
    parser.add_argument('--distribution', action='store_true', help='生成分布统计图表')
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    # 加载数据
    print(f"正在加载数据文件: {args.data_file}...")
    df = load_data(args.data_file)
    print(f"共加载了 {len(df)} 条记录，包含 {df['city'].nunique()} 个城市的数据。")
    
    # 过滤数据
    df = filter_data(df, args.cities, args.start_date, args.end_date)
    if len(df) == 0:
        print("错误：过滤后没有剩余数据，请检查过滤条件。")
        return
    
    print(f"过滤后剩余 {len(df)} 条记录，包含 {df['city'].nunique()} 个城市的数据。")
    
    # 准备可视化数据
    df = prepare_data_for_visualization(df)
    
    # 可视化数据
    output_paths = []
    
    # 生成主趋势图
    trend_path = visualize_pollen_trends(df, args.output_dir, args.output)
    output_paths.append({"type": "trend", "path": trend_path})
    
    # 生成高级图表
    if args.advanced:
        print("\n生成高级图表...")
        advanced_charts = create_advanced_charts(df, args.output_dir)
        for chart in advanced_charts:
            output_paths.append({"type": "advanced", "info": chart})
    
    # 生成分布统计图
    if args.distribution:
        print("\n生成花粉等级分布统计图...")
        dist_path = create_distribution_chart(df, args.output_dir)
        output_paths.append({"type": "distribution", "path": dist_path})
    
    print("\n可视化完成！所有图表已保存至目录: {}".format(os.path.abspath(args.output_dir)))
    
    # 打印生成的图表列表
    if len(output_paths) > 1:
        print("\n生成的图表列表:")
        for i, output in enumerate(output_paths, 1):
            if output["type"] == "trend":
                print(f"{i}. 趋势图: {os.path.basename(output['path'])}")
            elif output["type"] == "distribution":
                print(f"{i}. 分布统计图: {os.path.basename(output['path'])}")
            elif output["type"] == "advanced" and "info" in output:
                info = output["info"]
                if info["type"] == "monthly":
                    print(f"{i}. {info['month']}月趋势图: {os.path.basename(info['file'])}")
                elif info["type"] == "heatmap":
                    print(f"{i}. 城市对比热图: {os.path.basename(info['file'])}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 