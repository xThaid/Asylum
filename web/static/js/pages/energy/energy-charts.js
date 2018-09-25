
function genChart(data) {
    Chart.defaults.global.elements.point.radius = 0;
    let ctx = document.getElementById("power-today-chart").getContext('2d');
    window.myChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            legend: {
                display: false
            },
            maintainAspectRatio: false,
            responsive: true,
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }],
                xAxes:[{
                    ticks:{
                        autoSkip: true,
                        maxTicksLimit: 24
                    }
                }]
            }
        }
    });
}

$('.peity-donut-green').peity('donut',{
    fill: ["#28B779", "#eeeeee"],
    radius: 40,
    innerRadius: 33
});
$('.peity-donut-red').peity('donut',{
    fill: ["#DA542E", "#eeeeee"],
    radius: 40,
    innerRadius: 33
});
$('.peity-donut-orange').peity('donut',{
    fill: ["#E1A500", "#eeeeee"],
    radius: 40,
    innerRadius: 33
});


$('.peity-bar-green').peity('bar',{
    fill: ["#28B779"],
    width: 80,
    height:80
});
$('.peity-bar-red').peity('bar',{
    fill: ["#DA542E"],
    width: 80,
    height:80
});
$('.peity-bar-orange').peity('bar',{
    fill: ["#E1A500"],
    width: 80,
    height:80
});

function updateCell(name, value){
    let maxPower = 4000;
    $('#' + name + '_peity').text(value + "/" + maxPower).change();
    $('#' + name).text(value);
}

function update_data(){
    $.ajax({
        url         : "energy/getCurrentPowerData",
        type        : "GET",
        contentType : 'application/json',
        dataType    : 'json',
        success    : function (response) {
            updateCell('production_current', response.production);

            updateCell('consumption_current', response.consumption);

            updateCell('summary_power_use', response.use);
            updateCell('summary_power_import', response.import);
            updateCell('summary_power_export', response.export);
            updateCell('summary_power_store', response.store);
        }
    });
    setTimeout(update_data, 1000);
}

jQuery(document).ready(function(){
	update_data()
});
