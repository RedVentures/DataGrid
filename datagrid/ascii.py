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

from itertools import izip
import datagrid.renderer

class Renderer(datagrid.renderer.Renderer):
    """
    ASCII/Text Table Renderer
    """

    # Calculated max str-lens of each table column
    columnwidths = tuple()

    def setup(self, config):
        """
        Complete setup tasks for a successful render
        """
        self.columnwidths = tuple(max(len(data) for data in vals) 
                for vals in izip(*config.data))

    def table(self, config, head, body, tail):
        """
        Generate ASCII table

        Example:
        >>> r = Renderer()
        >>> r.table(None, 'head', 'body', 'tail')
        'headbodytail'
        """
        return head + body + tail

    def row(self, config, cells, level=0, name=None, value=None):
        """
        Generate ASCII Table Row

        Example:
        >>> r = Renderer()
        >>> r.row(None, 'table cells')
        'table cells\\n'
        """
        return cells + '\n'

    def cell(self, config, data, column):
        """
        Generate ASCII Table Cell
        
        Example:
        >>> r = Renderer()
        >>> r.columnwidths = (10,)
        >>> r.cell(None, 'cell data', 0)
        'cell data    '
        """
        return data.ljust(self.column_width(column)+3)

    def head(self, config):
        """
        Generate the Header Row

        Example:
        >>> from collections import namedtuple
        >>> cfg = namedtuple('Cfg', ('columns',))(('Heading',))
        >>> r = Renderer()
        >>> r.columnwidths = (10,)
        >>> r.head(cfg)
        'Heading      \\n=============\\n'
        """
        maxwidth = sum(self.columnwidths) + len(self.columnwidths)*3
        heading = ''.join(v.ljust(self.columnwidths[k] + 3) 
                for k, v in enumerate(config.columns))
        border = '=' * maxwidth
        return heading + '\n' + border + '\n'

    def tail(self, config, cells):
        """
        Generate the Footer Row

        Example:
        >>> r = Renderer()
        >>> r.columnwidths = (10,)
        >>> r.tail(None,'My Data')
        '=============\\nMy Data'
        """
        maxwidth = sum(self.columnwidths) + len(self.columnwidths)*3
        border = '=' * maxwidth
        return border + '\n' + cells

    def column_width(self, i):
        """
        Return column width for requested column
        """
        try: return self.columnwidths[i]
        except IndexError: return 0
        
