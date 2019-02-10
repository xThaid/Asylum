
var chartColorPlugin = { beforeDraw: function (chart) {
        var ctx = chart.chart.ctx;
        var ruleIndex = 0;
        var rules = chart.chart.options.backgroundRules;
        var yaxis = chart.chart.scales["y-axis-0"];
        var xaxis = chart.chart.scales["x-axis-0"];
        var dev = rules[1].yAxisSegement - rules[0].yAxisSegement;
        if(rules[0].yAxisSegement < 0)
            dev = 5;
        if (yaxis.ticksAsNumbers[0] - yaxis.ticksAsNumbers[yaxis.ticksAsNumbers.length - 1] < 6)
            dev = 1;
        var start_dev = yaxis.ticksAsNumbers[yaxis.ticksAsNumbers.length - 1] / dev;
        var stop_dev = yaxis.ticksAsNumbers[0] / dev;
        var start = Math.floor(start_dev);
        var stop = Math.ceil(stop_dev);
        var partPercentage = 1.0 / (stop_dev - start_dev);

        for(var i=start;i<stop;i++){
          /* Linie na granicach przedziałów
          if(i == Math.round(rules[ruleIndex].yAxisSegement / dev) && i > start){
            ctx.fillStyle = "rgba(100,100,100,1)";
            ctx.fillRect(xaxis.left, yaxis.top + (stop_dev - i) * (yaxis.height * partPercentage), xaxis.width, 10);
          }
          */
          if(i<rules[ruleIndex].yAxisSegement / dev){
            ctx.fillStyle = rules[ruleIndex].backgroundColor;
          if(i==start){
            ctx.fillRect(xaxis.left, yaxis.top + (stop_dev- i - 1 ) * (yaxis.height * partPercentage), xaxis.width, yaxis.height * partPercentage*(1-Math.abs(start - start_dev)));
            }
          else if(i==(stop - 1)){
            ctx.fillRect(xaxis.left, yaxis.top + ((stop - i - 1) * (yaxis.height * partPercentage)), xaxis.width, 1+ yaxis.height * partPercentage*(1-Math.abs(stop - stop_dev)));
          }else{
            ctx.fillRect(xaxis.left, yaxis.top + (stop_dev - i - 1) * (yaxis.height * partPercentage), xaxis.width,1 + yaxis.height * partPercentage);
          }
          }else{
            ruleIndex++;
            i--;
          }
        }
        if(chart.chart.options.linePosition !=null){
          var position = yaxis.height/(yaxis.ticksAsNumbers[0] - yaxis.ticksAsNumbers[yaxis.ticksAsNumbers.length - 1]);
          var pos2 = (yaxis.ticksAsNumbers[0]- chart.chart.options.linePosition)*position;

          ctx.fillStyle = "rgba(255,0,0,1)";
          ctx.fillRect(xaxis.left, yaxis.top + pos2, xaxis.width, 1.5);
      }
      } };

function genTemperatureChart(data, average) {
    Chart.defaults.global.elements.point.radius = 0;
    let ctx = document.getElementById("temperature-chart").getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            legend: {
                display: false
            },
             tooltips: {
                intersect: false,
                 mode: 'index',
                 position: 'nearest',
                callbacks: {
                  label: function(tooltipItem){
                      return data['datasets'][tooltipItem.datasetIndex]['label'] + ": "+ tooltipItem.yLabel + ' °C';
                  }
                },
              },
            maintainAspectRatio: false,
            responsive: true,
            scales: {
                yAxes: [{
                    ticks: {
                        callback: function(value) {
                            return value + ' °C';
                        },
                        beginAtZero: false,
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
            },
              backgroundRules: [{
                  backgroundColor: "rgba(0, 102, 204, 1)",
                  yAxisSegement: -15
              }, {
                  backgroundColor: "rgba(0, 204, 255, 1)",
                  yAxisSegement: -5
              }, {
                  backgroundColor: "rgba(0, 255, 153, 1)",
                  yAxisSegement: 5
              }, {
                  backgroundColor: "rgba(255, 255, 102, 1)",
                  yAxisSegement: 15
              }, {
                  backgroundColor: "rgba(255, 204, 0, 1)",
                  yAxisSegement: 25
              }, {
                  backgroundColor: "rgba(255, 102, 0, 1)",
                  yAxisSegement: 35
              }, {
                  backgroundColor: "rgba(204, 51, 0, 1)",
                  yAxisSegement: Infinity
              }],
              linePosition: average
        },
        plugins: [chartColorPlugin]
    });
}

