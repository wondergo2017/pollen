# 花粉数据可视化系统

这是一个用于花粉数据分析和可视化的Python工具，可以处理不同城市的花粉水平数据并生成直观的可视化图表。

## 项目结构

```
.
├── src/                    # 源代码目录
│   ├── visualization/      # 可视化相关代码
│   │   ├── __init__.py
│   │   └── pollen_visualization.py  # 核心可视化逻辑
│   ├── config/             # 配置相关代码
│   │   ├── __init__.py
│   │   └── visualization_config.py  # 可视化配置
│   └── __init__.py
├── data/                   # 数据文件目录
│   ├── sample_pollen_data.csv       # 示例数据
│   └── pollen_data_*.csv            # 各种花粉数据文件
├── examples/               # 示例脚本
│   ├── visualize_example.py         # 可视化示例
│   └── run_visualization.py         # 运行可视化的脚本
├── tests/                  # 测试文件目录
│   ├── test_visualization.py        # 可视化测试
│   ├── test_single_city.py          # 单城市数据测试
│   └── test_output/                 # 测试输出目录
├── output/                 # 输出文件目录
│   └── visualization_output/        # 可视化输出
├── setup.py                # 安装配置
└── README.md               # 项目说明文档
```

## 安装

1. 克隆仓库：
```bash
git clone <repository-url>
cd <repository-directory>
```

2. 安装依赖（推荐使用虚拟环境）：
```bash
pip install -e .
```

## 使用方法

### 使用示例脚本

直接运行示例脚本可以快速生成可视化效果：

```bash
python examples/run_visualization.py
```

该脚本会引导你选择数据文件、设置参数并生成花粉数据可视化图表。

### 使用可视化模块

也可以在自己的Python脚本中导入并使用可视化模块：

```python
from src.visualization import pollen_visualization as pv

# 加载数据
df = pv.load_data('data/sample_pollen_data.csv')

# 过滤数据
df = pv.filter_data(df, cities=['北京', '上海'], start_date='2025-03-01', end_date='2025-03-31')

# 准备数据
prepared_df = pv.prepare_data_for_visualization(df)

# 生成可视化
output_path = pv.visualize_pollen_trends(prepared_df, output_dir='output/visualization_output')
print(f"已生成可视化：{output_path}")
```

## 测试

运行测试来验证系统功能：

```bash
python tests/test_visualization.py
python tests/test_single_city.py
```

## 要求

- Python 3.6+
- pandas
- matplotlib
- numpy
- seaborn (可选，用于高级可视化)
- requests (可选，用于数据获取)

## 功能

- 支持多城市花粉数据的加载和处理
- 生成花粉水平趋势图和分布图
- 支持数据过滤（按城市、日期范围）
- 支持中文显示和多种输出格式
- 可定制的可视化配置

## 数据内容

脚本爬取的数据包括：

- 城市名称和代码
- 日期和星期
- 花粉等级（很低、较低、偏高、较高、很高等）
- 花粉颜色代码
- 花粉数量
- 过敏反应提示信息

## 使用方法

### 依赖安装

脚本依赖以下Python库：
```
pip install requests pandas openpyxl matplotlib numpy
pip install seaborn  # 可选，用于高级可视化
```

### 爬虫配置参数

可以通过修改 `config.py` 文件来自定义爬虫的行为：

```python
# 爬取数据的日期范围
USE_RELATIVE_DATES = True  # 是否使用相对时间范围
DAYS_TO_FETCH = 30  # 爬取过去多少天的数据

# 固定日期范围（如果USE_RELATIVE_DATES=False）
START_DATE = "2023-03-01"  # 开始日期
END_DATE = "2023-05-31"  # 结束日期

# 爬虫行为设置
REQUEST_DELAY = 2  # 请求间隔时间（秒）
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）
MAX_RETRIES = 3  # 最大重试次数

# 输出设置
OUTPUT_FORMAT = "csv"  # 数据保存格式，支持"csv"和"excel"
ADD_DATE_TO_FILENAME = True  # 是否自动在文件名中添加日期
FILENAME_PREFIX = "pollen_data"  # 自定义文件名前缀

# 仅爬取特定城市（留空表示爬取所有城市）
SELECTED_CITIES = []  # 例如: ["beijing", "shanghai"]
```

### 可视化配置参数

可以通过修改 `visualization_config.py` 文件自定义可视化的样式和行为：

```python
# 花粉等级对应的颜色映射
LEVEL_COLORS = {
    "未检测": "#999999",
    "很低": "#81CB31",
    "较低": "#A1FF3D",
    # ... 其他等级颜色 ...
}

# 图表默认设置
CHART_CONFIG = {
    "figsize": (12, 8),
    "title_fontsize": 16,
    "line_width": 2.5,
    "marker_size": 8,
    # ... 其他图表配置 ...
}

# 中文字体设置
FONT_FAMILY = "SimHei"  # 可根据系统修改为可用的中文字体
```

### 数据爬取

直接运行爬虫脚本即可：
```
python pollen_scraper.py
```

脚本会根据配置文件下载城市的花粉等级数据，并保存为指定格式的文件。

### 数据可视化

#### 命令行方式

使用可视化脚本生成花粉等级趋势图：

```bash
# 使用已有CSV数据文件生成可视化
python pollen_visualization.py pollen_data_2023-04-15.csv

# 指定特定城市生成可视化
python pollen_visualization.py pollen_data_2023-04-15.csv --cities 北京 上海 广州

# 指定输出文件路径
python pollen_visualization.py pollen_data_2023-04-15.csv --output pollen_trend.png

# 指定日期范围
python pollen_visualization.py pollen_data_2023-04-15.csv --start_date 2023-03-01 --end_date 2023-04-01

# 生成高级图表和分布统计图
python pollen_visualization.py pollen_data_2023-04-15.csv --advanced --distribution
```

