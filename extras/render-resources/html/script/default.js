
DataGrid = {
    
    init: function() {
        // Fetch all DataGrid instances to setup
        tables = DataGrid.get_tables();

        // Initialize all found datagrids
        for (var i = 0; i < tables.length; i++) {
            DataGrid.init_table(tables[i]);
        }
    },

    init_table: function(table) {
        // Skip if table is invalid
        if (!table) return false;

        // Fetch all table body rows
        rows = table.getElementsByTagName('tbody')[0]
            .getElementsByTagName('tr');
        
        // aggregate row refs to attach child row to
        child_bucket = [];
        current_level = 99;

        for (var i = 0; i < rows.length; i++) {
            // Aggregation level of current row
            aggregate_level = parseInt(rows[i].className.substr(2));
            
            // Have we changed aggregation levels?
            if (aggregate_level != 0) {
                if (aggregate_level >= current_level) {
                    for (var j = aggregate_level; j >= current_level; j--) 
                        child_bucket.pop();
                } 
                child_bucket.push(rows[i]);

                // Add child_rows array to row
                rows[i].child_rows = [];
                rows[i].child_rows_direct = [];
                rows[i].children_expanded = true;
                rows[i].aggregate_level = aggregate_level;

                // Set row indent
                rows[i].childNodes[0].style.paddingLeft 
                    = (((child_bucket.length - 1) * 2) + 1) + 'em';

                // Set row color
                shade = 100 + (child_bucket.length * 25);
                rows[i].style.backgroundColor = "rgb(" + shade + ", " + shade + ", " + shade + ")";

                // Set onclick handler
                row = rows[i];
                rows[i].addEventListener('click', 
                    function(e) {

                        // Get source element
                        if( !e ) e = window.event;
                        var row = e.currentTarget || e.srcElement;
                        
                        // toggle rows in bucket
                        if (row.children_expanded) {
                            for (var i = 1; i < row.child_rows.length; i++) {
                                row.child_rows[i].style.display = 'none';
                            }
                        } else {
                            for (var i = 0; i < row.child_rows_direct.length; i++) {
                                row.child_rows_direct[i].style.display = '';
                            }
                        }

                        // Toggle expanded bit
                        row.children_expanded = !row.children_expanded;

                    }, false);

                // Update aggregation level pointer
                current_level = aggregate_level;
            }

            // Drop child rows in bucket (if one exists)
            for (var j = 0; j < child_bucket.length; j++) {
                child_bucket[j].child_rows.push(rows[i]);
                if ((child_bucket[j].aggregate_level - 1) == aggregate_level) {
                    child_bucket[j].child_rows_direct.push(rows[i]);
                }
            }
        }
    },

    get_tables: function() {
        // Fetch all tables and examine classes
        tables = document.getElementsByTagName('table');

        // Find ids for datagrid instances
        var result = new Array();
        for (var i = 0; i < tables.length; i++) {
            if (tables[i].className == 'datagrid') {
                result[tables.length] = tables[i];
            }
        }

        return result;
    }

}

// Start after page loads
if (window.addEventListener)
    window.addEventListener('load', DataGrid.init, false);
else if (window.attachEvent)
    window.attachEvent('onload', DataGrid.init);

