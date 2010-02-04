<?php

#------------------------------------------------------------------------#
# DataGrid - Tabular Data Rendering Library
# Copyright (C) 2009-2010 Adam Wagner <awagner@redventures.com>
#                    Kenny Parnell <kparnell@redventures.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published 
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------#

/**
 * PHP Bindings to Python DataGrid module
 * 
 * @author Adam Wagner <awagner@redventures.com>
 */

/**
 * DataGrid Exception
 */
class DataGrid_Exception extends Exception {}

/**
 * Main DataGrid Class
 */
class DataGrid {

    /* -- Class Constants -- */

    const DEFAULT_RENDERER = 'datagrid.renderer.html';

    const OPT_GROUPBY = 'groupby';
    const OPT_AGGREGATE ='aggregate';
    const OPT_AUTOCOLUMN = 'autocolumn';
    const OPT_CALCULATE = 'calculate';
    const OPT_DESCRIPTION = 'columndescription';
    const OPT_DISPLAY = 'display';
    const OPT_FORMAT = 'format';
    const OPT_RENDERER = 'renderer';
    const OPT_RENDEREROPTION = 'rendereroption';
    const OPT_SORT = 'sort';
    const OPT_SUPPRESSDETAIL = 'suppressdetail';


    /* -- Public Static Properties -- */

    /**
     * DataGrid executable
     *
     * If custom path to executable is required, add it here
     *
     * @var string
     */
    public static $executable = 'rendergrid';


    /* -- Public Properties -- */

    /**
     * Data file to feed into datagrid executable
     */
    public $dataFile = null;

    /**
     * Associative array of flags to pass on command-line
     *
     * Format:
     *      # boolean options
     *          KEY => TRUE                  // becomes: --KEY
     *      # key/val option
     *          KEY => VAL                   // becomes: --KEY="VAL"
     *      # key/val option with multiple values
     *          KEY => array(V1, V2)         // becomes: --KEY="V1" --KEY="V2"
     *
     * Run 'rendergrid --help' for documentation and list of command-line args
     *
     * @var string[]
     */
    public $flags = array();


    /* -- Public Static Methods -- */

    /**
     * Instantiate new DataGrid object for rendering passed in data
     *
     * @param array|Traversable $data
     * @param array $flags - Optional flags configuring datagrid instance
     */
    public static function create( $data, array $flags = array(), 
            $tmpDir = '/tmp' ) {
        
        // Open tempfile and write new csv file
        $fileName = tempnam( $tmpDir, 'datagrid' );
        $fp = fopen( $fileName, 'w' );

        // We cannot always consume any entire array into memory, so always
        // use iterators for simplicity
        if ( is_array( $data ) )
            $data = new ArrayIterator( $data );

        // Generate cvs file
        try {
            // Write header record
            fputcsv( $fp, array_keys( (array) current( $data ) ) );

            // Write body of datafile
            foreach ( $data as $record ) {
                // convert objects to string 'object' (for php 5.2)
                $record = (array) $record;
                foreach ( $record as $key => $value ) {
                    if ( is_object( $value ) ) $record[$key] = 'object';
                } 

                // write to csv
                fputcsv( $fp, $record );
            }
        } catch ( DataGrid_Exception $e ) {
            // Cleanup created file
            fclose( $fp );
            unlink( $fileName ); 

            // Pass exception on
            throw $e;
        }

        // Close pointer
        fclose( $fp );

        // Continue with createFromFile
        return self::createFromFile( $fileName, true, $flags );

    }

    /**
     * Instantiate new DataGrid object for rendering given file
     *
     * @param string $dataFile
     * @param bool $includesHeader
     * @param array $flags - Optional flags configuring datagrid instance
     * @return DataGrid
     */
    public static function createFromFile( $dataFile, $includesHeader = false, 
            array $flags = array() ) {

        // Setup for direct file render
        $grid = new self;
        $grid->dataFile = $dataFile;
        $grid->flags[self::OPT_AUTOCOLUMN] = $includesHeader;

        // Return new datagrid
        return $grid;

    }

    
    /* -- Public Methods -- */

