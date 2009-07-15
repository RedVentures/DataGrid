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
     * @var string[]
     */
    public $flags = array();


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
        $grid->flags['--autocolumn'] = $includesHeader;

        // Return new datagrid
        return $grid;

    }

    
    /* -- Public Methods -- */

    /**
     * Render datagrid
     * 
     * @return string
     */
    public function render() {

        // Run shell command
        $returnCode = null;     // Unix exit status

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

        $flags = implode( ' ', array_keys( array_filter($this->flags) ) );

        return self::$executable . " $flags {$this->dataFile}";

    }

}

