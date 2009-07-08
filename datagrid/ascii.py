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

"""ASCII Table Rendering Module"""

def table(config, body):
    """
    Generate ASCII table

    Example:
    >>> table(None, 'table body')
    'table body'
    """
    return body

def row(config, cells, level=0, name=None, value=None):
    """
    Generate ASCII Table Row

    Example:
    >>> row(None, 'table cells')
    'table cells\\n'
    """
    return cells + '\n'

def cell(config, data, maxwidth):
    """
    Generate ASCII Table Cell
    
    Example:
    >>> cell(None, 'cell data', 10)
    'cell data    '
    """
    return data.ljust(maxwidth+3)

def head(config):
    """
    Generate the Header Row

    Example:
    >>> from collections import namedtuple
    >>> cfg = namedtuple('Cfg', ('columns', 'maxwidths'))(('Heading',), (10,))
    >>> head(cfg)
    'Heading   \\n============='
    """
    maxwidth = sum(config.maxwidths) + len(config.maxwidths)*3
    heading = ''.join(v.ljust(config.maxwidths[k]) for k, v in enumerate(config.columns))
    border = '=' * maxwidth
    return heading + '\n' + border

def tail(config, cells):
    """
    Generate the Footer Row

    Example:
    >>> from collections import namedtuple
    >>> cfg = namedtuple('Cfg', ('maxwidths',))((10,))
    >>> tail(cfg,'My Data')
    '=============\\nMy Data'
    """
    maxwidth = sum(config.maxwidths) + len(config.maxwidths)*3
    border = '=' * maxwidth
    return border + '\n' + cells

