#!/bin/env python
#------------------------------------------------------------------------#
# DataGrid - Tabular Data Rendering Library
# Copyright (C) 2009-2010 Adam Wagner <awagner@redventures.com>
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

"""DataGrid setup-tools"""

import sys
from distutils.core import setup
from datagrid.distutils import phpdir
from datagrid import about

# Executables and bindings list
data_files = [('bin', ['rendergrid'])]

# if we are installing, do checks for extras installation
if len(sys.argv) > 1 and sys.argv[1] == 'install':
    # Check for existance of php and find share dir
    print "Checking for PHP: ",
    dir = phpdir()
    if dir:
        print "found, Installing PHP bindings in", dir
        data_files.append((phpdir(), ['extras/bindings/datagrid.php']))
    else:
        print "not found, skipping install of php bindings"

# Dispatch distutils setup magic
setup(
        name = about.NAME,
        version = about.VERSION,
        packages = ['datagrid', 'datagrid.renderer'],
        data_files = data_files
     )

