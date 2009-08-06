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

