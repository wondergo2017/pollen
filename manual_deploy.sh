#!/bin/bash

# 手动部署脚本，强制更新GitHub Pages

echo "开始手动部署到GitHub Pages..."

# 确保目录存在
mkdir -p docs/maps

# 强制清理旧的地图文件和index.html
echo "清理旧的地图文件和index.html..."
rm -f docs/index.html
rm -rf docs/maps
mkdir -p docs/maps

# 生成2025年最新的地图文件
echo "生成新的地图文件..."
python static_map_generator.py -f data/pollen_data_latest.csv -o docs

# 检查生成的文件
echo "生成的文件列表:"
ls -la docs/
echo "地图文件夹内容:"
ls -la docs/maps/

# 提交更改
echo "提交更改..."
git add docs/
git commit -m "手动更新花粉地图 ($(date '+%Y-%m-%d'))"
git push origin main

# 部署到gh-pages分支
echo "部署到gh-pages分支..."
git checkout --orphan temp-gh-pages
git rm -rf --cached .
git add docs/
git commit -m "手动部署到GitHub Pages ($(date '+%Y-%m-%d'))"
git push --force origin temp-gh-pages:gh-pages

# 返回主分支
git checkout main
git branch -D temp-gh-pages

echo "手动部署完成!" 