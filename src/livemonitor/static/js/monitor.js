var charts = {};

var chart_options = {
    minValue: 0,
    fps: 12,
    millisPerPixel: 100,
    resetBoundsInterval: 60000,
    grid: { strokeStyle:'rgb(128, 128, 128)',
            fillStyle:'rgb(255, 255, 255)',
            lineWidth: 0.5,
            millisPerLine: 5000,
            verticalSections: 8, },
    labels: { fillStyle: 'rgb(0, 0, 0)'}};

var timeseries_options = {
    strokeStyle: 'rgb(0, 255, 0)',
    fillStyle: 'rgba(0, 255, 0, 0.4)',
    lineWidth: 3};


function setup_metric(i, name) {
    charts[name] = {};
    metric = charts[name];
    metric.name = name;
    metric.chart = new SmoothieChart(chart_options);
    metric.chart.streamTo(document.getElementById(name), 2000);
    metric.timeseries = new TimeSeries();
    metric.chart.addTimeSeries(
        metric.timeseries, timeseries_options);
};


function update_metrics(message) {
    data = $.parseJSON(message.data);
    $.each(data, function(metric, measure) {
        charts[metric].timeseries.append(measure.time, measure.value); });
};


$(document).ready(function(){
    var metrics = ['haproxy_requests', 'haproxy_errors'];
    $.each(metrics, setup_metric);

    charts['haproxy_errors'].timeseries.referenceSeries = charts['haproxy_requests'].timeseries;

    var ws = new WebSocket("ws://" + document.domain + ":5000/data");
    ws.onmessage = update_metrics;
});
