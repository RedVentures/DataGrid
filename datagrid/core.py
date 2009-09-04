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

"""
The module provides the main DataGrid class.
"""

import itertools
from collections import Mapping

from datagrid.calctools import formula, calculatevalues
from datagrid.datatools import multi_sorted

class DataGrid(object):
    """Core DataGrid Class"""
   
    # -- Attributes -- #

    # List of data rows we are going to render
    data = tuple()

    # Columns we want to aggregate on (or group by)
    groupby = tuple()

    # How we intend to summarize each column for each aggregation
    aggregate = dict()

    # Format methods applied to each column value
    formatters = dict()

    # Dictionary describing each column's purpose/meaning
    descriptions = dict()

    # Class/Module we will use to render our datagrid (ie: datagrid.html)
    renderer = None

    # Should we hide bottom level rows (the true data rows) and only 
    # display the aggregated data
    suppressdetail = False
    sortby = tuple()    # list of columns to sort on

    _calculatedcolumns = dict()
    _columns = tuple()      # columns to display
    _displaycolumns = tuple()   # indexes of columns to display
    _allcolumns = tuple()   # all columns (calculated and raw)
    _rawcolumns = tuple()   # columns containing raw data

    
    # -- Properties -- #

    # Calculated Columns
    @property
    def calculatedcolumns(self): 
        return self._calculatedcolumns

    @calculatedcolumns.setter
    def calculatedcolumns(self, value):
        # materialize all methods supplied for calculated columns
        self._calculatedcolumns = dict(
                (k, formula(v) if isinstance(v, str) else v) 
                for k, v in value.iteritems())

    # Display columns
    @property
    def columns(self): 
        return self._columns or ['']*len(self._displaycolumns)

    @columns.setter
    def columns(self, value):
        self._columns = value or tuple() 

    # -- Methods -- #

    def __init__(self, data, renderer, raw_columns=list(), descriptions=dict(),
            groupby=tuple(), aggregate=dict(), suppressdetail=False,
            calculatedcolumns=dict(), sortby=list(), columns=tuple(), 
            formatters=dict()):
        """
        Setup DataGrid instance
        """
        # check supplied args
        if not isinstance(aggregate, Mapping):
            raise TypeError('aggregate must be a Mapping object (ie dict)')

        # setup datagrid instance
        self.data = tuple(data)         # use tuples for performance
        self.renderer = renderer
        self.columns = columns or tuple()
        self.suppressdetail = suppressdetail
        self.groupby = tuple(groupby)
        self.calculatedcolumns = calculatedcolumns
        self.descriptions = descriptions

        # when getting calculated column values, we to know what columns 
        #   contain raw data versus calculated data
        self._rawcolumns = raw_columns or tuple()

        # append any calculated columns to our list of columns we have
        if self.calculatedcolumns:
            self._allcolumns = tuple(itertools.chain(raw_columns, 
                self.calculatedcolumns.keys()))
        else: 
            self._allcolumns = raw_columns or tuple()     # default to tuple
        
        # alias for easier readability below
        idx = self._allcolumns.index        
        
        # change column names to indexes
        self.aggregate = dict((idx(k), v) 
                for k, v in aggregate.iteritems())
        self.formatters = dict((idx(k), v)
                for k, v in formatters.iteritems())

        # normalize sortby list -- if sort item is string, assume we want 
        #   ascending sort, otherwise, use supplied sort direction
        self.sortby = [
                (idx(k), 'asc') if isinstance(k, str) else (idx(k[0]), k[1]) 
                for k in sortby]

    def render(self):
        """
        Begin render process
        """
        # make sure we have display columns
        if not len(self.columns): 
            self.columns = self._allcolumns

        # materialize display column into numerical indexes
        if len(self._allcolumns):
            self._displaycolumns = tuple(self._allcolumns.index(k) 
                    for k in self.columns)
        else:
            self._allcolumns = self._displaycolumns = range(len(self.data[0]))

        # run renderer setup logic (if we have any)
        if hasattr(self.renderer, 'setup'): 
            self.renderer.setup(self)

        # build table pieces and glue together
        head = self.renderer.head(self)

        # render body if we are suppressing detail on a flat set
        if not self.suppressdetail or self.groupby:
            body = self.render_body(self.data, self.groupby)
        else:
            body = ''

        tail = self.renderer.tail(self, self.render_cells(
                    self.generate_aggregate_row(self.data)))

        # render table and return
        return self.renderer.table(self, head, body, tail)

    def render_body(self, data, groupby=list(), aggregate_row=None):
        """
        Render table body segment

        For flat data sets (unaggregated), this includes the entire body of
        data.  Aggregated sets, however, will call render_body for each 
        aggregation name/value pair.
        """
        groupby_len = len(groupby)

        if groupby_len:
            # get unique values for aggregation requested
            idx = self._allcolumns.index(groupby[0])

            # create method to group by
            keyfunc = lambda x: x[idx]

            # group data into chunks of aggregated data
            output = []
            data = sorted(data, key=keyfunc)
            for value, subdata in itertools.groupby(data, keyfunc):
               
                # we will be looking at this more than once, so we need a 
                #   concrete list (tuple), not just an iterator
                subdata = tuple(subdata)

                # format aggregate value
                if idx in self.formatters:
                    fvalue = self.formatters[idx](value)
                else:
                    fvalue = value

                # this config gets sent to renderer.row for displaying 
                #   aggregate row information (name, value, etc)
                rowargs = dict(name=groupby[0], value=fvalue, level=groupby_len)
               
                # build aggregate summary row
                rowdata = self.generate_aggregate_row(subdata, aggregate_row)
                rowdata[idx] = value

                # if details are suppressed, decrement out agg-level
                if self.suppressdetail: 
                    rowargs['level'] -= 1

                # generate aggregate row
                rowoutput = self.render_row(rowdata, **rowargs)

                # render remainder of rows beneath aggregation level
                if rowargs['level'] > 0:
                    rowoutput += self.render_body(subdata, groupby[1:], 
                            rowdata)

                # append rendered data to output buffer
                output.append((rowdata, rowoutput))

            # sort aggregate row sorting and return compiled string
            output = multi_sorted(output, self.sortby, lambda c, d: d[0][c])
            return ''.join(row[1] for row in output)
        else:
            # sort data and display
            data = multi_sorted(data, self.sortby)
            return ''.join(self.render_row(row) for row in data)
    
    def render_cells(self, data):
        """
        Render cell-block using given data
        """
        # Find calculated column values and apply formatting for given row
        if self.calculatedcolumns:
            data_dict = dict(zip(self._rawcolumns, data))

            # calculated columns
            if self.calculatedcolumns:
                data_dict = calculatevalues(data_dict, self.calculatedcolumns)

            data = [data_dict[k] for k in self._allcolumns]

        # formatted columns
        if self.formatters:
            data = list(data)
            for column, formatter in self.formatters.iteritems():
                if data[column] != '': 
                    data[column] = formatter(data[column])

        # Return block of rendered cells (use renderer.cell for actual 
        #   rendering)
        return ''.join(self.renderer.cell(self, data[k], i) 
                for i, k in enumerate(self._displaycolumns))

    def render_row(self, data, **kargs):
        """
        Render table-row
        """
        return self.renderer.row(self, self.render_cells(data), **kargs)

    def generate_aggregate_row(self, data, rowmodel=None):
        """
        Generate aggregate row summary data
        """
        # prepopulate with empty data
        rowdata = rowmodel or [''] * len(self._allcolumns)

        # generate aggregate-row values
        if len(self.aggregate):
            column_values = zip(*data)
            for i, method in self.aggregate.iteritems():
                rowdata[i] = str(method([v 
                    for v in column_values[i] if v != '']))
        return rowdata

