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
from collections import Mapping

class DataGrid(object):
    
    data = tuple()
    aggregate = tuple()
    aggregatemethods = {}
    columns = tuple()
    renderer = None
    suppressdetail = False

    def __init__(self, data, renderer, columns=tuple(), aggregate=tuple(),
            aggregatemethods={}, suppressdetail=False):

        # check supplied args
        if not isinstance(aggregatemethods, Mapping):
            raise TypeError('aggregatemethods must be a Mapping object (ie dict)')

        # set instance vars
        self.data = tuple(data)
        self.columns = columns or tuple()
        self.renderer = renderer
        self.suppressdetail = suppressdetail
        self.aggregate = tuple(aggregate)
        self.aggregatemethods = dict(
                (self.columns.index(k), v) for k, v in aggregatemethods.items())

        # call render-setup (if we have one)
        if hasattr(self.renderer, 'setup'): self.renderer.setup(self)

    def render(self):
        head = self.renderer.head(self)
        body = self.render_body(self.data, self.aggregate)
        tail = self.renderer.tail(
                self, self.render_cells(self.generate_aggregate_row(self.data)))
        
        # render table and return
        return self.renderer.table(self, head, body, tail)

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
                rowArgs = dict(name=aggregate[0], value=value, level=aggregateLen)
                subData = [x for x in data if x[idx] == value]
                rowData = self.generate_aggregate_row(subData)
                rowData[self.columns.index(aggregate[0])] = value

                # if details are suppressed, decrement out agg-level
                if self.suppressdetail: rowArgs['level'] -= 1

                # add aggregate row
                output.append(self.render_row(rowData, **rowArgs))

                # render remainder of rows beneath aggregation level
                if rowArgs['level'] > 0:
                    output.append(self.render_body(subData, aggregate[1:]))
            return ''.join(output)
        else:
            return ''.join(self.render_row(row) for row in data)
    
    def render_cells(self, data):
        return ''.join(self.renderer.cell(self, str(v), k) 
                for k, v in enumerate(data))

    def render_row(self, data, **kargs):
        return self.renderer.row(self, self.render_cells(data), **kargs)

    def generate_aggregate_row(self, data):
        # prepopulate with empty data
        rowData = ['' for x in self.columns]

        # generate aggregate-row values
        if len(self.aggregatemethods):
            columnValues = zip(*data)
            for i, m in self.aggregatemethods.items():
                rowData[i] = str(m([float(v) for v in columnValues[i] if v != '']))
        return rowData

