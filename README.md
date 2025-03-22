# 花粉数据可视化系统

基于Python开发的花粉数据分析与可视化工具，可处理多城市花粉水平数据并生成直观的可视化图表和地图，帮助用户分析和理解花粉趋势数据。

## 功能特点

- **多样化可视化**：支持趋势图、分布图、地图等多种可视化类型
- **交互式地图**：基于PyEcharts的交互式花粉分布地图
- **静态地图生成**：支持生成静态花粉分布地图
- **多城市支持**：可同时分析和比较多个城市的花粉数据
- **灵活筛选**：按城市、日期范围等条件筛选数据
- **命令行工具**：提供便捷的命令行接口进行数据可视化
- **交互式选项**：支持交互式选择数据文件和可视化参数
- **中文支持**：完全支持中文显示和处理

## 系统要求

- Python 3.6+
- 主要依赖库：
  - pandas
  - matplotlib
  - numpy
  - seaborn (用于高级可视化)
  - requests (用于数据获取)
  - flask (用于地图服务器)
  - pyecharts (用于交互式地图)

## 项目结构

```
.
├── src/                    # 源代码目录
│   ├── visualization/      # 可视化相关代码
│   │   ├── __init__.py
│   │   ├── pollen_visualization.py  # 通用可视化逻辑
│   │   ├── trend_visualization.py   # 趋势图可视化
│   │   ├── distribution_visualization.py # 分布图可视化
│   │   ├── map_visualization.py     # 地图可视化
│   │   ├── static_map.py            # 静态地图生成
│   │   ├── data_loading.py          # 数据加载
│   │   ├── utils.py                 # 工具函数
│   │   └── main.py                  # 可视化主模块
│   ├── config/             # 配置相关代码
│   │   ├── __init__.py
│   │   └── visualization_config.py  # 可视化配置
│   ├── data/               # 数据处理代码
│   └── __init__.py
├── data/                   # 数据文件目录
│   ├── sample_pollen_data.csv       # 示例花粉数据
│   ├── sample_pollen_map_data.csv   # 示例地图数据
│   ├── sample_pollen_static_map_data.csv # 示例静态地图数据
│   ├── sample_map_server_data.csv   # 示例地图服务器数据
│   ├── sample_pyecharts_map_data.csv # 示例PyEcharts地图数据
│   └── pollen_data_*.csv            # 花粉数据文件
├── examples/               # 示例脚本
│   ├── visualize_example.py         # 可视化示例
│   ├── data_example.py              # 数据处理示例
│   └── run_visualization.py         # 交互式可视化脚本
├── scripts/                # 辅助脚本
│   └── install_fonts.py             # 字体安装脚本
├── output/                 # 输出文件目录
├── html/                   # HTML模板和静态文件目录
│   ├── templates/                   # Flask模板目录
│   └── static/                      # 静态资源目录
├── docs/                   # 文档目录
├── tests/                  # 测试目录
├── pollen_viz.py           # 命令行工具主入口
├── pollen_data_tool.py     # 数据处理工具入口
├── map_server_example.py   # 地图服务器示例
├── setup.py                # 安装配置
└── README.md               # 项目说明文档
```

## 安装说明

### 方法一：从源码安装

1. 克隆仓库：
```bash
git clone <repository-url>
cd <repository-directory>
```

2. 安装依赖（推荐使用虚拟环境）：
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者 venv\Scripts\activate  # Windows

# 安装包和依赖
pip install -e .
```

### 方法二：安装字体（可选但推荐）

如果在可视化时遇到中文字体问题，可以运行字体安装脚本：

```bash
python scripts/install_fonts.py
```

## 使用方法

### 命令行工具

项目提供了`pollen-viz`命令行工具，支持多种子命令：

```bash
# 列出可用数据文件
pollen-viz list-files

# 列出数据文件中的可用城市
pollen-viz list-cities -f data/pollen_data_2025-03-22.csv

# 生成花粉趋势图
pollen-viz trend -f data/pollen_data_2025-03-22.csv -c 北京,上海,广州 -s 2025-03-01 -e 2025-03-15

