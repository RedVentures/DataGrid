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

from itertools import ifilter, izip, starmap

def set_column_types(iter, types):
    """
    Cast each col in row as requested type

    Example:
    >>> i = set_column_types([['1','2'],['4','5']],(float,str))
    >>> list(i)
    [(1.0, '2'), (4.0, '5')]
    """
    # put types in single item lists, so we can use apply
    return (tuple(starmap(apply, izip(types,row))) for row in iter)

def get_column_types(iter):
    """
    Determine column types from content in each column

    Example:
    >>> get_column_types([[1,'2',3,'a'],[2,'3','z','b']])
    [<type 'float'>, <type 'float'>, <type 'str'>, <type 'str'>]
    """
    return [column_type(col) for col in zip(*iter)]

def column_type(iter):
    """
    Guess column type from data-therin (ie: str or float)

    Example:
    >>> column_type([1,2,3])
    <type 'float'>
    >>> column_type(['a','b','c'])
    <type 'str'>
    >>> column_type(['1', '2', '3'])
    <type 'float'>
    >>> column_type(['1', '1a', '1b'])
    <type 'str'>
    """
    for x in filter(None, iter):
        # assume float, but wrap-up early if we find a string
        if type(x) == str and not x.isdigit(): return str
    return float