    /**
     * Setup new datagrid instance
     *
     * @param string $flags
     */
    public function __construct( array $flags = array() ) {

        // Set option defaults
        $defaultFlags[self::OPT_RENDERER] = self::DEFAULT_RENDERER;

        // Merge default with given flags
        $this->flags = array_merge( $defaultFlags, $flags );

    }

    /**
     * Add formula-driven column
     *
     * @param string $columnName - Name of new column
     * @param string $formula - How to get the data we are seeking
     * @return DataGrid
     */
    public function addCalculatedColumn( $columnName, $formula ) {

        // set method for each given column
        $this->_appendFlagValue( self::OPT_CALCULATE, 
            "$columnName|$formula", $columnName );

        return $this;

    }

    /**
     * Add column description
     *
     * @param string $columnName - Name of column
     * @param string $description - What the column's all about
     * @return DataGrid
     */
    public function addColumnDescription( $columnName, $description ) {

        $this->_appendFlagValue( self::OPT_DESCRIPTION, 
            "$columnName|$description", $columnName );

        return $this;

    }

    /**
     * Set columns to grou data on
     *
     * @param array $groupby - list of columns to group on
     * @return DataGrid
     */
    public function groupby( array $groupby ) {

        $this->flags[self::OPT_GROUPBY] = $groupby;
        return $this;
        
    }

    /**
     * Render datagrid
     * 
     * @return string
     */
    public function render() {

        $command = $this->_buildShellCmd();
        $returnCode = null;     // Unix exit status

        // Run shell command
        ob_start();
        passthru( $command, $returnCode );
        $output = ob_get_contents();
        ob_end_clean();

        // Check for errors
        if ( $returnCode ) {
            $errorMessage = 
                "<div style='font-weight: bold'>Command:</div>
                 <div style='margin: 1em;'>$command</div>
                 <div style='font-weight: bold'>Failed with the following output:</div>
                 <pre>$output</pre>";

            $e = new DataGrid_Exception($errorMessage);
            throw $e;
        }

        // Append JS Config Object
        $output .= $this->_jsonConfig();

        // Output rendered datagrid
        return $output;

    }

    /**
     * Set aggregation method for the given column list
     *
     * @param array $columnList - columns to set aggregate method on
     * @param string $method - example: 'sum', 'count', avg', etc...
     * @return DataGrid 
     */
    public function setAggregationMethod( array $columnList, $method ) {

        // set method for each given column
        foreach ( $columnList as $col )
            $this->_appendFlagValue( self::OPT_AGGREGATE, 
                "$col|$method", $col );

        return $this;

    }

    /**
     * Set formatting to be used when rendering a column
     *
     * Formatting is determined by the formatting chain requested here.
     * Available formatters include 'percent' and 'number'.
     *
     * Example DataSet:
     *      ColA    ColB    ColC
     *      13213   2       3
     *      4       0.95    1232
     *  
     * Example:
     *      $g->setColumnFormatting('ColA', 'number');
     *
     *      would produce the following values for ColA:
     *      13,213 and 4
     *
     *      $g->setColumnFormatting('ColB', 'percent');
     *
     *      would produce the following values for ColB:
     *      200% and 95%
     *
     * @param string $column - Name of column to set formatting for
     * @param string $method1 - Formatting method to use
     * @param string $method2 - (optional) Second formatting method
     * @param string $methodN - (optional) Etc.
     *
     * @return DataGrid
     */
    public function setColumnFormatting() {

        // get options since we have declare none
        $args = func_get_args();
        $column = array_shift($args);

        $this->_appendFlagValue( self::OPT_FORMAT, 
            "$column|" . implode('|', $args), $column );

        return $this;

    }

