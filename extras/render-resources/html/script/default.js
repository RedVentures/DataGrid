
var DataGrid = {
    
    init: function() {
        // Fetch all DataGrid instances to setup
        var tables = window.DataGrid.get_tables();

        // Initialize all found datagrids
        for (var i = 0; i < tables.length; i++) {
            window.DataGrid.init_table(tables[i]);
        }
    },

    init_table: function(table) {
        // Skip if table is invalid
        if (!table) { 
            return false;
        }

        // Fetch all table body rows
        var rows = table.getElementsByTagName('tbody')[0]
            .getElementsByTagName('tr');
        
        // aggregate row refs to attach child row to
        var child_bucket = [];
        var current_level = 99;

        for (var i = 0; i < rows.length; i++) {
            // Get current row
            var row = rows[i];

            // Aggregation level of current row
            var aggregate_level = parseInt(row.className.substr(2), 10);
            
            // Have we changed aggregation levels?
            if (aggregate_level !== 0) {
                if (aggregate_level >= current_level) {
                    for (var j = aggregate_level; j >= current_level; j--) {
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
                var bg = window.DataGrid.generate_background(child_bucket.length);
                row.style.backgroundColor = bg;

                // Set onclick handler
                window.DataGrid.register_event(row, 'click', window.DataGrid.toggle_row);

                // Update aggregation level pointer
                current_level = aggregate_level;
            }

            // Drop child rows in bucket (if one exists)
            for (var k = 0; k < child_bucket.length; k++) {
                if (child_bucket[k] != row) {
                    child_bucket[k].child_rows.push(row);
                }
                if ((child_bucket[k].aggregate_level - 1) == aggregate_level) {
                    child_bucket[k].child_rows_direct.push(row);
                }
            }
        }
    },

    // Find and return all datagrid tables
    get_tables: function() {
        // Fetch all tables and examine classes
        var tables = document.getElementsByTagName('table');

        // Find ids for datagrid instances
        var result = [];
        for (var i = 0; i < tables.length; i++) {
            if (tables[i].className == 'datagrid') {
                result[tables.length] = tables[i];
            }
        }

        return result;
    },

    // Generate aggregate row background color
    generate_background: function(level) {
        var shade = 100 + (level * 25);
        return "rgb(" + shade + ", " + shade + ", " + shade + ")";
    },

    // Set display style property on given rows
    set_row_display: function(rows, display) {
        for (var i = 0; i < rows.length; i++ ) {
            rows[i].style.display = display;
        }
    },

    // Show/Hide decendant rows
    toggle_row: function(e) {
        // Get source element
        var evnt = e || window.event;
        var row = evnt.currentTarget || evnt.srcElement;
        
        // toggle rows in bucket
        if (row.children_expanded) {
            window.DataGrid.set_row_display(row.child_rows, 'none');
        } else {
            window.DataGrid.set_row_display(row.child_rows_direct, '');
        }

        // Toggle expanded bit
        row.children_expanded = !row.children_expanded;
    },

    // Universal event binder
    register_event: function(elem, evnt, fun) {
        if (elem.addEventListener) {
            elem.addEventListener(evnt, fun, false);
        } else if (elem.attachEvent) {
            elem.attachEvent('on' + evnt, fun);
        }
    }

};

// Setup after page loads
DataGrid.register_event(window, 'load', DataGrid.init);

