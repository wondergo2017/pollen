#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
花粉数据常量模块
此模块包含花粉数据处理所需的常量定义
"""

# 城市列表
CITIES = [
    {"en": "beijing", "cn": "北京", "id": 101010100},
    {"en": "yinchuan", "cn": "银川", "id": 101170101},
    {"en": "lanzhou", "cn": "兰州", "id": 101160101},
    {"en": "changchun", "cn": "长春", "id": 101060101},
    {"en": "xian", "cn": "西安", "id": 101110101},
    {"en": "taiyuan", "cn": "太原", "id": 101100101},
    {"en": "shenyang", "cn": "沈阳", "id": 101070101},
    {"en": "wulumuqi", "cn": "乌鲁木齐", "id": 101130101},
    {"en": "huhehaote", "cn": "呼和浩特", "id": 101080101},
    {"en": "liaocheng", "cn": "聊城", "id": 101121701},
    {"en": "zibo", "cn": "淄博", "id": 101120301},
    {"en": "chengde", "cn": "承德", "id": 101090402},
    {"en": "baotou", "cn": "包头", "id": 101080201},
    {"en": "eerduosi", "cn": "鄂尔多斯", "id": 101080701},
    {"en": "haerbin", "cn": "哈尔滨", "id": 101050101},
    {"en": "wulanhaote", "cn": "乌兰浩特", "id": 101081101},
    {"en": "haikou", "cn": "海口", "id": 101310101},
    {"en": "tianjin", "cn": "天津", "id": 101030100},
    {"en": "xining", "cn": "西宁", "id": 101150101},
    {"en": "cangzhou", "cn": "沧州", "id": 101090701},
    {"en": "chongqing", "cn": "重庆", "id": 101040100},
    {"en": "wuhan", "cn": "武汉", "id": 101200101},
    {"en": "shijiazhuang", "cn": "石家庄", "id": 101090101},
    {"en": "kunming", "cn": "昆明市", "id": 101290101},
    {"en": "botou", "cn": "泊头", "id": 101090711},
    {"en": "dalian", "cn": "大连", "id": 101070201},
    {"en": "jinan", "cn": "济南", "id": 101120101},
    {"en": "hangzhou", "cn": "杭州", "id": 101210101},
    {"en": "wuhai", "cn": "乌海市", "id": 101080301},
    {"en": "yantai", "cn": "烟台", "id": 101120501},
    {"en": "guangzhou", "cn": "广州", "id": 101280101},
    {"en": "baoding", "cn": "保定", "id": 101090201},
    {"en": "yangzhou", "cn": "扬州", "id": 101190601},
    {"en": "nanchong", "cn": "南充", "id": 101270501},
    {"en": "wuxi", "cn": "无锡", "id": 101190201},
    {"en": "fuzhou", "cn": "福州", "id": 101230101},
    {"en": "hefei", "cn": "合肥", "id": 101220101},
    {"en": "nanning", "cn": "南宁", "id": 101300101},
    {"en": "lasa", "cn": "拉萨", "id": 101140101},
    {"en": "guiyang", "cn": "贵阳", "id": 101260101},
    {"en": "nanchang", "cn": "南昌", "id": 101240101},
    {"en": "changsha", "cn": "长沙", "id": 101250101},
    {"en": "yanan", "cn": "延安", "id": 101110300},
    {"en": "liupanshui", "cn": "六盘水", "id": 101260803},
    {"en": "xianyang", "cn": "咸阳", "id": 101110200},
    {"en": "chengdu", "cn": "成都", "id": 101270101},
    {"en": "shanghai", "cn": "上海", "id": 101020100},
    {"en": "yulin", "cn": "榆林", "id": 101110401},
    {"en": "zhengzhou", "cn": "郑州", "id": 101180101}
]

# 默认配置
DEFAULT_CONFIG = {
    "USE_RELATIVE_DATES": True,
    "DAYS_TO_FETCH": 30,
    "START_DATE": "2023-03-01",
    "END_DATE": "2023-05-31",
    "REQUEST_DELAY": 2,
    "REQUEST_TIMEOUT": 10,
    "MAX_RETRIES": 3,
    "OUTPUT_FORMAT": "csv",
    "ADD_DATE_TO_FILENAME": True,
    "FILENAME_PREFIX": "pollen_data",
    "OUTPUT_ENCODING": "utf-8-sig",
    "SELECTED_CITIES": []
}

# 花粉等级描述
POLLEN_LEVELS = [
    {"level": "未检测", "color": "#999999", "message": "无花粉"},
    {"level": "很低", "color": "#81CB31", "message": "不易引发过敏反应"},
    {"level": "较低", "color": "#A1FF3D", "message": "对极敏感人群可能引发过敏反应"},
    {"level": "偏高", "color": "#F5EE32", "message": "易引发过敏，加强防护，对症用药"},
    {"level": "较高", "color": "#FFAF13", "message": "易引发过敏，加强防护，规范用药"},
    {"level": "很高", "color": "#FF2319", "message": "极易引发过敏，减少外出，持续规范用药"},
    {"level": "极高", "color": "#AD075D", "message": "极易引发过敏，建议足不出户，规范用药"}
] 