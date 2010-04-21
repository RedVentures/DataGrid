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

"""ASCII Table Rendering Module"""

import datagrid.renderer.abstract

class Renderer(datagrid.renderer.abstract.Renderer):
    """ASCII/Text Table Renderer"""

    def __init__(self):
        """Initialize instance vars."""
        # Internal storage
        self._currentrow = []
        self._bodyrows = []
        self._tailrow = []

        # calculated column widths (for proper column alignment)
        self.columnwidths = []

        # calculated aggregation depth
        self.levels = 0
        
        # Reference to datagrid.core.DataGrid object that is using renderer 
        self.config = None
        
        # Cell padding 
        self.padding = ' ' * 3

    def setup(self, config):
        """Prepare renderer to render new table."""
        self.config = config

        # initial column widths from headers
        self.columnwidths = [len(column) for column in config.columns]
            
        # find number of aggregation levels
        self.levels = len(self.config.groupby)
        if config.suppressdetail: 
            self.levels -= 1 # detail row does not count

    def table(self, config, head, body, tail): 
        """Generate table from cached values and return string."""
        # Build table header
        head = self._head()

        # Build main body of table
        body = ''.join(self._generate_rows())

        # Build footer (or tail) or table
        # pylint: disable-msg=w0142
        tail = self._tail(''.join(self._cell(*a) for a in self._tailrow))

        return head + body + tail

    # pylint: disable-msg=w0221
    def row(self, *args, **kargs): 
        """Core-facing row method.
        capture what we have in our cell collector and give it a home
        in the bodyrows list, then clear the collector to leave room
        for the next set of cells.
        """
        self._bodyrows.append((args[2:], kargs, self._currentrow))
        self._currentrow = []
        return ''

    def cell(self, config, style, data, column): 
        """Formatter that is called to render cell data
        for the ascii module, we simply capture this so we can output it
            once we've seen what the all cells look like"""
        # make sure we have the right format
        data = str(data)

        # add to list of rows to process
        self._currentrow.append((data, column))

        # pit against previous length champion
        self.columnwidths[column] = max(self.columnwidths[column], len(data))

        return ''   # datagrid.core needs to think this worked properly

    def head(self, config): 
        """Core-facing head method, all we usually use here is config, but
        we already have that stored on the object, so we can do nothing
        now."""
        return ''

    def tail(self, config, cells): 
        """Core-facing tail method, capture what we need to call this 
        'for real' later"""
        self._tailrow = (self._currentrow)
        self._currentrow = []

    def _generate_rows(self):
        """Generate row from cached data."""
        for args, kargs, cells in self._bodyrows:
            # generate cells for row
            # pylint: disable-msg=w0142
            cells = ''.join(self._cell(*cellArgs) for cellArgs in cells) 

            # return generated row
            # pylint: disable-msg=w0142
            yield self._row(cells, *args, **kargs)

    def _row(self, cells, style, level=0, name=None, value=None):
        """Generate ASCII Table Row

        Example:
        >>> from collections import namedtuple
        >>> cfg = namedtuple('Cfg', 'aggregate')(tuple())
        >>> r = Renderer()
        >>> r.config = cfg
        >>> r._row('table cells')
        'table cells\\n'
        """
        if self.levels:
            indent = self.aggregate_indent(level)
            row = '%s%s\n' % (indent, cells)
            if level > 0: 
                return '%s%s: %s\n%s' % (indent, name, value, row)
            else: 
                return row
        else: 
            return '%s\n' % cells

    def _cell(self, data, column):
        """Generate ASCII Table Cell
        
        Example:
        >>> r = Renderer()
        >>> r.columnwidths = (10,)
        >>> r._cell('cell data', 0)
        'cell data    '
        >>> r = Renderer()
        >>> r.columnwidths = (10,)
        >>> r._cell('2.0', 0)
        '       2.0   '
        """
        try:
            float(data)
            justify = data.rjust
        except ValueError:
            justify = data.ljust
        return justify(self.column_width(column)) + self.padding

    def _head(self):
        """Generate the Header Row

        Example:
        >>> from collections import namedtuple
        >>> cfg = namedtuple('Cfg', 'columns aggregate')(('Heading',),tuple())
        >>> r = Renderer()
        >>> r.config = cfg
        >>> r.columnwidths = (10,)
        >>> r._head()
        'Heading      \\n=============\\n'
        """
        maxwidth = sum(self.columnwidths) + \
                len(self.columnwidths) * len(self.padding)
        heading = ''.join(v.ljust(self.columnwidths[k]) + self.padding 
                for k, v in enumerate(self.config.columns))
        border = '=' * maxwidth
        indent = self.aggregate_indent()
        return indent + heading + '\n' + indent + border + '\n'

    def _tail(self, cells):
        """Generate the Footer Row

        Example:
        >>> from collections import namedtuple
        >>> Cfg = namedtuple('Cfg', 'aggregate')
        >>> r = Renderer()
        >>> r.config = Cfg(tuple())
        >>> r.columnwidths = (10,)
        >>> r._tail('My Data')
        '=============\\nMy Data'
        """
        maxwidth = sum(self.columnwidths) + \
                len(self.columnwidths) * len(self.padding)
        border = '=' * maxwidth
        indent = self.aggregate_indent()
        return indent + border + '\n' + indent + cells

    def column_width(self, index):
        """Return column width for requested column

        Example:
        >>> r = Renderer()
        >>> r.columnwidths = tuple([5])
        >>> r.column_width(0)
        5
        >>> r.column_width(1)
        0
        """
        try: 
            return self.columnwidths[index]
        except IndexError: 
            return 0
        
    def aggregate_indent(self, level=None):
        """Get aggregate row prefix
        
        >>> from collections import namedtuple
        >>> Cfg = namedtuple('Cfg', 'aggregate')
        >>> r = Renderer()
        >>> r.levels = 2
        >>> r.config = Cfg((1,2))
        >>> r.aggregate_indent()
        '    '
        >>> r.aggregate_indent(1)
        '|   '
        """
        if self.levels:
            try:
                level_markers = (self.levels - level) * '|'
                return level_markers.ljust(self.levels + 1) + ' '
            except TypeError: 
                return ' ' * (self.levels + 2)
        else: 
            return ''

