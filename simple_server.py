#!/usr/bin/env python
# -*- coding: utf-8 -*-

import http.server
import socketserver
import os
import webbrowser

PORT = 8081
DIRECTORY = "docs"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"启动HTTP服务器在端口 {PORT}...")
    print(f"提供目录: {os.path.abspath(DIRECTORY)}")
    print(f"请访问: http://localhost:{PORT}")
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("服务器已启动，按Ctrl+C停止")
            webbrowser.open(f"http://localhost:{PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("服务器已停止")

if __name__ == "__main__":
    main() 