/*global window */
/*jslint white: true, browser: true, undef: true, nomen: true, eqeqeq: true, 
 * plusplus: true, bitwise: true, regexp: true, strict: true, newcap: true, 
 * immed: true */
"use strict";
// Define foldl
var foldl = function (arr, fun) {
    for (var i = 0; i < arr.length; i += 1) {
        fun(arr[i]);
    }
};

// Fetch next element
var next = function (elem) {
    do {
        elem = elem.nextSibling;
    } while (elem && elem.nodeType !== 1);
    return elem;
};

var DataGrid = {
    
    init_hooks : {},

    init : function () {
        // Fetch all DataGrid instances to setup
        var tables = window.DataGrid.get_tables();

        // Initialize all found datagrids
        for (var i = 0; i < tables.length; i += 1) {
            if (!tables[i]) continue;   // Skip undefined
            window.DataGrid.init_table(tables[i]);

            // Fire all init hooks
            for (var j in window.DataGrid.init_hooks) {
                if (window.DataGrid.init_hooks.hasOwnProperty(j)) {
                    window.DataGrid.init_hooks[j](tables[i]);
                }
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
                if (row.childNodes[0].nodeType === 1) {
                    row.childNodes[0].style
                        .paddingLeft = (((child_bucket.length - 1) * 2) + 1) + 'em';
                }

                // Set row color
                if (row.style.backgroundColor == '') {
                    var bg = window.DataGrid.generate_background(child_bucket.length, table.id);
                    row.style.backgroundColor = bg;
                }

                // Set onclick handler
                window.DataGrid.register_event(row, 'click', window.DataGrid.toggle_row);
                row.style.cursor = 'pointer';

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

    // Default baseColors
    baseColors : [[100,100,100],[255,255,255]],

    // Generate aggregate row background color
    generate_background : function (level, id) {
        var calcColors = function (idx) {
            var max = Math.max(DataGrid.baseColors[0][idx], DataGrid.baseColors[1][idx]);
            var min = Math.min(DataGrid.baseColors[0][idx], DataGrid.baseColors[1][idx]);
            var interval = (max - min) / (DataGrid_Config[id]['groupby'].length + 1);
            if (DataGrid.baseColors[0][idx] > DataGrid.baseColors[1][idx]) interval *= -1;
            return parseInt(DataGrid.baseColors[0][idx] + (level * interval), 10);
        };

        var r = calcColors(0);
        var g = calcColors(1);
        var b = calcColors(2);
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
    register_init : function (method, name) {
        var slot = name || (function () {
            var i = 0;
            while (window.DataGrid.init_hooks.hasOwnProperty(i)) i += 1;
            return i;
        })();
        window.DataGrid.init_hooks[slot] = method;
    },

    // Fetch the named event
    fetch_init : function (name) {
        return window.DataGrid.init_hooks[name];
    },

    // Remove a registered event
    unregister_init : function (name) {
        delete window.DataGrid.init_hooks[name];
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
        loadingBlock.style.background = DataGrid.generate_background(DataGrid_Config[table.id]['groupby'].length, table.id);
        loadingBlock.style.padding = '.5em 2em';
        loadingBlock.style.border = '2px solid ' + DataGrid.generate_background(0, table.id);
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
        theads[i].onclick = function (e) {
            var e = e || window.event;
            var theHTML = this.innerHTML.replace(/(<([^>]+)>)/ig,'');
            if (e.shiftKey || e.ctrlKey) {
                var found = false;
                for (j = 0; j < sort_order.length; j += 1) {
                    if (sort_order[j][0] == theHTML) {
                        if (sort_order[j][1] == 'desc') {
                            sort_order.splice(j,1);
                        } else {
                            sort_order[j][1] = (sort_order[j][1] == 'asc' ? 'desc' : 'asc');
                        }
                        found = true;
                    }
                }
                if (!found) {
                    sort_order[sort_order.length] = [theHTML, 'asc'];
                }
            } else {
                var found = false;
                for (j = 0; j < sort_order.length; j += 1) {
                    if (sort_order[j][0] == theHTML) {
                        if (sort_order[j][1] == 'desc') {
                            found = 'delete'
                        } else {
                            found = (sort_order[j][1] == 'asc' ? 'desc' : 'asc');
                        }
                    }
                }
                if (found == 'delete') {
                    sort_order = [];
                } else {
                    sort_order = [[theHTML,(found || 'asc')]];
                }
            }

            DataGrid_Config[grid.id]['sortby'] = sort_order;
            DataGrid.reload_table(grid);
        };
    }
}, 'sorting');

// Add Controls
window.DataGrid.register_init(function (grid) {

    // Return if we have nothing to do
    if (typeof DataGrid_Controls !== 'object') return false;

    // Create the controls node
    var controls = document.getElementById(grid.id + 'Controls') || document.createElement('fieldset');
    controls.id = grid.id + 'Controls';
    controls.className = 'datagridControls';
    controls.innerHTML = '<legend>+ Show Controls</legend>';

    // Insert into the DOM
    if (!document.getElementById(grid.id + 'Controls')) {
        grid.parentNode.insertBefore(controls, grid);
    }

    // Inistantiate all of the controls
    for (control in DataGrid_Controls) {
        if (DataGrid_Controls.hasOwnProperty(control)) {
            var ctl_props = DataGrid_Controls[control];
            var wrapper = document.createElement('div');
            wrapper.className = "datagridControl";
            wrapper.style.display = "none";
            var ctl = document.createElement(ctl_props.type);
            ctl.innerHTML = ctl_props.html
            ctl_props.prepare.call(ctl, grid);
            wrapper.appendChild(ctl);
            controls.insertBefore(wrapper, next(controls.lastChild));
        }
    }

    // Attach the onclick to the controls
    controls.getElementsByTagName('legend')[0].onclick = function () {
        curr = next(this);
        while (curr != null && curr != next(curr)) {
            curr.style.display =  (curr.style.display == 'none') ? '' : 'none';
            curr = next(curr);
        }
        this.innerHTML =  (next(this).style.display != 'none') ? '- Hide Controls' : '+ Show Controls';
    };
}, 'controls');

// Setup after page loads
DataGrid.register_event(window, 'load', DataGrid.init);

/* vim: set ft=javascript ts=4 sw=4 et */
