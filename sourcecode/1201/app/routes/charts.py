"""Get charts data."""


from app.constants.general import PIE_CHART_MAX_LABELS, PIE_CHARTS_OTHERS


def get_pie_chart_data(chart_results, label_field, count_field):
    """Get data for pie chart.

    :param chart_results: Results to be used on pie chart
    :type chart_results: list
    :param label_field: Label field to be used to label values
    :type label_field: str
    :param count_field: Count field to be used to get count
    :type count_field: str
    :return: Data to be used by Pie Chart
    :rtype: dict
    """
    response = []
    tot_count = 0
    count = 0
    # Sort chart data
    chart_results.sort(key=lambda x: x[1])

    for index, item in enumerate(chart_results[::-1]):
        if index < PIE_CHART_MAX_LABELS:
            data = {label_field: item[0], count_field: item[1]}
            response.append(data)
        else:
            count += 1
            item_count = item[1]
            tot_count += float(item_count)
    if tot_count:
        data = {
            label_field: f"{PIE_CHARTS_OTHERS} ({count})",
            count_field: int(tot_count),
        }
        response.append(data)

    return response


def get_bar_graph_data(chart_results, count_of_sightings, time):
    """Get data for bar chart.

    :param chart_results: Results to be used on bar chart
    :type chart_results: list
    :param time: time field to be used for sighting created time
    :type time: str
    :param count_of_sightings: Count field to be used to get count of sightings
    :type count_of_sightings: str
    :return: Data to be used by bar Chart
    :rtype: dict
    """
    # Sort chart data
    chart_results.sort(key=lambda x: x[1])
    bar_graph_data = []
    for sighting_data in chart_results[::-1]:

        data = {count_of_sightings: sighting_data[0], time: sighting_data[1]}
        bar_graph_data.append(data)
    return bar_graph_data


def get_bar_graph_data_by_observable_type(
    chart_results, sighting_count, observable_type
):
    """Get data for bar chart.

    :param chart_results: Results to be used on bar chart
    :type chart_results: list
    :param observable_type: type field to be used for sighting created time
    :type observable_type: str
    :param sighting_count: Count field to be used to get count of sightings
    :type sighting_count: str
    :return: Data to be used by bar Chart
    :rtype: dict
    """
    bar_graph_data = []
    for sighting_data in chart_results:
        data = {sighting_count: sighting_data[0], observable_type: sighting_data[1]}
        bar_graph_data.append(data)
    return bar_graph_data
