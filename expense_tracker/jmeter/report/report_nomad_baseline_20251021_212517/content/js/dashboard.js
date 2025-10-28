/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
var showControllersOnly = false;
var seriesFilter = "";
var filtersOnlySampleSeries = true;

/*
 * Add header in statistics table to group metrics by category
 * format
 *
 */
function summaryTableHeader(header) {
    var newRow = header.insertRow(-1);
    newRow.className = "tablesorter-no-sort";
    var cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Requests";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 3;
    cell.innerHTML = "Executions";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 7;
    cell.innerHTML = "Response Times (ms)";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Throughput";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 2;
    cell.innerHTML = "Network (KB/sec)";
    newRow.appendChild(cell);
}

/*
 * Populates the table identified by id parameter with the specified data and
 * format
 *
 */
function createTable(table, info, formatter, defaultSorts, seriesIndex, headerCreator) {
    var tableRef = table[0];

    // Create header and populate it with data.titles array
    var header = tableRef.createTHead();

    // Call callback is available
    if(headerCreator) {
        headerCreator(header);
    }

    var newRow = header.insertRow(-1);
    for (var index = 0; index < info.titles.length; index++) {
        var cell = document.createElement('th');
        cell.innerHTML = info.titles[index];
        newRow.appendChild(cell);
    }

    var tBody;

    // Create overall body if defined
    if(info.overall){
        tBody = document.createElement('tbody');
        tBody.className = "tablesorter-no-sort";
        tableRef.appendChild(tBody);
        var newRow = tBody.insertRow(-1);
        var data = info.overall.data;
        for(var index=0;index < data.length; index++){
            var cell = newRow.insertCell(-1);
            cell.innerHTML = formatter ? formatter(index, data[index]): data[index];
        }
    }

    // Create regular body
    tBody = document.createElement('tbody');
    tableRef.appendChild(tBody);

    var regexp;
    if(seriesFilter) {
        regexp = new RegExp(seriesFilter, 'i');
    }
    // Populate body with data.items array
    for(var index=0; index < info.items.length; index++){
        var item = info.items[index];
        if((!regexp || filtersOnlySampleSeries && !info.supportsControllersDiscrimination || regexp.test(item.data[seriesIndex]))
                &&
                (!showControllersOnly || !info.supportsControllersDiscrimination || item.isController)){
            if(item.data.length > 0) {
                var newRow = tBody.insertRow(-1);
                for(var col=0; col < item.data.length; col++){
                    var cell = newRow.insertCell(-1);
                    cell.innerHTML = formatter ? formatter(col, item.data[col]) : item.data[col];
                }
            }
        }
    }

    // Add support of columns sort
    table.tablesorter({sortList : defaultSorts});
}

