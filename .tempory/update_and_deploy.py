#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据自动更新脚本
用于自动获取最新花粉数据、更新数据文件并推送到GitHub，触发自动部署
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime
import pandas as pd

def run_command(command):
    """运行Shell命令并打印输出"""
    print(f"执行命令: {command}")
    process = subprocess.Popen(
        command, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()
    
    if stdout:
        print(f"标准输出:\n{stdout}")
    if stderr:
        print(f"错误输出:\n{stderr}")
    
    return process.returncode, stdout, stderr

def update_data(data_dir="data", output_file=None, github_push=False):
    """
    更新花粉数据并推送到GitHub
    
    参数:
        data_dir: 数据目录
        output_file: 输出文件名，如果为None则自动生成
        github_push: 是否推送到GitHub仓库
    """
    # 确保数据目录存在
    os.makedirs(data_dir, exist_ok=True)
    
    # 生成当前日期字符串
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 如果没有指定输出文件，则使用当前日期生成文件名
    if output_file is None:
        output_file = os.path.join(data_dir, f"pollen_data_{today}.csv")
    
    print(f"准备更新花粉数据到文件: {output_file}")
    
    # TODO: 在这里添加获取最新花粉数据的代码
    # 这里只是一个示例，实际实现中应该调用API或爬取网站数据
    
    # 示例: 创建一个简单的测试数据集
    data = {
        "日期": [today] * 10,
        "城市": ["北京", "上海", "广州", "深圳", "成都", "西安", "南京", "武汉", "杭州", "长沙"],
        "花粉等级": ["较高", "中", "低", "较低", "高", "偏高", "中", "低", "较低", "高"]
    }
    
    df = pd.DataFrame(data)
    
    # 保存数据到文件
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"花粉数据已更新到: {output_file}")
    
    # 如果需要推送到GitHub
    if github_push:
        print("准备推送更新到GitHub...")
        
        # Git添加文件
        run_command(f"git add {output_file}")
        
        # Git提交
        commit_message = f"自动更新花粉数据 {today}"
        run_command(f'git commit -m "{commit_message}"')
        
        # Git推送
        run_command("git push")
        
        print("数据已推送到GitHub，将触发自动部署流程")
    
    return output_file

def main():
    parser = argparse.ArgumentParser(description="花粉数据自动更新脚本")
    parser.add_argument("-d", "--data-dir", default="data", help="数据目录 (默认: data)")
    parser.add_argument("-o", "--output", help="输出文件名 (默认使用当前日期生成)")
    parser.add_argument("-p", "--push", action="store_true", help="推送到GitHub仓库")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("花粉数据自动更新脚本")
    print("=" * 60)
    print(f"数据目录: {args.data_dir}")
    print(f"推送到GitHub: {'是' if args.push else '否'}")
    print("=" * 60)
    
    try:
        output_file = update_data(
            data_dir=args.data_dir,
            output_file=args.output,
            github_push=args.push
        )
        
        print(f"数据更新成功: {output_file}")
        return 0
    except Exception as e:
        print(f"数据更新失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 