# 生成花粉分布图
pollen-viz distribution -f data/pollen_data_2025-03-22.csv -c 北京,上海

# 生成所有类型图表
pollen-viz all -f data/pollen_data_2025-03-22.csv
```

### 交互式界面

使用交互式脚本可以通过菜单选择进行可视化：

```bash
# 启动交互式界面
python examples/run_visualization.py

# 使用特定数据文件启动
python examples/run_visualization.py --file data/pollen_data_2025-03-22.csv
```

### 交互式地图服务器

启动基于PyEcharts和Flask的交互式地图服务器：

```bash
# 启动地图服务器
python map_server_example.py -f data/pollen_data_2025-03-22.csv

# 指定端口启动
python map_server_example.py -f data/pollen_data_2025-03-22.csv -p 8000

# 不自动打开浏览器
python map_server_example.py -f data/pollen_data_2025-03-22.csv --no-browser
```

启动后，可以通过浏览器访问 http://localhost:8088 (或指定端口) 查看交互式地图。

### 在Python代码中使用

```python
from src.visualization import trend_visualization as tv
from src.visualization import data_loading as dl

# 加载数据
df = dl.load_data('data/pollen_data_2025-03-22.csv')

# 过滤数据
filtered_df = dl.filter_data(df, cities=['北京', '上海'], 
                            start_date='2025-03-01', 
                            end_date='2025-03-15')

# 生成趋势图
output_file = tv.generate_trend_visualization(filtered_df, 
                                              output_dir='output')
print(f"趋势图已生成：{output_file}")
```

## 数据文件格式

项目支持处理的CSV数据格式包含以下字段：
- `日期`: 日期（格式：YYYY-MM-DD）
- `城市`: 城市名称
- `花粉等级`: 花粉等级（暂无、很低、较低、偏高、较高、很高等）
- `等级描述`: 花粉等级的文字描述
- `颜色代码`: 花粉等级对应的颜色代码
- `城市ID`: 城市ID编码
- `城市代码`: 城市代码（拼音）

## 示例

系统附带了几个示例脚本，可以快速体验功能：

```bash
# 生成示例数据并可视化
python examples/visualize_example.py

# 自定义城市数量和天数
python examples/visualize_example.py --cities 5 --days 30

# 数据处理示例
python examples/data_example.py
```

## 常见问题解决

### 字体问题

如果遇到以下字体相关警告：

```
findfont: Generic family 'sans-serif' not found because none of the following families were found: Microsoft YaHei, SimSun, Arial Unicode MS
```

请尝试以下解决方案：

1. 运行字体安装脚本：
```bash
python scripts/install_fonts.py
```

2. 手动安装中文字体并修改配置文件：
在`src/config/visualization_config.py`中修改字体设置：
```python
FONT_FAMILY = "你的系统中可用的中文字体名称"
```

### 地图服务器问题

如果启动地图服务器时遇到问题：

1. 确保已安装所需依赖：
```bash
pip install flask pyecharts
```

2. 检查端口是否被占用，尝试使用其他端口：
```bash
python map_server_example.py -p 8000
```

3. 如果自动打开浏览器失败，请手动访问：
```
http://localhost:8088  # 或指定的端口
```

### 其他问题

如果遇到其他问题或需要更多帮助，请：
1. 检查日志输出
2. 确保依赖库已正确安装
3. 联系项目维护团队获取支持

## 开发团队

SPI2 Team

## 许可证

MIT许可证

### 静态地图生成器（GitHub Pages支持）

项目提供了静态地图生成器，可以生成适合部署到GitHub Pages的静态HTML文件：

```bash
# 生成静态地图
python static_map_generator.py -f data/sample_pollen_data.csv -o docs

# 指定输出目录
python static_map_generator.py -f data/pollen_data_2025-03-22.csv -o output/static_maps
```

生成的静态网站可以直接部署到GitHub Pages或任何静态网站托管服务。详细说明请参考`README-github-pages.md`。

## 贡献

欢迎贡献代码、提交问题和建议！请参考贡献指南文档。

## 许可证

本项目采用MIT许可证，详见LICENSE文件。 