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

"""Aggregate Method Library"""

import __builtin__
from operator import countOf

def count(values): 
    """
    Count Unique Values
    
    Example:
    >>> count(['red', 'green', 'red', 'blue'])
    '1 blue, 1 green, 2 red'
    """
    return ', '.join(str(countOf(values, x)) + ' ' + str(x) 
            for x in sorted(set(values)))

def avg(values): 
    """
    Average Values
    
    Example:
    >>> result = avg([1,2,3])
    >>> int(result)
    2
    """
    return sum(values) / len(values)

def sum(values): 
    """
    Sum Values
    
    Example:
    >>> result = sum([1,2,3])
    >>> int(result)
    6
    """
    return __builtin__.sum(float(x) for x in values)

