var series_index = {};

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

// Picked palette from http://www.colourlovers.com/palette/160924/DANCE_TO_THE_CHARTS
var strokeStyles = ["rgb(183,247,49)",
                    "rgb(255,194,38)",
                    "rgb(255,41,126)",
                    "rgb(194,61,255)",
                    "rgb(69,224,211)"];
var fillStyles = ["rgba(183,247,49,0.2)",
                  "rgba(255,194,38,0.2)",
                  "rgba(255,41,126,0.2)",
                  "rgba(194,61,255,0.2)",
                  "rgba(69,224,211,0.2)"];


function update_metrics(message) {
    data = $.parseJSON(message.data);
    $.each(data, function(metric, measure) {
        var timeseries = series_index[metric];
        timeseries.append(measure.time, measure.value); });
};


function setup_charts(charts_data) {
    var template = $('#chart_template');
    var container = $('#charts');

    $.each(charts_data, function(i, names) {
        var chart_obj = {};
        // Setup DOM
        var chart_dom = template.clone();
        chart_dom.removeAttr('style');
        $('h3', chart_dom).text(names[0]);
        container.append(chart_dom);

        // Setup chart
        var chart = new SmoothieChart(chart_options);
        chart.streamTo($('canvas', chart_dom).get(0));

        $.each(names, function(i, name) {
            var timeseries = new TimeSeries();
            var options = $.extend({}, timeseries_options);
            options.strokeStyle = strokeStyles[i % strokeStyles.length];
            options.fillStyle = fillStyles[i % fillStyles.length];
            chart.addTimeSeries(timeseries, options);
            chart_obj.timeseries = timeseries;
            series_index[name] = timeseries;
        });
    });

    init_websocket();
};

function init_websocket() {
    var ws = new WebSocket("ws://" + document.domain + ":5000/data");
    ws.onmessage = update_metrics;
};

$(document).ready(function(){
    $.ajax('/charts', {dataType: 'json', success: setup_charts});
});
