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

class DataGrid(object):
    
    data = []
    aggregate = []
    totalAggLevels = 0
    columns = []

    tableFormat = """
        <link rel='stylesheet' type='text/css' href='datagrid.css' />
        <table class='helper-gridview'><tbody>{body}</tbody></table>
        """
    rowFormat = "<tr class='l-{level}'>{cells}</tr>"
    aggRowFormat = """
        <tr class='l-{level}'>
            <td class='f' style='padding-left: {indent}px; 
                    padding-top: {level}px;'>
                <i>{aggname}:</i><span>{aggvalue}</span>
            </td>
            {cells}
        </tr>
        """
    cellFormat = "<td>{data}</td>"

    def __init__(self, data, columns=[], aggregate=[]):
        # convert data to tuple
        self.data = data

        # save aggregation
        self.aggregate = aggregate
        self.totalAggLevels = len(aggregate)

    def render(self):
        # render table and return
        return self.tableFormat.format(
                body=self.render_body(self.data, self.aggregate))

    def render_body(self,data,aggregate=[]):
        aggregateLen = len(aggregate)

        # reference render_row method
        render_method = self.render_row_agg \
            if self.totalAggLevels else self.render_row
        render_row = partial(render_method, aggregateLevel=aggregateLen)
        rowArgs = {'aggname': '', 'aggvalue': '', 
                'indent': (self.totalAggLevels-aggregateLen+1)*20} \
            if self.totalAggLevels else {}

        if aggregateLen:
            # get unique values for aggregation requested
            idx = self.columns.index(aggregate[0])
            values = set(x[idx] for x in data)

            # build output string
            output = []
            for value in values:
                # update row args (agg name & value)
                rowArgs.update(aggname=aggregate[0], aggvalue=value)
                subData = [x for x in data if x[idx] == value]
                output.append(render_row(subData[0], **rowArgs))

                # render remainder of rows beneath aggregation level
                output.append(self.render_body(subData, aggregate[1:]))
            return ''.join(output)
        else:
            return '\n'.join(render_row(row, **rowArgs) for row in data)
    
    def render_row(self,data,aggregateLevel):
        cells = ''.join(self.cellFormat.format(data=str(x)) for x in data)
        return self.rowFormat.format(cells=cells, level=aggregateLevel)

    def render_row_agg(self,data,aggregateLevel, **kargs):
        cells = ''.join(self.cellFormat.format(data=str(x)) for x in data)
        return self.aggRowFormat.format(cells=cells, \
                level=aggregateLevel, **kargs)

