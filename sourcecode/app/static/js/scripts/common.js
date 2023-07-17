function plotPieChart(chartId, labels, datasets, lable) {
    var sum = datasets.reduce(myFunc);
    var newlabels = [];
    for (val = 0; val < labels.length; val++) {
        newlabels[val] = capitalizeTheFirstLetterOfEachWord(labels[val]) + ' - ' + Math.round((datasets[val] / sum) * 100) + '%';

    }
    for (val = 0; val < labels.length; val++) {
        if (labels[val] && labels[val].length > 20) {
            newlabels[val] = labels[val].substr(0, 6) + '...' + labels[val].substr(labels[val].length - 6, 6); //truncate
        } else {
            newlabels[val] = labels[val]
        }
    }
    function capitalizeTheFirstLetterOfEachWord(words) {
        var separateWord = words.toString().toLowerCase().split(' ');
        for (var val = 0; val < separateWord.length; val++) {
            separateWord[val] = separateWord[val].charAt(0).toUpperCase() +
                separateWord[val].substring(1);
        }
        return separateWord.join(' ');
    }
    function getColorArray() {
        return ['#FF6633', '#FFB399', '#FF33FF', '#FFFF99', '#00B3E6',
            '#E6B333', '#3366E6', '#999966', '#99FF99', '#B34D4D',
            '#80B300', '#809900', '#E6B3B3', '#6680B3', '#66991A',
            '#FF99E6', '#CCFF1A', '#FF1A66', '#E6331A', '#33FFCC',
            '#66994D', '#B366CC', '#4D8000', '#B33300', '#CC80CC',
            '#66664D', '#991AFF', '#E666FF', '#4DB3FF', '#1AB399',
            '#E666B3', '#33991A', '#CC9999', '#B3B31A', '#00E680',
            '#4D8066', '#809980', '#E6FF80', '#1AFF33', '#999933',
            '#FF3380', '#CCCC00', '#66E64D', '#4D80CC', '#9900B3',
            '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF'
        ];
    }


    function myFunc(total, num) {
        return parseInt(total) + parseInt(num);
    }
    var ctx = document.getElementById(chartId).getContext('2d');

    var myChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: newlabels,
            datasets: [{
                backgroundColor: getColorArray(),
                data: datasets
            }]
        },
        options: {
            responsive: 'true',
            maintainAspectRatio: 'false',

            legend: {
                display: true,
                position: 'right',
                labels: {
                    fontColor: 'black'
                },
                onClick: (e) => e.stopPropagation(),
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem, data) {
                        var allData = data.datasets[tooltipItem.datasetIndex].data;
                        var tooltipLabel = data.labels[tooltipItem.index];
                        if (tooltipLabel.length > 40) { tooltipLabel = tooltipLabel.substr(0, 39) }
                        var tooltipData = allData[tooltipItem.index];
                        var total = 0;
                        for (var i in allData) {
                            total += parseFloat(allData[i]);
                        }
                        var tooltipPercentage = Math.round((tooltipData / total) * 100);
                        return [lable + ': ' + tooltipLabel, 'Count:   ' + tooltipData, 'Count%:   ' + tooltipPercentage + '%'];
                    }
                }
            }

        }


    });
}


function plotBarGraph(chartId, chartObj, bar_level) {
    var ctx = document.getElementById(chartId).getContext("2d");

    var myHorizontalBar = new Chart(ctx, {
        type: 'bar',
        data: chartObj,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                display: false
            },
            scales: {
                yAxes: [{
                    barThickness: 20,
                    min: 0,
                    ticks: {
                        precision: 0,
                        beginAtZero: true,
                        display: true,
                        fontColor: 'black',
                        callback: function(value) {
                            if (value && value.length > 20) {
                                return value.substr(0, 6) + '...' + value.substr(value.length - 6, 6); //truncate
                            } else {
                                return value
                            }
                        }
                    }
                }],
                xAxes: [{
                    ticks: {
                        min: 0,
                        beginAtZeto: true,
                        fontColor: 'black'
                    },
                    beginAtZero: true,
                    scaleLabel: {
                        display: true,
                        fontColor: 'black'
                    }
                }]
            },
            tooltips: {

                callbacks: {
                    title: function(tooltipItems, data) {
                        var idx = tooltipItems[0].index;
                        return bar_level + ': ' + data.labels[idx]; //do something with title
                    },
                    label: function(tooltipItems, data) {
                        return 'count: ' + tooltipItems.yLabel;
                    }
                }
            }
        }
    });
}

function plotBarGraph2(chartId, chartObj, bar_level) {
    var ctx = document.getElementById(chartId).getContext("2d");

    var myHorizontalBar = new Chart(ctx, {
        type: 'horizontalBar',
        data: chartObj,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                display: false
            },
            scales: {
                yAxes: [{
                    barThickness: 20,
                    min: 0,
                    ticks: {
                        precision: 0,
                        beginAtZero: true,
                        display: true,
                        fontColor: 'black',
                        callback: function(value) {
                            if (value && value.length > 20) {
                                return value.substr(0, 6) + '...' + value.substr(value.length - 6, 6); //truncate
                            } else {
                                return value
                            }
                        }
                    }
                }],
                xAxes: [{
                    ticks: {
                        min: 0,
                        beginAtZeto: true,
                        fontColor: 'black'
                    },
                    beginAtZero: true,
                    scaleLabel: {
                        display: true,
                        fontColor: 'black'
                    }
                }]
            },
            tooltips: {

                callbacks: {
                    title: function(tooltipItems, data) {
                        var idx = tooltipItems[0].index;
                        return bar_level + ': ' + data.labels[idx]; //do something with title
                    },
                    label: function(tooltipItems, data) {
                        return 'count: ' + tooltipItems.xLabel;
                    }
                }
            }
        }
    });
}
