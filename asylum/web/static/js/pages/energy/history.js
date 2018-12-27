function genPowerChart(data) {
    Chart.defaults.global.elements.point.radius = 0;
    let ctx = document.getElementById("power-today-chart").getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            legend: {
                display: true
            },
             tooltips: {
                intersect: false,
                 mode: 'index',
                 position: 'nearest',
                callbacks: {
                  label: function(tooltipItem){
                      return data['datasets'][tooltipItem.datasetIndex]['label'] + ": "+ tooltipItem.yLabel + ' W';
                  }
                },
              },
            maintainAspectRatio: false,
            responsive: true,
            scales: {
                yAxes: [{
                    ticks: {
                        callback: function(value) {
                            return value + ' W';
                        },
                        beginAtZero: true,
                        autoSkip: true,
                        maxTicksLimit: 10
                    },
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

function genEnergyChart(data) {
    Chart.defaults.global.elements.point.radius = 0;
    let ctx = document.getElementById("energy-today-chart").getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            legend: {
                display: true
            },
             tooltips: {
                callbacks: {
                  label: (item) => `${item.yLabel} kWh`,
                },
              },
            maintainAspectRatio: false,
            responsive: true,
            scales: {
                yAxes: [{
                    ticks: {
                        callback: function(value) {
                            return value + ' kWh';
                        },
                        beginAtZero: true,
                        autoSkip: true,
                        maxTicksLimit: 10
                    },
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

function createPeity(){
    $('.peity-bar-green').peity('bar',{
        fill: ["#28B779"],
        width: 90,
        height:90
    });
    $('.peity-bar-red').peity('bar',{
        fill: ["#DA542E"],
        width: 90,
        height:90
    });
    $('.peity-bar-orange').peity('bar',{
        fill: ["#E1A500"],
        width: 90,
        height:90
    });
}