    /**
     * Set list of columns to display
     *
     * If this optional call is not made, all data columns will be rendered
     *
     * @param array $columnList - columns to display
     * @return DataGrid
     */
    public function setDisplayColumns( array $columnList ) {

        // set columns list
        $this->flags[self::OPT_DISPLAY] = $columnList;

        return $this;

    }

    /**
     * Set renderer configuration option
     * 
     * Example (set html class of datagrid with HTML renderer):
     *      $grid->setRendererOption( 'html_class', 'myDataGridClass' );
     *
     * @param string $key
     * @param string $value
     * @return DataGrid
     */
    public function setRendererOption( $key, $value ) {

        // make sure we already have an array
        $this->_appendFlagValue( self::OPT_RENDEREROPTION, 
            "$key|$value", $key );

        return $this;

    }

    /**
     * Set sort parameters
     *
     * Accepts an array of column names indicating the sort order.
     * Changing the sort order is achieved by passing appending "|" and the
     * direction to the end of the column name.  ie: "FirstName|desc".
     * If not direction is specified, ascending is assumed.
     *
     * Here is a full example of how to sort by LastName, then FirstName
     * descending:
     *      $grid->sortBy( array( 'LastName', 'FirstName|desc' ) );
     *
     * @param string $columnList
     * @return DataGrid
     */
    public function sortBy( array $columnList ) {

        // set method for each given column
        $this->flags[self::OPT_SORT] = $columnList;
        return $this;

    }

    /**
     * Suppress detail rows from report
     *
     * @return DataGrid
     */
    public function suppressDetail() {

        $this->flags[self::OPT_SUPPRESSDETAIL] = true;
        return $this;

    }

    
    /* -- Private Methods -- */

    /**
     * Append value to array-style flag
     *
     * @param string $flag
     * @param string $value
     * @param string $key (unique key for value)
     */
    private function _appendFlagValue( $flag, $value, $key = '' ) {

        // make sure we already have an array
        if ( empty( $this->flags[$flag] )
                || !is_array( $this->flags[$flag] ) ) {
            $this->flags[$flag] = array();
        }

        // Append/Replace value
        if ( empty( $key ) ) {
            $this->flags[$flag][] = $value;
        } else {
            $this->flags[$flag][$key] = $value;
        }

    }

    /**
     * Build shell-exec string
     *
     * @return string
     */
    private function _buildShellCmd() {

        // Filter unused boolean flags
        $flags = array_filter($this->flags);
        
        // Transform into option string
        $flagString = '';
        foreach ( $flags as $key => $val ) {
            if ( $val === true ) {              // Single boolean option
                $flagString .= " --$key";
            } elseif ( is_string( $val ) ) {    // Single Key/Val option
                $flagString .= " --$key='" . addslashes( $val ) . "'";
            } elseif ( is_array( $val ) || is_object( $val ) ) {     // List of Key/Val options
                foreach ( $val as $v ) 
                    $flagString .= " --$key='" . addslashes( $v ) . "'";
            }
        }

        // Glue the pieces together
        return self::$executable . " $flagString {$this->dataFile} 2>&1";

    }

    /**
     * JSON version of currently selected configs
     *
     * @return string (json)
     */
    private function _jsonConfig() {
        list($tmp, $id) = explode('|', $this->_getValue(self::OPT_RENDEREROPTION, 'html_id'));

        return "<script type='text/javascript'>
            if (typeof DataGrid_Config == 'undefined') DataGrid_Config = {};
            DataGrid_Config['$id'] = " 
            . json_encode($this->flags) . "</script>";
    }

    /**
     * Get flag value at optional key position
     *
     * @param string $flag
     * @param string $key
     * @return mixed
     */
    private function _getValue($flag, $key=null) {
        $node = $this->flags[$flag];
        if (is_object($node)) {
            return $node->$key;
        } else {
            return $node[$key];
        }
    }

}

