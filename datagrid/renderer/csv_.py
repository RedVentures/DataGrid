#------------------------------------------------------------------------#
# DataGrid - Tabular Data Rendering Library
# Copyright (C) 2009-2010 Adam Wagner <awagner@redventures.com>
#                    Kenny Parnell <kparnell@redventures.com>
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

"""CSV Table Rendering Module"""

import csv
from cStringIO import StringIO

import datagrid.renderer.abstract


class Renderer(datagrid.renderer.abstract.Renderer):
    """CSV Table renderer"""
    def __init__(self):
        self.currentrow = []

    def table(self, config, head, body, foot):
        """Generate CSV file from head/body csv chunks"""
        return ''.join([head, body, foot])

    def row(self, config, style, cells, level=0, name=None, value=None):
        """Generate CSV row from list of cell values"""
        rowdata, self.currentrow = self.currentrow, []
        return _makecsvrow(rowdata)

    def cell(self, config, style, data, column):
        """Echo value back to datagrid core"""
        self.currentrow.append(data)
        return ''

    def head(self, config):
        """Build header row for CSV table"""
        return _makecsvrow(config.columns)

    def tail(self, config, data):
        """CSV file requires no tail record.. skip"""
        return ''


def _makecsvrow(data):
    """Build string with csv row from list of data"""
    buf = StringIO()
    csv.writer(buf).writerow(data)
    csvrow = buf.getvalue()
    buf.close()
    return csvrow

