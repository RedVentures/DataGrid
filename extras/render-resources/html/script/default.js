/*global window */
/*jslint white: true, browser: true, undef: true, nomen: true, eqeqeq: true, 
 * plusplus: true, bitwise: true, regexp: true, strict: true, newcap: true, 
 * immed: true */
"use strict";
var DataGrid = {
    
    init_hooks : [],

    init : function () {
        // Fetch all DataGrid instances to setup
        var tables = window.DataGrid.get_tables();

        // Initialize all found datagrids
        for (var i = 0; i < tables.length; i += 1) {
            if (!tables[i]) continue;   // Skip undefined
            window.DataGrid.init_table(tables[i]);

            // Fire all init hooks
            for (var j = 0; j < window.DataGrid.init_hooks.length; j += 1) {
                window.DataGrid.init_hooks[j](tables[i]);
            }
        }
    },

    init_table : function (table) {
        // Skip if table is invalid
        if (!table) { 
            return false;
        }

        // Init loading bit
        DataGrid_Meta[table.id]['_busy'] = false;

        // Make sure we have display columns listed
        if (typeof DataGrid_Config[table.id]['display'] == 'undefined'
                || DataGrid_Config[table.id].display.length == 0) {
            DataGrid_Config[table.id].display = DataGrid_Meta[table.id].allcolumns;
        }
        
        // No further processing is required for flat datasets
        if (typeof DataGrid_Config[table.id]['groupby'] == 'undefined'
                || DataGrid_Config[table.id]['groupby'].length == 0) {
            // Init group by for further functionality
            DataGrid_Config[table.id].groupby = [];
            return;
        }

        // Fetch all table body rows
        var rows = table.getElementsByTagName('tbody')[0]
            .getElementsByTagName('tr');
        
        // aggregate row refs to attach child row to
        var child_bucket = [];
        var current_level = 99;

        for (var i = 0; i < rows.length; i += 1) {
            // Get current row
            var row = rows[i];

            // Aggregation level of current row
            var aggregate_level = parseInt(row.className.substr(2), 10);
            
            // Have we changed aggregation levels?
            if (aggregate_level !== 0) {
                if (aggregate_level >= current_level) {
                    for (var j = aggregate_level; j >= current_level; j -= 1) {
                        child_bucket.pop();
                    }
                } 
                child_bucket.push(row);

                // Add child_rows array to row
                row.child_rows = [];
                row.child_rows_direct = [];
                row.children_expanded = true;
                row.aggregate_level = aggregate_level;

                // Set row indent
                row.childNodes[0].style
                    .paddingLeft = (((child_bucket.length - 1) * 2) + 1) + 'em';

                // Set row color
                if (row.style.backgroundColor == '') {
                    var bg = window.DataGrid.generate_background(child_bucket.length, table.id);
                    row.style.backgroundColor = bg;
                }

                // Set onclick handler
                window.DataGrid.register_event(row, 'click', window.DataGrid.toggle_row);

                // Update aggregation level pointer
                current_level = aggregate_level;
            }

            // Drop child rows in bucket (if one exists)
            for (var k = 0; k < child_bucket.length; k += 1) {
                if (child_bucket[k] !== row) {
                    child_bucket[k].child_rows.push(row);
                }
                if ((child_bucket[k].aggregate_level - 1) === aggregate_level) {
                    child_bucket[k].child_rows_direct.push(row);
                }
            }
        }
    },

    // Reload JS (send config back to alter display)
    reload_table : function(table, additional_params) {
        // Skip if busy
        if (DataGrid.is_busy(table)) return;

        DataGrid.mark_busy(table);
        
        if (window.XMLHttpRequest) {
            xhr = new XMLHttpRequest()
        } else {
            xhr = new ActiveXObject('Microsoft.XMLHTTP');
        }
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4) {
                // Create new node
                var newGridParent = document.createElement('div');

                // Check for expired reports
                if (xhr.responseText == 'expired') {
                    if (confirm("Report results have expired, click OK to reload report")) {
                        location = location;
                    }
                    return;
                }

                newGridParent.innerHTML = xhr.responseText;
                newGrid = newGridParent.getElementsByTagName('table')[0];

                // Replace old with new
                table.parentNode.replaceChild(newGrid, table);
                window.DataGrid.init();

                // Clear loading message
                DataGrid.mark_free(table);
            }
        }

        var req = '';
        if (typeof DataGrid.url === 'function') {
            req = DataGrid.url(table.id, DataGrid_Config[table.id], additional_params);
        } else if (typeof DataGrid.url === 'string') {
            req = DataGrid.url + 'id=' + table.id 
                + '&config=' + escape(JSON.stringify(DataGrid_Config[table.id]))
                + (additional_params ? '&' + additional_params : '');
        } else {
            throw 'DataGrid.url not defined!';
        }

        xhr.open('GET', req);
        xhr.send(null);
    },

    // Find and return all datagrid tables
    get_tables : function () {
        // Fetch all tables and examine classes
        var tables = document.getElementsByTagName('table');

        // Find ids for datagrid instances
        var result = [];
        for (var i = 0; i < tables.length; i += 1) {
            if (tables[i].className === 'datagrid') {
                result[tables.length] = tables[i];
            }
        }

        return result;
    },

    // Generate aggregate row background color
    generate_background : function (level, id) {
        if (typeof DataGrid.baseColor !== 'undefined') {
            var span = Math.max.apply(Math, DataGrid.baseColor) - Math.min.apply(Math, DataGrid.baseColor);
            var interval = span / (DataGrid_Config[id]['groupby'].length + 1);
            var r = parseInt(DataGrid.baseColor[0], 10) + (level * interval);
            var g = parseInt(DataGrid.baseColor[1], 10) + (level * interval);
            var b = parseInt(DataGrid.baseColor[2], 10) + (level * interval);
        } else {
            var interval = 100 / (DataGrid_Config[id]['groupby'].length + 0);
            var r = 100 + (level * interval);
            var g = 100 + (level * interval);
            var b = 100 + (level * interval);
        }
        return "rgb(" + r + ", " + g + ", " + b + ")";
    },

    // Set display style property on given rows
    set_row_display : function (rows, display) {
        for (var i = 0; i < rows.length; i += 1) {
            rows[i].style.display = display;
        }
    },

    // Show/Hide decendant rows
    toggle_row : function (e) {
        // Get source element
        var evnt = e || window.event;
        var row = evnt.currentTarget || evnt.srcElement.parentNode;
        
        // toggle rows in bucket
        if (row.children_expanded) {
            window.DataGrid.set_row_display(row.child_rows, 'none');
        } else {
            window.DataGrid.set_row_display(row.child_rows_direct, '');
        }

        // Toggle expanded bit
        row.children_expanded = !row.children_expanded;
    },

    // Register event to fire on each datagrid everytime init is called
    register_init : function (method) {
        window.DataGrid.init_hooks[window.DataGrid.init_hooks.length] = method;
    },

    // Universal event binder
    register_event : function (elem, evnt, fun) {
        if (elem.addEventListener) {
            elem.addEventListener(evnt, fun, false);
        } else if (elem.attachEvent) {
            elem.attachEvent('on' + evnt, fun);
        }
    },

    // Mark table as busy
    mark_busy : function (table) {
        DataGrid_Meta[table.id]['_busy'] = true;

        var tablePos = window.DataGrid.get_position(table);
        loadingBlock = document.createElement('div');
        loadingBlock.style.margin = '2em';
        loadingBlock.style.background = '#aca';
        loadingBlock.style.padding = '.5em 2em';
        loadingBlock.style.border = '2px solid #8a8';
        loadingBlock.style.position = 'absolute';
        loadingBlock.style.left = tablePos[0] + 'px';
        loadingBlock.style.top = tablePos[1] + 'px';
        loadingBlock.style.zIndex = 1000;
        loadingBlock.innerHTML = 'Loading.  Please wait...';

        // Store ref so we can remove when finished
        DataGrid_Meta[table.id]['_busyBlock'] = loadingBlock;
        
        // Display loading message
        document.body.appendChild(loadingBlock);
    },

    // Mark table as free
    mark_free : function (table) {
        DataGrid_Meta[table.id]['_busy'] = false;
        document.body.removeChild(DataGrid_Meta[table.id]['_busyBlock']);
    },

    // Check if table is busy
    is_busy : function (table) {
        return DataGrid_Meta[table.id]['_busy'];
    },

    // Get arbitrary elem position
    get_position : function(elem) {
        var curleft = curtop = 0;
        if (elem.offsetParent) {
            do {
                curleft += elem.offsetLeft;
                curtop += elem.offsetTop;
            } while (elem = elem.offsetParent);
        }
        return [curleft, curtop];
    }

};

