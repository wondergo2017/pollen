#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
地图部署测试脚本
用于测试地图生成和部署过程
"""

import os
import sys
import subprocess
import argparse
import shutil

def run_command(command, cwd=None):
    """运行命令并打印输出"""
    print(f"执行命令: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        cwd=cwd
    )
    stdout, stderr = process.communicate()
    
    if stdout:
        print(f"标准输出:\n{stdout}")
    if stderr:
        print(f"错误输出:\n{stderr}")
    
    return process.returncode, stdout, stderr

def test_map_generation(data_file, output_dir):
    """测试地图生成功能"""
    print("=" * 60)
    print("测试地图生成")
    print("=" * 60)
    
    # 创建临时输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 运行地图生成脚本
    cmd = f"python static_map_generator.py -f {data_file} -o {output_dir}"
    exit_code, _, _ = run_command(cmd)
    
    if exit_code != 0:
        print(f"错误: 地图生成失败，退出代码 {exit_code}")
        return False
    
    # 检查生成的文件
    index_file = os.path.join(output_dir, "index.html")
    maps_dir = os.path.join(output_dir, "maps")
    
    if not os.path.exists(index_file):
        print(f"错误: 未找到主页文件 {index_file}")
        return False
    
    if not os.path.exists(maps_dir) or not os.path.isdir(maps_dir):
        print(f"错误: 未找到地图目录 {maps_dir}")
        return False
    
    map_files = [f for f in os.listdir(maps_dir) if f.endswith('.html')]
    if not map_files:
        print(f"错误: 地图目录中没有找到HTML文件")
        return False
    
    print(f"成功: 找到 {len(map_files)} 个地图文件")
    print(f"主页文件: {index_file}")
    print(f"地图目录: {maps_dir}")
    print(f"示例地图文件: {map_files[0]}")
    
    return True

def test_deployment_structure(output_dir):
    """测试部署结构是否正确"""
    print("=" * 60)
    print("测试部署结构")
    print("=" * 60)
    
    # 检查目录结构
    index_file = os.path.join(output_dir, "index.html")
    maps_dir = os.path.join(output_dir, "maps")
    
    if not os.path.exists(index_file):
        print(f"错误: 未找到主页文件 {index_file}")
        return False
    
    # 读取index.html文件内容
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            index_content = f.read()
            
        if 'maps/map_' not in index_content:
            print("警告: index.html中可能缺少对地图文件的引用")
    except Exception as e:
        print(f"错误: 读取index.html时出错: {str(e)}")
    
    if not os.path.exists(maps_dir) or not os.path.isdir(maps_dir):
        print(f"错误: 未找到地图目录 {maps_dir}")
        return False
    
    map_files = [f for f in os.listdir(maps_dir) if f.endswith('.html')]
    if not map_files:
        print(f"错误: 地图目录中没有找到HTML文件")
        return False
    
    # 检查地图文件内容
    try:
        map_file_path = os.path.join(maps_dir, map_files[0])
        with open(map_file_path, 'r', encoding='utf-8') as f:
            map_content = f.read()
            
        # 检查是否包含echarts脚本引用
        if 'echarts.min.js' not in map_content:
            print("警告: 地图文件可能缺少echarts.min.js引用")
            
        # 检查是否包含中国地图数据
        if 'china.js' not in map_content:
            print("警告: 地图文件可能缺少china.js引用")
    except Exception as e:
        print(f"错误: 读取地图文件时出错: {str(e)}")
    
    print(f"成功: 部署结构看起来正确")
    return True

def main():
    parser = argparse.ArgumentParser(description="地图部署测试脚本")
    parser.add_argument("-f", "--file", default="data/sample_pollen_data.csv", help="数据文件路径")
    parser.add_argument("-o", "--output", default=".tempory/test_deploy", help="输出目录路径")
    parser.add_argument("--clean", action="store_true", help="测试前清理输出目录")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("地图部署测试脚本")
    print("=" * 60)
    print(f"数据文件: {args.file}")
    print(f"输出目录: {args.output}")
    print(f"清理输出: {'是' if args.clean else '否'}")
    print("=" * 60)
    
    # 清理输出目录
    if args.clean and os.path.exists(args.output):
        print(f"清理输出目录: {args.output}")
        shutil.rmtree(args.output)
    
    # 测试地图生成
    if not test_map_generation(args.file, args.output):
        print("地图生成测试失败")
        return 1
    
    # 测试部署结构
    if not test_deployment_structure(args.output):
        print("部署结构测试失败")
        return 1
    
    print("=" * 60)
    print("测试成功完成!")
    print("=" * 60)
    print(f"您可以打开以下文件检查生成的地图:")
    print(f"  {os.path.join(args.output, 'index.html')}")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 