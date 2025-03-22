# 花粉数据静态地图部署指南

本指南将帮助你使用`static_map_generator.py`工具生成静态地图网站，并将其部署到GitHub Pages上。

## 前提条件

- Python 3.6+
- 必要的Python库：
  - pandas
  - numpy
  - pyecharts
- 花粉数据CSV文件
- GitHub账户（用于部署GitHub Pages）

## 工具说明

`static_map_generator.py`是一个Python脚本，用于从花粉数据CSV文件生成一组静态HTML文件，这些文件可以直接部署到GitHub Pages或任何其他静态网站托管服务上。

不同于运行在服务器上的`map_server_example.py`，这个工具生成的是完全静态的网页，不需要后端服务器支持。

## 使用方法

### 生成静态地图文件

1. 打开终端或命令提示符，进入项目目录

2. 运行以下命令生成静态地图文件：

```bash
python static_map_generator.py -f 你的数据文件.csv -o 输出目录
```

例如：

```bash
python static_map_generator.py -f data/sample_pollen_data.csv -o docs
```

参数说明：
- `-f` 或 `--file`：花粉数据CSV文件路径（必需）
- `-o` 或 `--output-dir`：输出目录路径（默认为`docs`）

3. 脚本执行完毕后，将在指定的输出目录（默认为`docs`）中生成以下文件：
   - `index.html`：主页面
   - `maps/`目录：包含每个日期的地图HTML文件

### 本地预览

在部署到GitHub Pages之前，你可以在本地预览生成的网站：

1. 打开输出目录中的`index.html`文件，例如：

```
docs/index.html
```

2. 在浏览器中打开这个文件，你应该能看到地图界面，并可以通过下拉菜单选择不同日期的地图。

如果本地预览出现问题，可能是浏览器的安全策略限制了本地文件的JavaScript执行。你可以考虑使用简单的HTTP服务器来预览，例如：

```bash
# 如果你安装了Python 3
cd docs
python -m http.server 8000
```

然后在浏览器中访问 http://localhost:8000

## 部署到GitHub Pages

### 方法一：使用main分支下的docs目录

1. 在GitHub上创建一个新的仓库，或使用现有仓库

2. 将生成的静态文件添加到你的Git仓库：

```bash
# 如果是新仓库
git init
git add docs/
git commit -m "Add static maps for GitHub Pages"
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main

# 如果是现有仓库
git add docs/
git commit -m "Add static maps for GitHub Pages"
git push
```

3. 前往GitHub仓库设置页面（Settings）

4. 找到"Pages"部分

5. 在"Source"下，选择"Deploy from a branch"

6. 在分支选择下拉菜单中，选择"main"，在目录下拉菜单中选择"/docs"，然后点击"Save"

7. 稍等片刻，你的网站将被部署，GitHub会显示网站的URL（通常是 `https://你的用户名.github.io/你的仓库名/`）

### 方法二：使用gh-pages分支

1. 安装gh-pages工具（如果没有）：

```bash
npm install -g gh-pages
```

2. 使用gh-pages部署：

```bash
gh-pages -d docs
```

3. 前往GitHub仓库设置页面（Settings）

4. 找到"Pages"部分

5. 在"Source"下，选择"Deploy from a branch"

6. 在分支选择下拉菜单中，选择"gh-pages"，然后点击"Save"

## 定期更新

如果你需要定期更新花粉数据和地图，可以：

1. 获取最新的花粉数据文件

2. 重新运行静态地图生成器：

```bash
python static_map_generator.py -f 你的新数据文件.csv -o docs
```

3. 将更新后的文件提交到GitHub：

```bash
git add docs/
git commit -m "Update static maps with new data"
git push
```

GitHub Pages将自动更新你的网站。

## 自定义

如果你想自定义网站的外观，可以修改`static_map_generator.py`中的`create_index_html`函数，调整HTML和CSS代码。

## 故障排除

如果在GitHub Pages上访问地图时出现问题：

1. 确保GitHub Pages已正确配置并启用

2. 检查网站URL是否正确

3. 检查浏览器控制台是否有JavaScript错误

4. 确保所有资源（如地图HTML文件）都能正确加载

## 注意事项

- GitHub Pages有一定的网站大小限制，如果你的地图数据非常多或复杂，可能需要考虑分割数据或使用其他托管服务
- 默认情况下，GitHub Pages网站是公开的，如果你的数据敏感，应考虑使用私有仓库和付费GitHub计划 