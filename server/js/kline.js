function get_option(opData){
    var series = [{
        type: 'candlestick',
        name: 'ohlcs',
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

    for(var name in opData['mas']){
        series.push({
            type: 'line',
            name: name,
            data: opData['mas'][name],
            smooth: true,
            showSymbol: false,
            lineStyle: {
                normal: {
                    color: 'yellow',
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

        tooltip: {
            trigger: 'axis',
            formatter: '{b0}<br/>oclh<br/>{c0}<br/>',
            axisPointer: {
                animation: false,
                lineStyle: {
                    color: '#376df4',
                    width: 2,
                    opacity: 1
                }
            }
        },

        grid: {
            left: '50',
            right: '1%',
            bottom: '60',
            top: '50',
        },

        xAxis: {
            type: 'category',
            data: opData['dates'],
            axisLine: { lineStyle: { color: 'red' } }
        },
        yAxis: {
            type: 'log',
            logBase: 1.05,
            scale: true,
            axisLabel: {
                formatter: function (value, index) {
                    var num = new Number(value);
                    return num.toFixed(2);
                }
            },
            axisLine: { lineStyle: { color: 'red' } },
            splitLine: {
                show: true,
                lineStyle: {
                    type: 'dashed'
                }
            }

        },
        dataZoom: [{
            show: true,
            type: 'slider',
            start: 5,
            end: 100,
        }],

        animation: false,
        series: series
    };
    return option;
}

function update_series(chart, originOption, opData){
    var series = originOption.series;

    for(var i = 0; i < series.length; i++){
        if(series[i].name == 'ohlcs'){
            series[i].data = opData['ohlcs'].concat(series[i].data);
        }else{
            series[i].data = opData['mas'][series[i].name].concat(series[i].data);
        }
    }
    var n = opData.dates.length;
    var option = {
        series: series,
        xAxis: {
            data: opData['dates'].concat(originOption.xAxis[0].data)
        },
        dataZoom: [{
            start: null,
            end: null,
            startValue: originOption.dataZoom[0].startValue + n,
            endValue: originOption.dataZoom[0].endValue + n
        }]
    };
    return option;
}

function init_chart(chartId){
    var myChart = echarts.init(document.getElementById(chartId));
    var src = $("#monthly").attr('data-src');
    var code = $("#monthly").attr('data-code');
    myChart.showLoading();

    var api_url = "/ohlc/" + src + "/"+ code
    $.post(api_url, {"duration": chartId}, function (data){
        // data = JSON.parse(data);
        myChart.hideLoading();
        option = get_option(data['data']);
        myChart.setOption(option);
    }, "json");

    myChart.on('datazoom', function (params) {
        if(params.start == 0){
            myChart.showLoading();
            var originOption = myChart.getOption();
            var enddate = originOption.xAxis[0].data[0];
            $.post(api_url, {"duration": chartId, "enddate": enddate}, function (data){
                myChart.hideLoading();
                if(data['code'] == 0 && data.data.n > 0){
                    option = update_series(myChart, originOption, data['data']);
                    myChart.setOption(option);
                }else{
                    console.log(data);
                }
            }, "json");
        }
    });
}

init_chart('monthly');
init_chart('weekly')
init_chart('daily')

