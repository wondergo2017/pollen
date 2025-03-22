#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉分布静态地图服务器
提供docs目录的本地HTTP服务
"""

import os
import sys
import http.server
import socketserver
import webbrowser
from urllib.parse import urlparse
import argparse

def serve_docs(port=8000, open_browser=True):
    """
    启动一个本地HTTP服务器，提供docs目录的服务
    
    参数:
    port: 端口号，默认为8000
    open_browser: 是否自动打开浏览器，默认为True
    """
    # 确认docs目录存在
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs')
    if not os.path.exists(docs_dir):
        print(f"错误: 找不到docs目录: {docs_dir}")
        return 1
    
    # 确认index.html文件存在
    index_path = os.path.join(docs_dir, 'index.html')
    if not os.path.exists(index_path):
        print(f"错误: 找不到首页文件: {index_path}")
        return 1
    
    # 切换到docs目录
    os.chdir(docs_dir)
    
    handler = http.server.SimpleHTTPRequestHandler
    
    # 尝试绑定端口，如果失败则尝试下一个端口
    while True:
        try:
            httpd = socketserver.TCPServer(("", port), handler)
            break
        except OSError:
            print(f"端口 {port} 已被占用，尝试下一个端口...")
            port += 1
    
    print("=" * 60)
    print(f"花粉分布静态地图服务器 运行在 http://localhost:{port}/")
    print(f"目录: {docs_dir}")
    print("=" * 60)
    print("按 Ctrl+C 停止服务器")
    
    # 自动打开浏览器
    if open_browser:
        webbrowser.open(f'http://localhost:{port}/')
    
    # 启动服务器
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
    finally:
        httpd.server_close()
    
    return 0

def main():
    parser = argparse.ArgumentParser(description='花粉分布静态地图服务器')
    parser.add_argument('-p', '--port', type=int, default=8000, help='服务器端口号 (默认: 8000)')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    
    args = parser.parse_args()
    
    return serve_docs(port=args.port, open_browser=not args.no_browser)

if __name__ == "__main__":
    sys.exit(main()) 