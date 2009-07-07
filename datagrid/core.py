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

import sys
from functools import partial
from itertools import izip

class DataGrid(object):
    
    data = []
    aggregate = []
    totalAggLevels = 0
    columns = []
    columnWidths = []
    renderer = None

    def __init__(self, data, renderer, columns=[], aggregate=[]):
        # cement data
        data = tuple(data)

        # setup renderer
        renderer.aggregation = tuple(aggregate)
        try: renderer.columns = tuple(columns)
        except TypeError: renderer.columns = tuple(range(len(data[0])))

        # set instance vars
        self.data = list(data)
        self.renderer = renderer
        self.aggregate = aggregate
        self.totalAggLevels = len(aggregate)
        self.columnWidths = tuple(max(len(data) for data in vals) 
                for vals in izip(*self.data))

    def render(self):
        # render table and return
        return self.renderer.table(
                self.render_body(self.data, self.aggregate))

    def render_body(self,data,aggregate=[]):
        aggregateLen = len(aggregate)

        if aggregateLen:
            # get unique values for aggregation requested
            idx = self.columns.index(aggregate[0])
            values = set(x[idx] for x in data)

            # build output string
            output = []
            for value in values:
                # update row args (agg name & value)
                rowArgs = dict(aggname=aggregate[0], aggvalue=value)
                subData = [x for x in data if x[idx] == value]
                output.append(self.render_row(subData[0], **rowArgs))

                # render remainder of rows beneath aggregation level
                output.append(self.render_body(subData, aggregate[1:]))
            return ''.join(output)
        else:
            return '\n'.join(self.render_row(row) for row in data)
    
    def render_row(self, data, aggregateLevel = 0, **kargs):
        cells = ''.join(self.renderer.cell(str(v), self.column_width(k)) 
                for k, v in enumerate(data))
        return self.renderer.row(cells, aggregateLevel, **kargs)

    def column_width(self, i):
        try: return self.columnWidths[i]
        except IndexError: return 0

