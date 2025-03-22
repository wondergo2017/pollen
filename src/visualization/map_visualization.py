def create_pollen_map(data, date_str=None):
    """创建花粉分布地图"""
    # 设置标题
    if date_str:
        title = f"{date_str} 全国花粉分布"
    else:
        title = "全国花粉分布地图"
    
    # 准备地图数据
    province_data = {}  # 按省份存储数据
    city_data = []      # 存储城市详细数据（用于弹窗显示）
    
    # 从数据中提取城市和对应的花粉等级
    for _, row in data.iterrows():
        city_name = row['城市']
        level = row['花粉等级']
        desc = row.get('等级描述', '')
        color_code = row.get('颜色代码', LEVEL_COLOR_MAP.get(level, '#999999'))
        
        # 获取城市坐标
        coordinates = get_city_coordinates(city_name)
        if coordinates is None:
            continue
            
        # 将花粉等级映射为数值，用于热力图显示
        level_value = list(LEVEL_SIZE_MAP.keys()).index(level) * 10 if level in LEVEL_SIZE_MAP else 0
        
        # 提取省份名称（简单处理：取城市名前两个字符，如"北京市"取"北京"）
        province_name = city_name[:2]
        if province_name.endswith(('市', '省', '区')):
            province_name = province_name[:-1]
        
        # 更新省份数据（取同一省份中的最高等级）
        if province_name in province_data:
            if level_value > province_data[province_name]:
                province_data[province_name] = level_value
        else:
            province_data[province_name] = level_value
        
        # 添加城市数据（用于弹窗显示）
        city_data.append({
            "name": city_name,
            "province": province_name,
            "value": level_value,
            "level": level,
            "desc": desc,
            "color": color_code,
            "coordinates": coordinates
        })
    
    # 转换为地图所需的数据格式
    map_data = [(province, value) for province, value in province_data.items()]
    
    # 创建地图实例
    map_chart = Map(init_opts=opts.InitOpts(
        width="100%", 
        height="600px", 
        theme=ThemeType.LIGHT,
        page_title=title
    ))
    
    # 添加地图数据
    map_chart.add(
        series_name="花粉等级",
        data_pair=map_data,
        maptype="china",
        is_roam=True,  # 允许缩放和平移
        label_opts=opts.LabelOpts(is_show=True),  # 显示省份名称
        symbol_size=20,  # 增加标记大小
        itemstyle_opts=opts.ItemStyleOpts(
            border_width=2,  # 增加边框宽度
            border_color="#FFFFFF",  # 白色边框
            opacity=0.9  # 略微提高透明度以保持颜色鲜明
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="item",
            formatter=lambda params: (
                f"{params.name}<br/>"
                f"花粉等级: {POLLEN_LEVELS[int(params.value/10)] if 0 <= int(params.value/10) < len(POLLEN_LEVELS) else '暂无'}"
            )
        )
    )
    
    # 设置全局选项
    map_chart.set_global_opts(
        title_opts=opts.TitleOpts(
            title=title,
            pos_left="center",
            pos_top="20px",
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=20,
                color="#333333"
            )
        ),
        visualmap_opts=opts.VisualMapOpts(
            is_show=True,
            type_="color",
            min_=0,
            max_=90,  # 对应最高等级"极高"的值
            range_text=["高", "低"],
            pos_right="10%",
            pos_bottom="10%",
            item_width=30,
            item_height=200,
            range_color=[
                "#81CB31", "#A1FF3D", "#F5EE32", 
                "#FFAF13", "#FF2319"
            ],
            textstyle_opts=opts.TextStyleOpts(
                color="#333333"
            ),
            dimension=0  # 确保视觉映射应用到值而不是索引
        ),
        legend_opts=opts.LegendOpts(
            is_show=True,
            pos_left="left",
            pos_top="bottom"
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="item"
        )
    )
    
    return map_chart 