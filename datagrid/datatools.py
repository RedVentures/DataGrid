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

from functools import partial
from itertools import ifilter, izip, starmap

def multi_sorted(data, sortcolumns, key=None):
    """
    Sort 2D dataset by given columns and key function

    Params:
        - data: 2-dimensional dataset to be sorted
        - sortcolumns: list of columns to be sorted (and their directions)
            direction is supplied as either 'asc' or 'desc' str values.
            example: (0, 'desc') would sort the set on the first column
            descending.
        - key: sort key func.

    Example:
    >>> data = [[1, 2, 3], [4, 5, 6]]
    >>> list(multi_sorted(data, [[0,'desc']]))
    [[4, 5, 6], [1, 2, 3]]
    """

    # Default key function if none is given
    if key is None: key = lambda column, data: data[column]

    # Apply sorted iterator for each given sort column/direction
    for column, direction in reversed(sortcolumns):
        data = sorted(data, key=partial(key, column))
        if direction == 'desc': data = reversed(data)

    # Return sorting iterator
    return data

def set_column_types(data, types):
    """
    Map types to columns on give data (generator) 

    Example:
    >>> i = set_column_types([['1','abc','0'],['4','b','1']],(float,str,int))
    >>> list(i)
    [(1.0, 'abc', 0), (4.0, 'b', 1)]
    """
    # by using an iterator, if we hit the except clause below, we should
    # output the same rows twice (assuming the exception is not hit on the
    # first row
    data = iter(data)

    for row in data:
        # apply type mapping to current row and yield
        try: yield tuple(starmap(lambda f,v: f(v), izip(types,row)))

        # we found a problem with the types mapping.
        # either we have the wrong number of args, or a column was
        # incorrectly mapped.  This will likely happen on every row,
        # so we should yield the remainder with no transformations
        except TypeError, ValueError:
            types = [str]*len(row)
            for row in data: yield row
            break

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
    >>> column_type(['1', '2', '3.0'])
    <type 'float'>
    >>> column_type(['1', '2.0.0', '3.0'])
    <type 'str'>
    >>> column_type(['1', '1a', '1b'])
    <type 'str'>
    """
    for x in filter(None, iter):
        # assume float, but wrap-up early if we find a string
        if type(x) == str and not (
                x.count('.') <= 1 and x.replace('.','').isdigit()):
            return str
    return float



