/**
 * 花粉地图修复工具的JavaScript功能
 */
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('extract-button').addEventListener('click', function() {
        const sourceHtml = document.getElementById('source-html').value;
        const outputEl = document.getElementById('output-html');
        const statusEl = document.getElementById('status');
        
        if (!sourceHtml.trim()) {
            statusEl.innerHTML = '<span class="error">请先粘贴原始地图HTML内容</span>';
            return;
        }
        
        try {
            // 从源HTML中提取日期
            let dateMatch = sourceHtml.match(/全国花粉分布地图 - (\d{4}-\d{2}-\d{2})/);
            let mapDate = dateMatch ? dateMatch[1] : '未知日期';
            
            // 从源HTML中提取数据数组
            let dataArrays = [];
            const dataRegex = /"data": \[\s*([\s\S]*?)\s*\]/g;
            let match;
            
            while ((match = dataRegex.exec(sourceHtml)) !== null) {
                if (match[1].trim()) {
                    dataArrays.push(match[1]);
                }
            }
            
            if (dataArrays.length === 0) {
                statusEl.innerHTML = '<span class="error">无法从源HTML中提取数据</span>';
                return;
            }
            
            // 构建新的花粉数据
            let pollenData = [];
            const nameValueRegex = /"name": "([^"]+)"[\s\S]*?"value": \[([\s\S]*?)\]/g;
            let matches = dataArrays.join(',').matchAll(nameValueRegex);
            
            for (const match of matches) {
                const name = match[1];
                const valueParts = match[2].split(',');
                if (valueParts.length >= 3) {
                    const value = parseInt(valueParts[2].trim());
                    pollenData.push({ name, value });
                }
            }
            
            // 如果没有数据，尝试其他方式提取
            if (pollenData.length === 0) {
                const simpleNameValueRegex = /"name": "([^"]+)"[\s\S]*?"value": (\d+)/g;
                let simpleMatches = sourceHtml.matchAll(simpleNameValueRegex);
                
                for (const match of simpleMatches) {
                    const name = match[1];
                    const value = parseInt(match[2]);
                    pollenData.push({ name, value });
                }
            }
            
            // 去除重复项
            const uniqueNames = new Set();
            pollenData = pollenData.filter(item => {
                if (uniqueNames.has(item.name)) {
                    return false;
                }
                uniqueNames.add(item.name);
                return true;
            });
            
            // 生成新的HTML
            const newHtml = generateMapHtml(mapDate, pollenData);
            
            outputEl.value = newHtml;
            statusEl.innerHTML = `<span class="success">处理成功!</span><br>
            提取到${pollenData.length}个城市的花粉数据，日期: ${mapDate}<br>
            请复制上面的HTML内容并保存为新文件`;
            
        } catch (error) {
            console.error(error);
            statusEl.innerHTML = `<span class="error">处理失败: ${error.message}</span><br>请检查输入的HTML格式是否正确`;
        }
    });
});

/**
 * 生成修复后的地图HTML
 * @param {string} mapDate - 地图日期
 * @param {Array} pollenData - 花粉数据数组
 * @returns {string} - 生成的HTML
 */
function generateMapHtml(mapDate, pollenData) {
    return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>全国花粉分布地图 - ${mapDate}</title>
    <!-- 使用更可靠的CDN来加载ECharts和中国地图数据 -->
    <script src="https://cdn.bootcdn.net/ajax/libs/echarts/5.4.3/echarts.min.js"></script>
    <script src="https://cdn.bootcdn.net/ajax/libs/echarts/5.4.3/map/js/china.js"></script>
    
    <style>
        body {
            margin: 0;
            height: 100vh;
            overflow: hidden;
        }
        #map-container {
            width: 100%;
            height: 100%;
        }
    </style>
</head>
<body>
    <!-- 地图容器 -->
    <div id="map-container"></div>
    
    <script>
        // 确保地图和ECharts都已加载
        window.onload = function() {
            if (!echarts) {
                alert('ECharts库未能正确加载，请检查网络连接');
                return;
            }
            
            // 初始化地图
            var mapChart = echarts.init(document.getElementById('map-container'));
            
            // 花粉数据
            var pollenData = ${JSON.stringify(pollenData, null, 4)};
            
            // 确保地图数据已加载
            if (!echarts.getMap('china')) {
                console.error('中国地图数据未能正确加载');
                // 尝试手动注册一个空地图
                echarts.registerMap('china', {geoJSON: {"type":"FeatureCollection","features":[]}});
            }
            
            // 花粉级别与描述的映射
            var levelMap = {
                0: "暂无",
                1: "很低",
                2: "低",
                3: "较低",
                4: "中等",
                5: "偏高",
                6: "高",
                7: "较高",
                8: "很高",
                9: "极高",
                10: "爆表"
            };
            
            // 配置地图选项
            var option = {
                title: {
                    text: '全国花粉分布地图 - ${mapDate}',
                    left: 'center',
                    top: 20,
                    textStyle: {
                        fontSize: 24
                    }
                },
                tooltip: {
                    trigger: 'item',
                    formatter: function(params) {
                        var value = params.value;
                        if (value === undefined) value = 0;
                        var level = levelMap[value] || "未知";
                        return params.name + '<br>花粉水平: ' + value + ' (' + level + ')';
                    }
                },
                visualMap: {
                    min: 0,
                    max: 10,
                    left: 'left',
                    top: 'bottom',
                    text: ['高', '低'],
                    calculable: true,
                    inRange: {
                        color: ['#50a3ba', '#eac736', '#d94e5d']
                    }
                },
                series: [
                    {
                        name: '花粉水平',
                        type: 'map',
                        map: 'china',
                        roam: true,
                        label: {
                            show: true
                        },
                        emphasis: {
                            label: {
                                show: true
                            }
                        },
                        data: pollenData
                    }
                ]
            };
            
            // 渲染地图
            mapChart.setOption(option);
            
            // 监听窗口大小变化，调整地图大小
            window.addEventListener('resize', function() {
                mapChart.resize();
            });
            
            console.log('地图初始化完成');
        };
    </script>
</body>
</html>`;
} 