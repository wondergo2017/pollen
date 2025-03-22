#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据命令行工具
提供简单的命令行接口，用于获取和处理花粉数据
"""

import os
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入数据模块
from src.data.cli import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断，程序退出")
    except Exception as e:
        print(f"\n程序执行出错: {str(e)}")
        import traceback
        traceback.print_exc() 