function genHumidityChart(data, average) {
    Chart.defaults.global.elements.point.radius = 0;
    let ctx = document.getElementById("humidity-chart").getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            legend: {
                display: false
            },
             tooltips: {
                intersect: false,
                 mode: 'index',
                 position: 'nearest',
                callbacks: {
                  label: function(tooltipItem){
                      return data['datasets'][tooltipItem.datasetIndex]['label'] + ": "+ tooltipItem.yLabel + ' %';
                  }
                },
              },
            maintainAspectRatio: false,
            responsive: true,
            scales: {
                yAxes: [{
                    ticks: {
                        callback: function(value) {
                            return value + ' %';
                        },
                        beginAtZero: false,
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
            },
            backgroundRules: [{
                backgroundColor: "rgba(255, 204, 0, 1)",
                yAxisSegement: 20
            }, {
                backgroundColor: "rgba(255, 255, 102, 1)",
                yAxisSegement: 40
            }, {
                backgroundColor: "rgba(0, 255, 153, 1)",
                yAxisSegement: 60
            }, {
                backgroundColor: "rgba(0, 204, 255, 1)",
                yAxisSegement: 80
            }, {
                backgroundColor: "rgba(0, 102, 204, 1)",
                yAxisSegement: Infinity
            }],
            linePosition: average
        },
        plugins: [chartColorPlugin]
    });
}
function genPressureChart(data, average) {
    Chart.defaults.global.elements.point.radius = 0;
    let ctx = document.getElementById("pressure-chart").getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            legend: {
                display: false
            },
             tooltips: {
                intersect: false,
                 mode: 'index',
                 position: 'nearest',
                callbacks: {
                  label: function(tooltipItem){
                      return data['datasets'][tooltipItem.datasetIndex]['label'] + ": "+ tooltipItem.yLabel + ' hPa';
                  }
                },
              },
            maintainAspectRatio: false,
            responsive: true,
            scales: {
                yAxes: [{
                    ticks: {
                        callback: function(value) {
                            return value + ' hPa';
                        },
                        beginAtZero: false,
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
            },
            backgroundRules: [{
                backgroundColor: "rgba(0, 102, 204, 1)",
                yAxisSegement: 990
            }, {
                backgroundColor: "rgba(0, 204, 255, 1)",
                yAxisSegement: 1000
            }, {
                backgroundColor: "rgba(0, 255, 153, 1)",
                yAxisSegement: 1020
            }, {
                backgroundColor: "rgba(255, 255, 102, 1)",
                yAxisSegement: 1030
            }, {
                backgroundColor: "rgba(255, 204, 0, 1)",
                yAxisSegement: Infinity
            }],
            linePosition: average
        },
        plugins: [chartColorPlugin]
    });
}
function genDustChart(data, average) {
    Chart.defaults.global.elements.point.radius = 0;
    let ctx = document.getElementById("dust-chart").getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            legend: {
                display: false
            },
             tooltips: {
                intersect: false,
                 mode: 'index',
                 position: 'nearest',
                callbacks: {
                  label: function(tooltipItem){
                      return data['datasets'][tooltipItem.datasetIndex]['label'] + ": "+ tooltipItem.yLabel + ' µg/m³';
                  }
                },
              },
            maintainAspectRatio: false,
            responsive: true,
            scales: {
                yAxes: [{
                    ticks: {
                        callback: function(value) {
                            return value + ' µg/m³';
                        },
                        beginAtZero: false,
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
        },
        backgroundRules: [{
            backgroundColor: "rgba(112, 202, 44, 1)",
            yAxisSegement: 25
        }, {
            backgroundColor: "rgba(211, 209, 36, 1)",
            yAxisSegement: 50
        }, {
            backgroundColor: "rgba(239, 174, 22, 1)",
            yAxisSegement: 75
        }, {
            backgroundColor: "rgba(239, 119, 40, 1)",
            yAxisSegement: 100
        }, {
            backgroundColor: "rgba(179, 12, 90, 1)",
            yAxisSegement: Infinity
        }],
        linePosition: average
    },
    plugins: [chartColorPlugin]
    });
}
