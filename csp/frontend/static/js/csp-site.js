// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/

$(function() {

    var chartDataURL = $("#chart").data("chart-data-url");

    $.getJSON(chartDataURL, function (data) {
        var graph = new Rickshaw.Graph({
            element: document.querySelector("#chart"),
            width: 1024,
            height: 200,
            series: [{
                color: 'steelblue',
                data: data.data
            }]
        });

        var x_axis = new Rickshaw.Graph.Axis.X( { graph: graph } );

        var y_axis = new Rickshaw.Graph.Axis.Y( {
            graph: graph,
            orientation: 'left'
            //tickFormat: Rickshaw.Fixtures.Number.formatKMBT
            //element: document.getElementById('y_axis'),
        });

        graph.render();
    });

});
