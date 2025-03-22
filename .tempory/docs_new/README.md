# 花粉地图部署指南

这是一个完全静态的花粉分布地图网站，可以直接部署到GitHub Pages或任何静态网站托管服务上。

## 文件结构

- `index.html`: 主页面，包含日期选择器和地图显示框
- `maps/`: 包含各日期的地图HTML文件
  - `map_YYYY-MM-DD.html`: 每个日期对应的地图文件

## 如何部署到GitHub Pages

### 1. 创建GitHub仓库

如果你还没有GitHub仓库，请先创建一个。

### 2. 上传文件

将本目录下的所有文件上传到你的GitHub仓库。有两种方式：

- 通过Web界面上传
- 通过Git命令上传：
  ```bash
  cd docs_new
  git init
  git add .
  git commit -m "初始提交花粉地图网站"
  git remote add origin https://github.com/你的用户名/你的仓库名.git
  git push -u origin main
  ```

### 3. 配置GitHub Pages

1. 进入GitHub仓库页面
2. 点击"Settings"（设置）
3. 在左侧菜单中找到"Pages"（页面）
4. 在"Source"（源）部分，选择"Deploy from a branch"（从分支部署）
5. 在分支选择下拉菜单中选择"main"（或"master"）
6. 点击"Save"（保存）

### 4. 访问你的网站

几分钟后，你的网站将在以下地址可用：
```
https://你的用户名.github.io/你的仓库名/
```

## 更新地图数据

如需更新地图数据，请使用`static_map_generator.py`脚本重新生成地图文件：

```bash
python static_map_generator.py -f 新的数据文件.csv -o docs_new
```

然后将更新后的文件推送到GitHub仓库：

```bash
git add .
git commit -m "更新花粉数据"
git push
```

## 使用GitHub Actions自动部署

本项目已配置GitHub Actions工作流，可以在以下情况下自动部署花粉地图网站：

1. 当推送到main分支时
2. 当data目录中的数据文件更新时
3. 当static_map_generator.py脚本更新时
4. 手动触发工作流时

### 自动部署工作流程

1. GitHub Actions会自动检出代码
2. 设置Python环境
3. 安装必要的依赖
4. 运行static_map_generator.py生成最新的地图文件
5. 将生成的文件部署到gh-pages分支
6. GitHub Pages从gh-pages分支提供网站服务

### 手动触发部署

如果需要手动触发部署，可以：

1. 在GitHub仓库页面点击"Actions"标签
2. 在左侧选择"部署花粉地图到GitHub Pages"工作流
3. 点击"Run workflow"按钮
4. 选择分支并点击"Run workflow"确认

### 自定义自动部署

如果需要自定义部署流程，可以编辑`.github/workflows/deploy-pollen-map.yml`文件：

- 更改触发条件
- 添加更多依赖
- 使用不同的数据文件
- 调整部署参数

### 查看部署状态

可以在GitHub仓库的"Actions"标签页查看部署历史和状态。如果部署失败，可以查看详细日志了解原因。

## 注意事项

- 本网站完全静态，不需要后端服务器
- 使用CDN加载ECharts库，确保地图可以在大多数环境下正常显示
- 如有地图加载问题，请检查网络是否可以访问CDN资源 