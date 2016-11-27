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
                    var num = new Number(value);
                    return num.toFixed(2);
                }
            },
            axisLine: { lineStyle: { color: '#8392A5' } },
            splitLine: { show: true }

        },
        dataZoom: [
            {
                show: true,
                type: 'slider',
                // y: '90%',
                start: 50,
                end: 100,
            },
            {
                type: 'inside',
                start: 50,
                end: 100
            }],
        animation: false,
        series: series
    };
    return option;
}

function get_series(opData){
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

    myChart.on('datazoom', function (params) {
        if(params.start == 0){
            $.post("/stk/kline/000001", {"duration": chartId, "enddate": "20160513"}, function (data){
                option = get_series(data['data']);
                myChart.setOption(option);
            }, "json");
        }
    });
}

init_chart('monthly');
init_chart('weekly')
init_chart('daily')