$(document).ready(function() {

    // Customize table sorter default options
    $.extend( $.tablesorter.defaults, {
        theme: 'blue',
        cssInfoBlock: "tablesorter-no-sort",
        widthFixed: true,
        widgets: ['zebra']
    });

    var data = {"OkPercent": 0.0, "KoPercent": 100.0};
    var dataset = [
        {
            "label" : "FAIL",
            "data" : data.KoPercent,
            "color" : "#FF6347"
        },
        {
            "label" : "PASS",
            "data" : data.OkPercent,
            "color" : "#9ACD32"
        }];
    $.plot($("#flot-requests-summary"), dataset, {
        series : {
            pie : {
                show : true,
                radius : 1,
                label : {
                    show : true,
                    radius : 3 / 4,
                    formatter : function(label, series) {
                        return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'
                            + label
                            + '<br/>'
                            + Math.round10(series.percent, -2)
                            + '%</div>';
                    },
                    background : {
                        opacity : 0.5,
                        color : '#000'
                    }
                }
            }
        },
        legend : {
            show : true
        }
    });

    // Creates APDEX table
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.0, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [0.0, 500, 1500, "GET Home"], "isController": false}, {"data": [0.0, 500, 1500, "POST Login"], "isController": false}, {"data": [0.0, 500, 1500, "GET Expenses"], "isController": false}, {"data": [0.0, 500, 1500, "POST Add Expense"], "isController": false}]}, function(index, item){
        switch(index){
            case 0:
                item = item.toFixed(3);
                break;
            case 1:
            case 2:
                item = formatDuration(item);
                break;
        }
        return item;
    }, [[0, 0]], 3);

    // Create statistics table
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 2000, 2000, 100.0, 2.554000000000002, 0, 944, 0.0, 1.0, 1.0, 7.990000000000009, 17.363221224801627, 18.88504652258087, 0.0], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["GET Home", 500, 500, 100.0, 0.22199999999999978, 0, 90, 0.0, 0.0, 0.0, 1.0, 4.358172008332825, 4.719934333243264, 0.0], "isController": false}, {"data": ["POST Login", 500, 500, 100.0, 5.976000000000004, 0, 944, 0.0, 1.0, 1.0, 144.8800000000001, 4.358665899541468, 4.746008279285876, 0.0], "isController": false}, {"data": ["GET Expenses", 500, 500, 100.0, 0.0559999999999999, 0, 7, 0.0, 0.0, 0.0, 1.990000000000009, 4.362240446693422, 4.762680487698482, 0.0], "isController": false}, {"data": ["POST Add Expense", 500, 500, 100.0, 3.9619999999999993, 0, 875, 0.0, 1.0, 2.0, 7.990000000000009, 4.345067913411486, 4.722715417604477, 0.0], "isController": false}]}, function(index, item){
        switch(index){
            // Errors pct
            case 3:
                item = item.toFixed(2) + '%';
                break;
            // Mean
            case 4:
            // Mean
            case 7:
            // Median
            case 8:
            // Percentile 1
            case 9:
            // Percentile 2
            case 10:
            // Percentile 3
            case 11:
            // Throughput
            case 12:
            // Kbytes/s
            case 13:
            // Sent Kbytes/s
                item = item.toFixed(2);
                break;
        }
        return item;
    }, [[0, 0]], 0, summaryTableHeader);

    // Create error table
    createTable($("#errorsTable"), {"supportsControllersDiscrimination": false, "titles": ["Type of error", "Number of errors", "% in errors", "% in all samples"], "items": [{"data": ["Non HTTP response code: org.apache.http.client.ClientProtocolException/Non HTTP response message: URI does not specify a valid host name: http:/expenses/", 500, 25.0, 25.0], "isController": false}, {"data": ["Non HTTP response code: org.apache.http.client.ClientProtocolException/Non HTTP response message: URI does not specify a valid host name: http:/", 500, 25.0, 25.0], "isController": false}, {"data": ["Non HTTP response code: org.apache.http.client.ClientProtocolException/Non HTTP response message: URI does not specify a valid host name: http:/add/", 500, 25.0, 25.0], "isController": false}, {"data": ["Non HTTP response code: org.apache.http.client.ClientProtocolException/Non HTTP response message: URI does not specify a valid host name: http:/login/", 500, 25.0, 25.0], "isController": false}]}, function(index, item){
        switch(index){
            case 2:
            case 3:
                item = item.toFixed(2) + '%';
                break;
        }
        return item;
    }, [[1, 1]]);

        // Create top5 errors by sampler
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 2000, 2000, "Non HTTP response code: org.apache.http.client.ClientProtocolException/Non HTTP response message: URI does not specify a valid host name: http:/expenses/", 500, "Non HTTP response code: org.apache.http.client.ClientProtocolException/Non HTTP response message: URI does not specify a valid host name: http:/", 500, "Non HTTP response code: org.apache.http.client.ClientProtocolException/Non HTTP response message: URI does not specify a valid host name: http:/add/", 500, "Non HTTP response code: org.apache.http.client.ClientProtocolException/Non HTTP response message: URI does not specify a valid host name: http:/login/", 500, "", ""], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": ["GET Home", 500, 500, "Non HTTP response code: org.apache.http.client.ClientProtocolException/Non HTTP response message: URI does not specify a valid host name: http:/", 500, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["POST Login", 500, 500, "Non HTTP response code: org.apache.http.client.ClientProtocolException/Non HTTP response message: URI does not specify a valid host name: http:/login/", 500, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["GET Expenses", 500, 500, "Non HTTP response code: org.apache.http.client.ClientProtocolException/Non HTTP response message: URI does not specify a valid host name: http:/expenses/", 500, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["POST Add Expense", 500, 500, "Non HTTP response code: org.apache.http.client.ClientProtocolException/Non HTTP response message: URI does not specify a valid host name: http:/add/", 500, "", "", "", "", "", "", "", ""], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
