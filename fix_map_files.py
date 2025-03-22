#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复地图HTML文件中的JavaScript语法错误
"""

import os
import re
import glob

def fix_formatter_function(html_content):
    """
    修复格式化函数的语法错误
    """
    # 定义用于匹配formatter函数的正则表达式
    pattern = r'"formatter": function\(params\) \{([^}]*)\},'
    
    # 替换函数
    def formatter_replacement(match):
        # 获取原始内容
        content = match.group(1)
        
        # 格式化JavaScript代码
        formatted_js = """function(params) {
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
                
                // 检测是否为移动设备，如果是则添加提示
                var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
                var touchTip = isMobile ? '<br/>(点击可放大地图)' : '';
                
                return params.name + '<br/>花粉等级: ' + levelText + touchTip;
            }"""
        
        return f'"formatter": {formatted_js},'
    
    # 使用正则表达式查找并替换
    fixed_content = re.sub(pattern, formatter_replacement, html_content)
    
    return fixed_content

def fix_map_files(directory):
    """
    修复目录中所有地图HTML文件
    """
    map_files = glob.glob(os.path.join(directory, "map_*.html"))
    print(f"找到 {len(map_files)} 个地图文件需要修复")
    
    for file_path in map_files:
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修复内容
            fixed_content = fix_formatter_function(content)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
                
            print(f"✓ 已修复: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"✗ 修复失败 {os.path.basename(file_path)}: {str(e)}")

if __name__ == "__main__":
    maps_dir = "docs/maps"
    if os.path.exists(maps_dir):
        fix_map_files(maps_dir)
    else:
        print(f"错误: 目录 {maps_dir} 不存在") 