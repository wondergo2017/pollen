# 中国天气网花粉等级数据爬虫与可视化工具

这个Python项目用于爬取[中国天气网](https://www.weather.com.cn/forecast/hf_index.shtml)上各城市的花粉等级数据，并提供强大的数据可视化功能。

## 功能

- 爬取中国天气网支持的50个城市的花粉等级数据
- 获取近30天的历史花粉等级数据或指定日期范围的数据
- 将数据保存为CSV或Excel格式
- 自定义配置参数，包括日期范围、爬取间隔、输出格式等
- 支持选择性爬取特定城市的数据
- 自动重试机制，提高数据获取成功率
- **高级数据可视化功能**：
  - 多城市花粉等级趋势对比图
  - 城市花粉等级分布统计图
  - 热力图分析
  - 自定义图表样式和配置

## 项目结构

- `pollen_scraper.py` - 主爬虫脚本
- `config.py` - 爬虫配置文件
- `test_single_city.py` - 单城市测试脚本
- `pollen_visualization.py` - 可视化核心模块
- `visualization_config.py` - 可视化配置文件
- `visualize_example.py` - 示例数据生成与可视化脚本
- `run_visualization.py` - 交互式可视化工具
- `README.md` - 项目说明文档

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

这是因为系统中缺少中文字体（如SimHei, Microsoft YaHei等）。脚本已添加自动字体检测功能，会自动选择系统中可用的字体。

### 解决方法

1. **自动检测**：
   - 最新版本的脚本会自动检测系统中可用的字体，优先选择中文字体
   - 如果没有找到中文字体，会自动使用系统默认字体

2. **手动安装中文字体**：
   - Linux系统：
     ```bash
     sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei
     ```
   - Windows系统：
     默认已安装中文字体，如宋体(SimSun)、黑体(SimHei)等

3. **自定义字体**：
   - 修改 `visualization_config.py` 文件中的 `FONT_FAMILY` 变量，设置为系统中可用的字体

### 字体问题注意事项

- 即使没有合适的中文字体，脚本仍然可以正常运行并生成图表
- 可能会看到一些关于缺失字形的警告，但不会影响图表的整体生成
- 如果中文显示为方块或乱码，说明当前系统缺少中文字体支持
- 图表中的中文标签可能无法正确显示，但数据点和图表结构不受影响

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