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

"""Tools for handling aggregation options"""

import __builtin__

import datagrid.aggregate

def parse_options(aggregation):
    """Parse string aggregation options and return a format suitable for
    datagrid.core
    
    Example:
    >>> aggregation = parse_options(['colA|count', 'colB|max'])
    >>> aggregation['colA'].func_name
    'count'
    >>> aggregation['colB'].__doc__[:3]
    'max'
    """
    # Create dictionary from simple list of strings,
    aggregation = dict(a.split('|') for a in aggregation)

    # Replace string aggregation requests from dictionary with function
    # from datagrid.aggregate module
    if aggregation:
        for key, method_name in aggregation.iteritems():
            # Look for method from aggregate first and __builtin__ second
            try:
                method = vars(datagrid.aggregate)[method_name]
            except KeyError:
                method = vars(__builtin__)[method_name]
            aggregation[key] = method

    return aggregation

