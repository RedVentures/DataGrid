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
 * PHP Bindings Example Usage
 *
 * @author Adam Wagner <awagner@redventures.com>
 */

require 'datagrid.php';

// point to datagrid executable
//      (this step is not required if datagrid has been installed)
DataGrid::$executable = '../../rendergrid';

// create some fake data
$data = array(
    array( 'FirstName' => 'Bob',  'LastName' => 'Smith', 'Age' => '32'), 
    array( 'FirstName' => 'Fred', 'LastName' => 'Smith', 'Age' => '25'), 
    array( 'FirstName' => 'John', 'LastName' => 'Doe',   'Age' => '53')
);

// create new instance and set some configurations
$grid = DataGrid::create($data);
$grid->aggregate( array( 'LastName' ) );
$grid->setAggregationMethod( array( 'Age' ), 'avg' );
$grid->addCalculatedColumn( 'TwiceAge', '{Age}*2' );
$grid->addColumnDescription( 'Age', 'How many years since birth' );

// output rendered grid
print $grid->render();

