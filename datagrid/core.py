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

    def __init__(self, data, renderer, columns=tuple(), aggregate=tuple(),
            aggregatemethods={}):

        # check supplied args
        if not isinstance(aggregatemethods, Mapping):
            raise TypeError('aggregatemethods must be a Mapping object (ie dict)')

        # set instance vars
        self.data = tuple(data)
        self.columns = columns if columns is not None else tuple()
        self.renderer = renderer
        self.aggregate = tuple(aggregate)
        self.aggregatemethods = aggregatemethods

        # call render-setup (if we have one)
        if hasattr(self.renderer, 'setup'): self.renderer.setup(self)

    def render(self):
        # render table and return
        return self.renderer.table(self,
                self.renderer.head(self),
                self.render_body(self.data, self.aggregate),
                self.renderer.tail(self, '')
                )

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
                output.append(self.render_row(subData[0], **rowArgs))

                # render remainder of rows beneath aggregation level
                output.append(self.render_body(subData, aggregate[1:]))
            return ''.join(output)
        else:
            return ''.join(self.render_row(row) for row in data)
    
    def render_row(self, data, **kargs):
        cells = ''.join(self.renderer.cell(self, str(v), k) 
                for k, v in enumerate(data))
        return self.renderer.row(self, cells, **kargs)

