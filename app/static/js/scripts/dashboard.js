function pie_chart_by_confidence_success(data) {
    context_data = JSON.stringify(data)
    context_data = JSON.parse(context_data)
    other_data = JSON.stringify(context_data.other)
    other_data = other_data.replace(/"/g, '')
    other_data = other_data.replace(/'/g, '"')
    other_data = JSON.parse(other_data)
    pie_data = JSON.stringify(other_data.pie_data)
    pie_data = JSON.parse(pie_data)
  if (!(pie_data) || pie_data.length === 0) {
        $("#chart2Body_nodata").show();
        document.getElementById("chartContainer2").style.minHeight = "200px";
        document.getElementById("chartContainer2").style.height = "200px";
        return { "ERROR": "No data recieved." };
    }
    var labels = [];
    var datasets = [];
    for (index = 0; index < pie_data.length; index++) {
        labels[index] = pie_data[index].confidence;
        datasets[index] = pie_data[index].count;
    }
    plotPieChart('chart2', labels, datasets, "confidence");

}

 function indicator_matches_by_histogram_success(data) {
    context_data = JSON.stringify(data)
    context_data = JSON.parse(context_data)
    other_data = JSON.stringify(context_data.other)
    other_data = other_data.replace(/"/g, '')
    other_data = other_data.replace(/'/g, '"')
    other_data = JSON.parse(other_data)
   bar_data = JSON.stringify(other_data.bar_chart1)
    bar_data = JSON.parse(bar_data)
        if (!(bar_data) || bar_data.length === 0) {
            $("#chart1Body_nodata").show();
            document.getElementById("chartContainer1").style.height = "200px";
            return { "ERROR": "No data recieved." };
        }

        var labels = [];
        var datasets = [];

        for (index = 0; index < bar_data.length; index++) {
            labels[index] = bar_data[index].time;
            datasets[index] = bar_data[index].count;
        }

        var horizontalBarChartData = {
            labels: labels,
            datasets: [{
                label: "location",
                backgroundColor: "#00b0f0",
                data: datasets
            }]

        };

        plotBarGraph('chart1', horizontalBarChartData, 'time');
    }

    function top_10_indicator_type_success(data) {
     context_data = JSON.stringify(data)
     context_data = JSON.parse(context_data)
     other_data = JSON.stringify(context_data.other)
     other_data = other_data.replace(/"/g, '')
     other_data = other_data.replace(/'/g, '"')
     other_data = JSON.parse(other_data)
     bar_data1 = JSON.stringify(other_data.bar_chart2)
     bar_data1 = JSON.parse(bar_data1)
        if (!(bar_data1) || bar_data1.length === 0) {
            $("#chart3Body_nodata").show();
            document.getElementById("chartContainer3").style.height = "200px";
            return { "ERROR": "No data recieved." };
        }
        var labels = [];
        var datasets = [];

        for (index = 0; index < bar_data1.length; index++) {
            labels[index] = bar_data1[index].type;
            datasets[index] = bar_data1[index].count;
        }
        var horizontalBarChartData = {
            labels: labels,
            datasets: [{
                label: "type",
                backgroundColor: "#00b0f0",
                data: datasets
            }]

        };

        plotBarGraph2('chart3', horizontalBarChartData, 'type');
    }