#### 交互式方式

使用交互式运行脚本，通过菜单选择进行可视化：

```bash
# 交互式选择数据文件和可视化参数
python run_visualization.py

# 使用命令行参数指定数据文件，其他通过交互方式选择
python run_visualization.py --data_file pollen_data_2023-04-15.csv

# 使用示例数据进行可视化
python run_visualization.py --sample
```

#### 示例脚本

使用示例脚本快速体验可视化功能：

```bash
# 生成示例数据并可视化
python visualize_example.py

# 自定义城市数量和天数
python visualize_example.py --cities 8 --days 60

# 使用已有数据文件并启用高级图表
python visualize_example.py --data_file pollen_data_2023-04-15.csv --advanced
```

所有生成的可视化图表将默认保存在 `visualization_output` 目录中。

## 字体配置与问题解决

在运行可视化脚本时，可能会遇到以下字体相关警告：

```
findfont: Generic family 'sans-serif' not found because none of the following families were found: Microsoft YaHei, SimSun, Arial Unicode MS
```

这是因为系统中缺少中文字体（如SimHei, Microsoft YaHei等）。脚本已添加自动字体检测功能，会尝试自动选择系统中可用的字体。

### 解决方法

我们提供了一个字体安装脚本，可以帮助您安装中文字体：

```bash
# 检查已安装的中文字体
python scripts/install_fonts.py check

# 安装文泉驿微米黑字体（Linux和macOS推荐）
python scripts/install_fonts.py install wqy-microhei

# 安装所有支持的中文字体
python scripts/install_fonts.py install all

# 或者使用交互式界面
python scripts/install_fonts.py
```

如果您已经安装了中文字体，但仍然出现警告，可以尝试刷新字体缓存：

```bash
python scripts/install_fonts.py update-cache
```

对于不同操作系统的用户，推荐安装以下字体：

- **Windows**: 默认已安装宋体(SimSun)和微软雅黑(Microsoft YaHei)
- **macOS**: 安装 WenQuanYi Micro Hei 或 Noto Sans CJK SC
- **Linux**: 安装 WenQuanYi Micro Hei 或 Noto Sans CJK SC

### 手动安装字体

如果自动安装失败，可以手动下载并安装以下任一字体：

1. [文泉驿微米黑 (WenQuanYi Micro Hei)](http://wenq.org/wqy2/index.cgi?MicroHei)
2. [思源黑体 (Source Han Sans)](https://github.com/adobe-fonts/source-han-sans/releases)
3. [Noto Sans CJK SC](https://github.com/googlefonts/noto-cjk)

安装完成后，重新运行程序，字体警告应该会消失。

## 可视化功能详解

### 多城市趋势对比图

- 将多个城市的花粉等级趋势绘制在同一图表上
- 根据花粉等级使用不同颜色标记数据点
- 支持自定义日期范围和城市列表
- 显示清晰的日期标签和花粉等级说明

### 花粉等级分布统计图

- 通过堆叠柱状图展示各城市不同花粉等级的分布情况
- 直观比较不同城市的花粉等级分布差异
- 易于分析特定城市的花粉等级主要集中在哪个水平

### 城市对比热力图

- 通过热力图直观展示多个城市在不同日期的花粉等级
- 使用颜色深浅表示花粉等级高低
- 方便一次性查看大量城市数据
- 需要安装seaborn库支持

### 月度趋势分析

- 对长时间范围的数据进行月度分析
- 自动生成每月的花粉趋势图
- 便于观察花粉季节性变化

### 自定义图表样式

- 支持自定义图表大小、标题字体、线条粗细等
- 可调整标记点大小、网格样式和透明度
- 可设置中文字体，确保中文正确显示

## 数据示例

| city | city_id | cityCode | addTime | week | level | levelCode | color | elenum | levelMsg |
|------|---------|----------|---------|------|-------|-----------|-------|--------|----------|
| 北京 | 101010100 | beijing | 2023-04-05 | 星期三 | 很高 | 5 | #FF2319 | 1 | 极易引发过敏，减少外出，持续规范用药。 |
| 上海 | 101020100 | shanghai | 2023-04-05 | 星期三 | 较低 | 2 | #A1FF3D | 23 | 对极敏感人群可能引发过敏反应。 |

## 可视化示例效果

可视化图表将展示以下特点：

- 使用鲜明的颜色区分不同的花粉等级
- 线条平滑连接各个日期的数据点
- 清晰的图例说明城市和花粉等级含义
- 坐标轴标签和刻度清晰可读
- 网格线辅助查看准确值
- 自适应日期标签，避免重叠

## 使用场景与建议

- **城市选择**：建议每次可视化时选择3-5个城市，避免图表过于拥挤
- **时间范围**：通常1-2个月的数据最适合趋势分析
- **图表选择**：
  - 分析少量城市的详细趋势：使用趋势对比图
  - 分析多城市的整体分布：使用分布统计图
  - 观察大量城市数据的概览：使用热力图

## 注意事项

- 默认爬取频率为每个城市间隔2秒，以避免对服务器造成过大压力
- 如果请求失败，脚本会自动重试最多3次
- 可以选择性爬取特定城市的数据，减少爬取时间
- 数据仅用于个人研究和学习，请勿用于商业目的
- 花粉等级数据通常在春季（3-5月）最为活跃
- 可视化功能需要 matplotlib 库支持中文字体，默认使用 SimHei，可能需要额外配置
- 对于高级图表（如热力图），需要安装 seaborn 库

## 支持的城市

脚本支持爬取的城市包括：北京、上海、广州、深圳、天津、重庆、成都、杭州、南京、西安、武汉、长沙等50个主要城市。 