function get_option(opData){
    var option = {
        title: {
            text: ''
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data:opData.names
        },
        grid: {
            left: '10',
            right: '1%',
            bottom: '3%',
            top: '120',
            containLabel: true
        },
        toolbox: {
            feature: {
                saveAsImage: {}
            }
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: opData.years
        },
        yAxis: {
            type: 'value'
        },
        series: opData.items
    };
    return option;
}

function init_chart(chartId){
    var myChart = echarts.init(document.getElementById(chartId));
    myChart.showLoading();

    var api_url = "/ohlc/pages/gdp";
    $.post(api_url, {"duration": chartId}, function (data){
        // data = JSON.parse(data);
        myChart.hideLoading();
        option = get_option(data['data']);
        myChart.setOption(option);
    }, "json");
}

init_chart('gdp');

