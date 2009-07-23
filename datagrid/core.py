#------------------------------------------------------------------------#
# DataGrid - Tabular Data Rendering Library
# Copyright (C) 2009 Adam Wagner <awagner@redventures.com>
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

import sys
from itertools import chain, groupby
from collections import Mapping
from datagrid.calctools import formula, calculatevalues

class DataGrid(object):
   
    # -- Attributes -- #

    data = tuple()
    aggregate = tuple()
    aggregatemethods = {}
    columns = tuple()   
    descriptions = dict()
    renderer = None
    suppressdetail = False
    sortby = tuple()    # list of columns to sort on

    _displaycolumns = tuple()   # indexes of columns to display
    _allcolumns = tuple()   # all columns (calculated and raw)
    _rawcolumns = tuple()   # columns containing raw data

    
    # -- Properties -- #

    # Calculated Columns
    @property
    def calculatedcolumns(self): return self._calculatedcolumns

    @calculatedcolumns.setter
    def calculatedcolumns(self, value):
        # materialize all methods supplied for calculated columns
        self._calculatedcolumns = dict(
                (k, formula(v) if isinstance(v, str) else v) 
                for k, v in value.iteritems())


    # -- Methods -- #

    def __init__(self, data, renderer, columns=tuple(), descriptions=dict(),
            aggregate=tuple(), aggregatemethods={}, suppressdetail=False,
            calculatedcolumns={}, sortby=[], display=tuple()):
        """
        Setup DataGrid instance
        """

        # check supplied args
        if not isinstance(aggregatemethods, Mapping):
            raise TypeError('aggregatemethods must be a Mapping object (ie dict)')

        # setup datagrid instance
        self.data = tuple(data)         # use tuples for performance
        self.renderer = renderer
        self.columns = display or tuple()
        self.suppressdetail = suppressdetail
        self.aggregate = tuple(aggregate)
        self.calculatedcolumns = calculatedcolumns
        self.descriptions = descriptions

        # when getting calculated column values, we to know what columns contain
        #   raw data versus calculated data
        self._rawcolumns = columns or tuple()

        # append any calculated columns to our list of columns we have
        if self.calculatedcolumns:
            self._allcolumns = tuple(chain(columns, self.calculatedcolumns.keys()))
        else: self._allcolumns = columns or tuple()     # default to tuple
        
        # alias for easier readability below
        idx = self._allcolumns.index        
        
        # change column names to indexes
        self.aggregatemethods = dict((idx(k), v) 
                for k, v in aggregatemethods.iteritems())

        # normalize sortby list -- if sort item is string, assume we want ASC sort
        #   otherwise, use supplied sort direction
        self.sortby = [
                (idx(k), 'asc') if isinstance(k, str) else (idx(k[0]), k[1]) 
                for k in sortby]

    def render(self):
        """
        Begin render process
        """
        # make sure we have display columns
        if not len(self.columns): self.columns = self._allcolumns
        
        # materialize display column into numerical indexes
        self._displaycolumns = tuple(self._allcolumns.index(k) for k in self.columns)

        # run renderer setup logic (if we have any)
        if hasattr(self.renderer, 'setup'): self.renderer.setup(self)

        # build table pieces and glue together
        head = self.renderer.head(self)
        body = self.render_body(self.data, self.aggregate)
        tail = self.renderer.tail(
                self, self.render_cells(self.generate_aggregate_row(self.data)))

        # render table and return
        return self.renderer.table(self, head, body, tail)

    def render_body(self,data,aggregate=[],aggregateRow=None):
        """
        Render table body segment

        For flat data sets (unaggregated), this includes the entire body of
        data.  Aggregated sets, however, will call render_body for each 
        aggregation name/value pair.
        """
        aggregateLen = len(aggregate)

        if aggregateLen:
            # get unique values for aggregation requested
            idx = self._allcolumns.index(aggregate[0])

            # create method to group by
            keyfunc = lambda x: x[idx]

            # group data into chunks of aggregated data
            output = []
            data = sorted(data, key=keyfunc)
            for value, subData in groupby(data, keyfunc):
               
                # we will be looking at this more than once, so we need a concrete
                #   list (tuple), not just an iterator
                subData = tuple(subData)

                # this config gets sent to renderer.row for displaying aggregate 
                #   row information (name, value, etc)
                rowArgs = dict(name=aggregate[0], value=value, level=aggregateLen)
               
                # build aggregate summary row
                rowData = self.generate_aggregate_row(subData, aggregateRow)
                rowData[self._allcolumns.index(aggregate[0])] = value

                # add aggregate row
                output.append(self.render_row(rowData, **rowArgs))

                # if details are suppressed, decrement out agg-level
                if self.suppressdetail: rowArgs['level'] -= 1

                # render remainder of rows beneath aggregation level
                if rowArgs['level'] > 0:
                    output.append(self.render_body(subData, aggregate[1:], rowData))
            return ''.join(output)
        else:
            # sort data and display
            for column, direction in reversed(self.sortby):
                data = sorted(data, key=lambda x: x[column])
                if direction == 'desc': data = reversed(data)
            return ''.join(self.render_row(row) for row in data)
    
    def render_cells(self, data):
        """
        Render cell-block using given data
        """
        # Find calculated column values for given row
        if self.calculatedcolumns:
            dataDict = dict(zip(self._rawcolumns, data))
            dataDict = calculatevalues(dataDict, self.calculatedcolumns)
            data = (dataDict[k] for k in self._allcolumns)

        # Return block of rendered cells (use renderer.cell for actual rendering)
        return ''.join(self.renderer.cell(self, data[k], k) 
                for k in self._displaycolumns)

    def render_row(self, data, **kargs):
        """
        Render table-row
        """
        return self.renderer.row(self, self.render_cells(data), **kargs)

    def generate_aggregate_row(self, data, rowModel=None):
        """
        Generate aggregate row summary data
        """
        # prepopulate with empty data
        rowData = rowModel or ['' for x in self._allcolumns]

        # generate aggregate-row values
        if len(self.aggregatemethods):
            columnValues = zip(*data)
            for i, m in self.aggregatemethods.iteritems():
                rowData[i] = str(m([v for v in columnValues[i] if v != '']))
        return rowData

