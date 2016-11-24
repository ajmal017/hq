function get_option(opData){
    var series = [{
        type: 'candlestick',
        data: opData['ohlcs'],
        itemStyle: {
            normal: {
                color: '#FD1050',
                color0: '#0CF49B',
                borderColor: '#FD1050',
                borderColor0: '#0CF49B'
            }
        }
    }]

    for(var i = 0; i < opData['mas'].length; i ++){
        series.push({
            type: 'line',
            data: opData['mas'][i],
            smooth: true,
            showSymbol: false,
            lineStyle: {
                normal: {
                    color: 'green',
                    width: 1
                }
            }
        })
    }
    var option = {
        backgroundColor: '#21202D',
        legend: {
            inactiveColor: '#777',
            textStyle: {
                color: '#fff'
            },
            left: 0,
            right: 0,
            bottom: 0,
            top:0,
            padding: [0, 0, 0, 0]
        },

        xAxis: {
            type: 'category',
            data: opData['dates'],
            axisLine: { lineStyle: { color: '#8392A5' } }
        },
        yAxis: {
            type: 'log',
            logBase: 1.1,
            scale: true,
            axisLabel: {
                formatter: function (value, index) {
                    // 格式化成月/日，只在第一个刻度显示年份
                    var num = new Number(value);
                    return num.toFixed(2);
                }
            },
            axisLine: { lineStyle: { color: '#8392A5' } },
            splitLine: { show: true }

        },
        dataZoom: [{
            textStyle: {
                color: '#8392A5'
            },
            handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
            handleSize: '100%',
            dataBackground: {
                areaStyle: {
                    color: '#8392A5'
                },
                lineStyle: {
                    opacity: 0.8,
                    color: '#8392A5'
                }
            },
            handleStyle: {
                color: '#fff',
                shadowBlur: 3,
                shadowColor: 'rgba(0, 0, 0, 0.6)',
                shadowOffsetX: 2,
                shadowOffsetY: 2
            }
        }, {
            type: 'inside'
        }],
        animation: false,
        series: series
    };
    return option;
}

function init_chart(chartId){
    var myChart = echarts.init(document.getElementById(chartId));
    myChart.showLoading();
    $.post("/stk/kline/000001", {"duration": chartId}, function (data){
        // data = JSON.parse(data);
        myChart.hideLoading();
        option = get_option(data['data']);
        myChart.setOption(option);
    }, "json");
}

init_chart('monthly');
init_chart('weekly')
init_chart('daily')

