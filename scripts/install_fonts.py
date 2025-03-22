#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中文字体安装脚本
此脚本用于下载和安装中文字体，解决可视化模块中文显示问题
"""

import os
import sys
import platform
import subprocess
import shutil
import tempfile
import matplotlib
import matplotlib.font_manager as fm
from urllib.request import urlretrieve
import zipfile
import tarfile

# 字体下载链接
FONT_SOURCES = {
    "wqy-microhei": {
        "url": "https://sourceforge.net/projects/wqy/files/wqy-microhei/0.2.0-beta/wqy-microhei-0.2.0-beta.tar.gz/download",
        "filename": "wqy-microhei-0.2.0-beta.tar.gz",
        "extract_dir": "wqy-microhei",
        "font_files": ["wqy-microhei.ttc"]
    },
    "noto-sans-cjk": {
        "url": "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf",
        "filename": "NotoSansCJKsc-Regular.otf",
        "font_files": ["NotoSansCJKsc-Regular.otf"]
    },
    "source-han-sans": {
        "url": "https://github.com/adobe-fonts/source-han-sans/releases/download/2.004R/SourceHanSansSC.zip",
        "filename": "SourceHanSansSC.zip",
        "extract_dir": "SourceHanSansSC",
        "font_files": ["OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf"]
    }
}

def get_font_dir():
    """获取字体安装目录"""
    system = platform.system()
    if system == "Windows":
        # Windows字体目录
        return os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    elif system == "Darwin":  # macOS
        # macOS字体目录
        return os.path.expanduser("~/Library/Fonts")
    else:
        # Linux字体目录
        home = os.path.expanduser("~")
        font_dir = os.path.join(home, ".fonts")
        if not os.path.exists(font_dir):
            os.makedirs(font_dir, exist_ok=True)
        return font_dir

def get_matplotlib_font_dir():
    """获取matplotlib字体目录"""
    matplotlib_data_dir = matplotlib.get_data_path()
    font_dir = os.path.join(matplotlib_data_dir, "fonts", "ttf")
    return font_dir

def download_and_install_font(font_key):
    """下载并安装指定的字体"""
    if font_key not in FONT_SOURCES:
        print(f"错误: 未知字体 '{font_key}'")
        return False

    font_info = FONT_SOURCES[font_key]
    url = font_info["url"]
    filename = font_info["filename"]
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"正在下载字体 {font_key}...")
        download_path = os.path.join(temp_dir, filename)
        urlretrieve(url, download_path)
        
        # 解压缩字体文件（如果需要）
        extract_path = temp_dir
        if filename.endswith(".zip"):
            print("正在解压ZIP文件...")
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            if "extract_dir" in font_info:
                extract_path = os.path.join(temp_dir, font_info["extract_dir"])
        elif filename.endswith(".tar.gz") or filename.endswith(".tgz"):
            print("正在解压TAR.GZ文件...")
            with tarfile.open(download_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_path)
            if "extract_dir" in font_info:
                extract_path = os.path.join(temp_dir, font_info["extract_dir"])
        
        # 安装字体
        font_dir = get_font_dir()
        matplotlib_font_dir = get_matplotlib_font_dir()
        
        for font_file in font_info["font_files"]:
            if "extract_dir" in font_info and not os.path.exists(os.path.join(extract_path, font_file)):
                font_path = font_file  # 可能是相对于extract_path的路径
            else:
                font_path = os.path.join(extract_path, font_file)
            
            if not os.path.exists(font_path):
                # 如果指定路径不存在，尝试直接使用下载的文件
                if os.path.exists(download_path) and not "extract_dir" in font_info:
                    font_path = download_path
                else:
                    print(f"错误: 无法找到字体文件 {font_file}")
                    continue
            
            # 复制到系统字体目录
            font_file_name = os.path.basename(font_path)
            dest_path = os.path.join(font_dir, font_file_name)
            print(f"正在安装字体到 {dest_path}...")
            shutil.copy2(font_path, dest_path)
            
            # 复制到matplotlib字体目录
            matplotlib_dest_path = os.path.join(matplotlib_font_dir, font_file_name)
            print(f"正在安装字体到matplotlib: {matplotlib_dest_path}...")
            shutil.copy2(font_path, matplotlib_dest_path)
        
        print(f"字体 {font_key} 安装成功!")
        return True
    
    except Exception as e:
        print(f"安装字体 {font_key} 时出错: {str(e)}")
        return False
    
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

def update_font_cache():
    """更新字体缓存"""
    system = platform.system()
    try:
        if system == "Linux":
            # Linux字体缓存更新命令
            subprocess.run(["fc-cache", "-fv"], check=True)
        elif system == "Darwin":  # macOS
            # macOS字体缓存更新命令
            subprocess.run(["atsutil", "databases", "-remove"], check=True)
            
        # 更新matplotlib字体缓存
        print("正在刷新matplotlib字体缓存...")
        fm._get_fontconfig_fonts.cache_clear()
        fm.fontManager._load_fontmanager(try_read_cache=False)
        
        print("字体缓存更新成功!")
        return True
    except Exception as e:
        print(f"更新字体缓存时出错: {str(e)}")
        return False

def check_installed_fonts():
    """检查已安装的中文字体"""
    print("\n已安装的中文字体:")
    found = False
    
    # 检查系统字体
    try:
        import subprocess
        result = subprocess.run(['fc-list', ':lang=zh'], capture_output=True, text=True)
        if result.returncode == 0:
            fonts = []
            for line in result.stdout.splitlines():
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        font_path = parts[0].strip()
                        font_name = parts[1].split('=')[0].strip() if '=' in parts[1] else parts[1].strip()
                        fonts.append((font_name, font_path))
            
            if fonts:
                found = True
                for i, (name, path) in enumerate(fonts, 1):
                    print(f"{i}. {name} - {path}")
    except Exception:
        pass
    
    # 检查matplotlib字体
    print("\nMatplotlib可用的中文字体:")
    chinese_fonts = [f.name for f in fm.fontManager.ttflist if any(
        chinese_text in f.name for chinese_text in 
        ['Hei', 'Ming', 'Song', 'Yuan', 'Kai', 'Fang', 'Zhong', 'CN', 'GB', 'SC', 'TC', 'CJK', '黑', '宋', '圆', '楷', '仿', '中']
    )]
    
    if chinese_fonts:
        found = True
        for i, font in enumerate(sorted(set(chinese_fonts)), 1):
            print(f"{i}. {font}")
    
    if not found:
        print("未找到任何中文字体，请运行安装命令")
    
    return found

def main():
    """主函数"""
    print("中文字体安装工具\n")
    
    # 检查参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "install":
            # 安装指定字体
            font_key = sys.argv[2] if len(sys.argv) > 2 else "wqy-microhei"
            if font_key == "all":
                for key in FONT_SOURCES.keys():
                    download_and_install_font(key)
            else:
                download_and_install_font(font_key)
            update_font_cache()
        elif command == "check":
            # 检查已安装字体
            check_installed_fonts()
        elif command == "update-cache":
            # 仅更新字体缓存
            update_font_cache()
        else:
            print("未知命令:", command)
            print("可用命令: install, check, update-cache")
    else:
        # 交互式界面
        print("可用命令:")
        print("1. 检查已安装的中文字体")
        print("2. 安装文泉驿微米黑字体 (推荐)")
        print("3. 安装思源黑体")
        print("4. 安装Noto Sans CJK SC字体")
        print("5. 安装所有字体")
        print("6. 更新字体缓存")
        print("0. 退出")
        
        try:
            choice = input("\n请输入命令编号: ")
            if choice == "1":
                check_installed_fonts()
            elif choice == "2":
                download_and_install_font("wqy-microhei")
                update_font_cache()
            elif choice == "3":
                download_and_install_font("source-han-sans")
                update_font_cache()
            elif choice == "4":
                download_and_install_font("noto-sans-cjk")
                update_font_cache()
            elif choice == "5":
                for key in FONT_SOURCES.keys():
                    download_and_install_font(key)
                update_font_cache()
            elif choice == "6":
                update_font_cache()
            elif choice == "0":
                print("退出")
                return
            else:
                print("无效的选择")
        except KeyboardInterrupt:
            print("\n操作已取消")
        except Exception as e:
            print(f"出错: {str(e)}")

if __name__ == "__main__":
    main() 