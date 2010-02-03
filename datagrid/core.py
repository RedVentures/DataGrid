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

"""The module provides the main DataGrid class."""

import itertools
from copy import copy
from collections import Mapping, defaultdict
from string import ascii_uppercase

from datagrid.calctools import formula, calculatevalues
from datagrid.datatools import multi_sorted


class ColumnDoesNotExistError(Exception):
    """Requested display column not found in given dataset."""
    pass


class DataGrid(object):
    """Tabular Data Rendering Object.

    Provides:
        __init__: receive incoming params and set instance defaults
        render: return compiled representation of tabular data
        
        _normalize: prepare instance vars for render
        _render_body: render grouped segment of data
        _render_cells: render block of cells within a single row
        _render_row: render row of data
        _compile_aggregate_data: aggregate summary data
    """

    def __init__(self, data, labels=None, descriptions=None, groupby=None, 
            aggregate=None, suppressdetail=False, calculatedcolumns=None, 
            sortby=None, columns=None, formatters=None):
        """Receive incoming params and set instance defaults.
        
        Params:
            data: two-dimensional dataset to render
            labels: column name list (for all columns)
            descriptions: long description of what is contained in a column
            groupby: group data into given sets
            aggregate: method to aggregate data in each column for grouped rows
            suppressdetail: (bool) exclude detail-level row from render
            calculatedcolumns: new columns composed from given calculation of 
                existing columns
            sortby: how we will sort the data for display
            columns: display columns to include in rendered output
            formatters: final-pass formatting of columns (ie: currency, percent)

        Example:
        >>> d = DataGrid([[1,2,3],[4,5,6]], ['col-a', 'col-b', 'col-c'])
        >>> d.data
        [[1, 2, 3], [4, 5, 6]]
        >>> d.labels
        ['col-a', 'col-b', 'col-c']
        """
        self.data = list(data)
        self.labels = labels or []
        self.descriptions = descriptions or {}
        self.groupby = groupby or []
        self.aggregate = aggregate or {}
        self.suppressdetail = suppressdetail
        self.calculatedcolumns = calculatedcolumns or {}
        self.sortby = sortby or []
        self.columns = columns or []
        self.formatters = formatters or {}
        self.renderer = None

        # working 'private' vars
        self._rawcolumns = None
        self._allcolumns = None
        self._displaycolumns = None
        self._calculatedcolumns = None


    def render(self, renderer):
        """Compile data into requested tabular form (via renderer).
        
        Params:
            renderer: object/module used to render data into requested form
        
        Example:
        >>> import datagrid.renderer.ascii
        >>> d = DataGrid([[1,2,3],[4,5,6]], ['col-a', 'col-b', 'col-c'])
        >>> renderer = datagrid.renderer.ascii.Renderer()
        >>> type(d.render(renderer))
        <type 'str'>
        >>> d = DataGrid([[1,2,3],[4,5,6]])
        >>> type(d.render(renderer))
        <type 'str'>
        """
        self._normalize()

        # run renderer setup logic (if we have any)
        self.renderer = renderer
        if hasattr(self.renderer, 'setup'): 
            self.renderer.setup(self)

        # build table pieces and glue together
        head = self.renderer.head(self)

        # render body if we are suppressing detail on a flat set
        if not self.suppressdetail or self.groupby:
            body = self._render_body(self.data, self.groupby)
        else:
            body = ''

        tail = self.renderer.tail(self, self._render_cells(
                    self._compile_aggregate_data(self.data)))

        # render table and return
        return self.renderer.table(self, head, body, tail)


    def _normalize(self):
        """Prepare instance for render."""
        # when getting calculated column values, we to know what columns 
        #   contain raw data versus calculated data
        self._rawcolumns = pad_column_names(len(self.data[0]), self.labels)

        # materialize calculated column methods
        self._calculatedcolumns = dict(
                (k, formula(v) if isinstance(v, str) else v)
                for k, v in self.calculatedcolumns.iteritems())

        # append any calculated columns to our list of columns we have
        if self._calculatedcolumns:
            self._allcolumns = tuple(itertools.chain(self._rawcolumns, 
                self._calculatedcolumns.keys()))
        else: 
            self._allcolumns = self._rawcolumns
        
        # alias for easier readability below
        idx = self._allcolumns.index        
        
        # change column names to indexes
        self.aggregate = dict((idx(k), v) 
                for k, v in self.aggregate.iteritems())
        self.formatters = dict((idx(k), v)
                for k, v in self.formatters.iteritems())

        # normalize sortby list -- if sort item is string, assume we want 
        #   ascending sort, otherwise, use supplied sort direction
        self.sortby = [
                (idx(k), 'asc') if isinstance(k, str) else (idx(k[0]), k[1]) 
                for k in self.sortby]

        # make sure we have display columns
        if not len(self.columns): 
            self.columns = self._allcolumns

        # materialize display column into numerical indexes
        if len(self._allcolumns):
            self._displaycolumns = []
            try:
                for column in self.columns:
                    self._displaycolumns.append(self._allcolumns.index(column))
            except ValueError:
                raise ColumnDoesNotExistError(column)
        else:
            self._allcolumns = self._displaycolumns = range(len(self.data[0]))


    def _render_body(self, data, groupby=list(), aggregate_row=None):
        """Render table body segment

        For flat data sets (unaggregated), this includes the entire body of
        data.  Aggregated sets, however, will call _render_body for each 
        aggregation name/value pair."""
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
                rowdata = self._compile_aggregate_data(subdata, aggregate_row)
                rowdata[idx] = value

                # if details are suppressed, decrement out agg-level
                if self.suppressdetail: 
                    rowargs['level'] -= 1

                # generate aggregate row
                rowoutput = self._render_row(rowdata, **rowargs)

                # render remainder of rows beneath aggregation level
                if rowargs['level'] > 0:
                    rowoutput += self._render_body(subdata, groupby[1:], 
                            rowdata)

                # append rendered data to output buffer
                output.append((rowdata, rowoutput))

            # sort aggregate row sorting and return compiled string
            output = multi_sorted(output, self.sortby, lambda c, d: d[0][c])
            return ''.join(row[1] for row in output)
        else:
            # sort data and display
            data = multi_sorted(data, self.sortby)
            return ''.join(self._render_row(row) for row in data)
    
    def _render_cells(self, data):
        """Render cell-block using given data"""
        # Find calculated column values and apply formatting for given row
        if self._calculatedcolumns:
            data_dict = dict(zip(self._rawcolumns, data))

            # calculated columns
            if self._calculatedcolumns:
                data_dict = calculatevalues(data_dict, self._calculatedcolumns)

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

    def _render_row(self, data, **kargs):
        """Render table-row"""
        return self.renderer.row(self, self._render_cells(data), **kargs)

    def _compile_aggregate_data(self, data, rowmodel=None):
        """Generate aggregate row summary data"""
        # prepopulate with empty data
        rowdata = rowmodel or [''] * len(self._allcolumns)

        # generate aggregate-row values
        if len(self.aggregate):
            column_values = zip(*data)
            for i, method in self.aggregate.iteritems():
                rowdata[i] = str(method([v 
                    for v in column_values[i] if v != '']))
        return rowdata


def pad_column_names(width, columns=None):
    """Return columns list with any missing columns filled with generated names.
    
    Example:
    >>> pad_column_names(5, ['mycol', 'yourcol'])
    ['mycol', 'yourcol', 'C', 'D', 'E']
    >>> pad_column_names(5)
    ['A', 'B', 'C', 'D', 'E']
    """
    if not columns:
        columns = []
    else:
        columns = copy(columns)
    initial_len = len(columns)

    # name generating generator
    def mknames():
        for block in (itertools.product(ascii_uppercase, repeat=x) 
                for x in itertools.count(1)):
            for name in block:
                yield name

    # fill column list
    names = mknames()
    for idx in itertools.count(1):
        name = ''.join(names.next())
        if idx <= initial_len:
            continue
        if idx > width:
            break
        columns.append(name)

    return columns

