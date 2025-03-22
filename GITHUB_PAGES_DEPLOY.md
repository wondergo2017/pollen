# 花粉地图GitHub Pages部署指南

本文档详细介绍如何将花粉地图部署到GitHub Pages，包括手动部署和自动部署两种方式。

## 自动部署（推荐）

使用GitHub Actions可以自动完成地图生成和部署过程。每当代码或数据更新时，网站会自动重新部署。

### 1. 设置仓库

1. 将项目代码推送到GitHub仓库
2. 确保以下文件存在于仓库中：
   - `.github/workflows/deploy-pollen-map.yml`：部署工作流配置
   - `.github/workflows/update-pollen-data.yml`：数据更新工作流配置（可选）
   - `static_map_generator.py`：地图生成脚本
   - `data/`目录：包含花粉数据文件

### 2. 启用GitHub Pages

1. 进入GitHub仓库页面
2. 点击"Settings"（设置）
3. 在左侧菜单中找到"Pages"（页面）
4. 在"Source"（源）部分，选择"Deploy from a branch"（从分支部署）
5. 在分支选择下拉菜单中选择"gh-pages"
6. 点击"Save"（保存）

### 3. 触发部署

初始部署可以通过以下方式触发：

1. 手动触发部署工作流：
   - 进入GitHub仓库页面
   - 点击"Actions"标签
   - 从左侧选择"部署花粉地图到GitHub Pages"工作流
   - 点击"Run workflow"按钮
   - 选择分支，然后点击"Run workflow"确认

2. 自动触发条件：
   - 当推送到main分支时
   - 当`data`目录中的数据文件更新时
   - 当`static_map_generator.py`脚本更新时

### 4. 监控部署状态

部署过程可在GitHub Actions页面监控：

1. 进入GitHub仓库页面
2. 点击"Actions"标签
3. 找到正在运行的工作流程并点击查看详情
4. 等待工作流程完成（绿色勾表示成功，红色叉表示失败）

### 5. 访问部署的网站

部署成功后，您的网站将在以下地址可用：
```
https://[用户名].github.io/[仓库名]/
```

例如，如果您的GitHub用户名是"example"，仓库名是"pollen-map"，则网站地址为：
```
https://example.github.io/pollen-map/
```

## 手动部署

如果您不想使用GitHub Actions，也可以手动部署花粉地图。

### 1. 生成静态网站文件

```bash
# 生成静态网站文件
python static_map_generator.py -f data/sample_pollen_data.csv -o docs
```

### 2. 查看生成的文件

确保`docs`目录中含有以下文件：
- `index.html`：主页文件
- `maps/`目录：包含地图HTML文件

### 3. 推送到GitHub仓库

```bash
# 添加文件到Git
git add docs/

# 提交更改
git commit -m "添加静态地图网站"

# 推送到GitHub
git push origin main
```

### 4. 启用GitHub Pages

1. 进入GitHub仓库页面
2. 点击"Settings"（设置）
3. 在左侧菜单中找到"Pages"（页面）
4. 在"Source"（源）部分，选择"Deploy from a branch"（从分支部署）
5. 在分支选择下拉菜单中选择"main"，在目录下拉菜单中选择"/docs"
6. 点击"Save"（保存）

## 注意事项

### 部署故障排除

如果部署失败或网站无法正常显示，请检查：

1. **文件结构**：确保`index.html`和`maps/`目录位于正确的位置
2. **文件引用**：确保`index.html`中正确引用了地图文件
3. **CDN访问**：确保地图文件中使用的CDN资源可以访问
4. **GitHub Actions日志**：检查工作流日志中的错误信息

### 常见问题

1. **只有README但没有地图**：
   - 检查地图生成步骤是否成功
   - 检查`docs`目录是否包含所有必要文件
   - 尝试使用`.github/workflows/test-map-deploy.yml`工作流进行测试

2. **地图加载错误**：
   - 检查浏览器控制台是否有JavaScript错误
   - 确保CDN资源可以访问
   - 尝试修改`static_map_generator.py`使用不同的CDN

3. **权限错误**：
   - 确保工作流中添加了适当的权限：`permissions: contents: write`

### 自定义部署过程

如需自定义部署过程，可以编辑以下文件：

1. `.github/workflows/deploy-pollen-map.yml`：修改部署触发条件和步骤
2. `.github/workflows/update-pollen-data.yml`：修改数据更新流程
3. `static_map_generator.py`：修改地图生成逻辑和样式 