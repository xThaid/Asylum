
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

    $('#productionPowerChart').peity('donut',{
        fill: ["green", "#eeeeee"],
        radius: 22,
        innerRadius: 13
    });
     $('#productionPowerChart2').peity('bar',{
        fill: ["purple"],
         height: 40,
         width: 80
    });

     $('#productionPowerChart3').peity('donut',{
        fill: ["green", "#eeeeee"],
        radius: 22,
        innerRadius: 13
    });
     $('#productionPowerChart4').peity('donut',{
        fill: ["green", "#eeeeee"],
        radius: 22,
        innerRadius: 13

    });
}
