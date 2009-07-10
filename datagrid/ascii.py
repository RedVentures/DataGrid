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
    config = None

    def setup(self, config):
        """
        Complete setup tasks for a successful render
        """
        self.config = config
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
        >>> from collections import namedtuple
        >>> cfg = namedtuple('Cfg', 'aggregate')(tuple())
        >>> r = Renderer()
        >>> r.row(cfg, 'table cells')
        'table cells\\n'
        """
        if config.aggregate:
            levels = len(config.aggregate)
            indent = ((levels - level) * '|').ljust(levels + 1) + ' '
            row = indent + cells + '\n'
            if level > 0: return indent + name + ': ' + value + '\n' + row
            else: return row
        else: return cells + '\n'

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
        >>> cfg = namedtuple('Cfg', 'columns aggregate')(('Heading',),tuple())
        >>> r = Renderer()
        >>> r.config = cfg
        >>> r.columnwidths = (10,)
        >>> r.head(cfg)
        'Heading      \\n=============\\n'
        """
        maxwidth = sum(self.columnwidths) + len(self.columnwidths)*3
        heading = ''.join(v.ljust(self.columnwidths[k] + 3) 
                for k, v in enumerate(config.columns))
        border = '=' * maxwidth
        indent = self.aggregate_indent()
        return indent + heading + '\n' + indent + border + '\n'

    def tail(self, config, cells):
        """
        Generate the Footer Row

        Example:
        >>> from collections import namedtuple
        >>> Cfg = namedtuple('Cfg', 'aggregate')
        >>> r = Renderer()
        >>> r.config = Cfg(tuple())
        >>> r.columnwidths = (10,)
        >>> r.tail(None,'My Data')
        '=============\\nMy Data'
        """
        maxwidth = sum(self.columnwidths) + len(self.columnwidths)*3
        border = '=' * maxwidth
        indent = self.aggregate_indent()
        return indent + border + '\n' + indent + cells

    def column_width(self, i):
        "Return column width for requested column"
        try: return self.columnwidths[i]
        except IndexError: return 0
        
    def aggregate_indent(self, level=None):
        "Get aggregate row prefix"
        levels = len(self.config.aggregate)
        if levels:
            try:
                return ((levels - level) * '|').ljust(levels + 1) + ' '
            except: return ' ' * (levels + 2)
        else: return ''