// Add sorting
window.DataGrid.register_init(function (grid) {

    // Fetch existing sort order
    var sort_order = DataGrid_Config[grid.id]['sortby'] || [];

    // Fetch the theads for the grid
    var theads = grid.getElementsByTagName('th');

    // Set classes for sorted columns
    for (var i = 0; i < sort_order.length; i += 1) {
        for (var j = 0; j < theads.length; j += 1) {
            if (theads[j].innerHTML == sort_order[i][0]) {
                theads[j].className = 'sorted_' + sort_order[i][1];
            }
        }
    }

    // Set onclick event
    for (i = 0; i < theads.length; i += 1) {
        // Skip the empty thead
        if (theads[i].innerHTML == "") continue;

        // Set the cursor style so the user knows they can click
        theads[i].style.cursor = 'pointer';

        // Attach the on click event
        DataGrid.register_event(theads[i], 'click', function (e) {
            var e = e || window.event;
            if (e.shiftKey) {
                var found = false;
                for (j = 0; j < sort_order.length; j += 1) {
                    if (sort_order[j][0] == this.innerHTML) {
                        sort_order[j][1] = (sort_order[j][1] == 'asc' ? 'desc' : 'asc');
                        found = true;
                    }
                }
                if (!found) {
                    sort_order[sort_order.length] = [this.innerHTML, 'asc'];
                }
            } else {
                var found = false;
                for (j = 0; j < sort_order.length; j += 1) {
                    if (sort_order[j][0] == this.innerHTML) {
                        found = (sort_order[j][1] == 'asc' ? 'desc' : 'asc');
                    }
                }
                sort_order = [[this.innerHTML,(found || 'asc')]];
            }

            DataGrid_Config[grid.id]['sortby'] = sort_order;
            DataGrid.reload_table(grid);
        });
    }
});

// Setup after page loads
DataGrid.register_event(window, 'load', DataGrid.init);

/* vim: set ft=javascript ts=4 sw=4 et */
