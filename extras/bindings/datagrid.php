<?php

#------------------------------------------------------------------------#
# DataGrid - Tabular Data Rendering Library
# Copyright (C) 2009 Adam Wagner <awagner@redventures.com>
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
 * PHP DataGrid Bindings
 * 
 * @author Adam Wagner <awagner@redventures.net>
 */

class DataGrid {

    /* -- Class Constants -- */

    const OPT_AGGREGATE = 'aggregate';
    const OPT_AUTOCOLUMN = 'autocolumn';
    const OPT_RENDERER = 'renderer';


    /* -- Public Static Properties -- */

    /**
     * DataGrid executable
     *
     * If custom path is required, add it here
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
     *          KEY                               // becomes: --KEY
     *      # key/val option
     *          KEY => VAL                        // becomes: --KEY="VAL"
     *      # key/val option with multiple values
     *          KEY => array(V1, V2)              // becomes: --KEY="V1" --KEY="V2"
     *
     * Run 'rendergrid --help' for documentation and list of command-line args
     *
     * @var string[]
     */
    public $flags = array();

    /**
     * Renderer sys used to generate output
     * 
     * Possible Values: datagrid.html, datagrid.ascii (or any custom python module)
     *
     * @var string
     */
    public $renderer = 'datagrid.html';


    /* -- Public Static Methods -- */

    /**
     * Instantiate new DataGrid setup for rendering given file
     *
     * @param string $dataFile
     * @param bool $includesHeader
     * @return DataGrid
     */
    public static function createFromFile( $dataFile, $includesHeader = false ) {

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
        $defaultFlags[self::OPT_RENDERER] = 'datagrid.html';

        // Merge default with given flags
        $this->flags = array_merge( $defaultFlags, $flags );

    }

    /**
     * Set columns to aggregate data on
     *
     * @param array $aggregate - list of columns to aggregate on
     * @return DataGrid
     */
    public function aggregate( array $aggregate ) {

        $this->flags[self::OPT_AGGREGATE] = $aggregate;
        return $self;
        
    }

    /**
     * Render datagrid
     * 
     * @return string
     */
    public function render() {

        $returnCode = null;     // Unix exit status

        // Run shell command
        ob_start();
        passthru( $this->_buildShellCmd(), $returnCode );
        $output = ob_get_contents();
        ob_end_clean();

        // Output rendered datagrid
        return $output;

    }

    
    /* -- Private Methods -- */

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
            } elseif ( is_array( $val ) ) {     // List of Key/Val options
                foreach ( $val as $v ) 
                    $flagString .= " --$key='" . addslashes( $v ) . "'";
            }
        }

        // Glue the pieces together
        return self::$executable . " $flagString {$this->dataFile}";

    }

}

