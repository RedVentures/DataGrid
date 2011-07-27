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

"""datagrid.core test module"""

import unittest
import __builtin__

from datagrid.core import DataGrid
from datagrid import format


# -- TEST FIXTURES -- #

# Test data: simple 2x3 table
testData = [['1', '2', '3'], ['4', '5', '6']]

# Column names for test table
testCols = ['one', 'two', 'three']

class StackTestRenderer(object):
    """
    Allows testing of datagrid-renderer interaction and call order
    """

    # Stack of filter calls made
    callLog = []

    def __getattr__(self, name):
        # Create new method
        def method(*args, **kargs):
            self.callLog.append(name)
            return ''

        # Assign to instance and return
        setattr(self,name,method)
        return method

class EchoRenderer(object):
    """
    Test Renderer that simply echos method name and received input.
    This renderer is used for basic output testing
    """

    def table(self, config, head, body, tail):
        return "[t]" + head + body + tail + "[/t]"

    def row(self, config, style, cells, level=0, name=None, value=None):
        return "[r]" + cells + "[/r]"

    def cell(self, config, style, data, column):
        return "[c]%s[/c]" % data

    def head(self, config):
        return "[h/]"

    def tail(self, config, cells):
        return "[f]" + cells + "[/f]"


# -- TEST CLASSES -- #

class TestRenderInteract(unittest.TestCase):
    """DataGrid core unit-test"""

    # Grid fixture
    grid = None

    def setUp(self):
        """Setup fixtures"""
        self.grid = DataGrid(testData, testCols)

    def tearDown(self):
        """Cleanup and prep for next run"""
        StackTestRenderer.callLog = []

    def testRender(self):
        # Evaluation order or render methods for given test table
        testLog = ['setup', 'head',             # Setup table and header
                'cell', 'cell', 'cell', 'row',  # Rendering Row 1 
                'cell', 'cell', 'cell', 'row',  # Rendering Row 2
                'cell', 'cell', 'cell', 'tail', # Rendering Footer
                'table']                        # Wrap up table render

        # Test simple render
        self.grid.render(StackTestRenderer())
        self.assertEquals(testLog, self.grid.renderer.callLog)

    def testRenderAggregate(self):
        # Aggregation eval order
        testLog = ['setup', 'head',             # Setup table and header
                'cell', 'cell', 'cell', 'row',  # Rendering Agg Row 1 
                'cell', 'cell', 'cell', 'row',  # Rendering Row 1 
                'cell', 'cell', 'cell', 'row',  # Rendering Agg Row 2
                'cell', 'cell', 'cell', 'row',  # Rendering Row 2 
                'cell', 'cell', 'cell', 'tail', # Rendering Footer
                'table']                        # Wrap up table render

        # Test simple render
        self.grid.groupby = ['one']
        self.grid.render(StackTestRenderer())
        self.assertEquals(testLog, self.grid.renderer.callLog)


class TestOutput(unittest.TestCase):

    # Grid fixture
    grid = None

    def setUp(self):
        """Setup for all tests in class"""
        self.grid = DataGrid(testData, testCols)

    def testBasicRender(self):
        # Output of test run should look like this
        expected = "[t][h/][r][c]1[/c][c]2[/c][c]3[/c][/r]" \
                "[r][c]4[/c][c]5[/c][c]6[/c][/r][f][c][/c][c][/c][c][/c][/f][/t]"
        self.assertEquals(expected, self.grid.render(EchoRenderer()))

    def testHideColumn(self):
        # Output of test run should look like this
        expected = "[t][h/][r][c]1[/c][c]2[/c][/r]" \
                "[r][c]4[/c][c]5[/c][/r][f][c][/c][c][/c][/f][/t]"

        # Only show first two columns
        self.grid.columns = ('one', 'two')
        self.assertEquals(expected, self.grid.render(EchoRenderer()))

    def testFormattedRender(self):
        # Output of test run should look like this
        expected = "[t][h/][r][c]01[/c][c]2[/c][c]3[/c][/r]" \
                "[r][c]04[/c][c]5[/c][c]6[/c][/r][f][c][/c][c][/c][c][/c][/f][/t]"
        self.grid.formatters = {'one': lambda x: x.zfill(2)}
        self.assertEquals(expected, self.grid.render(EchoRenderer()))

    def testSortByRender(self):
        # Output of test run should look like this
        expected = ("[t][h/]"
                "[r][c]4[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[f][c][/c][c][/c][c][/c][/f]"
                "[/t]")
        self.grid.sortby = [('one', 'desc')]
        self.assertEquals(expected, self.grid.render(EchoRenderer()))

    def testGroup(self):
        self.grid.groupby = ['one']
        expected = ("[t][h/]"
                "[r][c]1[/c][c][/c][c][/c][/r]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]4[/c][c][/c][c][/c][/r]"
                "[r][c]4[/c][c]5[/c][c]6[/c][/r]"
                "[f][c][/c][c][/c][c][/c][/f]"
                "[/t]")
        actual = self.grid.render(EchoRenderer())
        self.assertEquals(expected, actual)

    def testGroupAggrigate(self):
        self.grid.data = [[1, 2, 3], [4, 5, 6]]
        self.grid.groupby = ['one']
        self.grid.aggregate['two'] = vars(__builtin__)['sum']
        self.grid.aggregate['three'] = vars(__builtin__)['sum']
        expected = ("[t][h/]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]4[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]4[/c][c]5[/c][c]6[/c][/r]"
                "[f][c][/c][c]7[/c][c]9[/c][/f]"
                "[/t]")
        actual = self.grid.render(EchoRenderer())
        self.assertEquals(expected, actual)

    def testGroupAggrigateSort(self):
        self.grid.data = [[1, 2, 3], [4, 5, 6]]
        self.grid.groupby = ['one']
        self.grid.aggregate['two'] = vars(__builtin__)['sum']
        self.grid.aggregate['three'] = vars(__builtin__)['sum']
        self.grid.sortby = [('two', 'desc')]
        expected = ("[t][h/]"
                "[r][c]4[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]4[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[f][c][/c][c]7[/c][c]9[/c][/f]"
                "[/t]")
        actual = self.grid.render(EchoRenderer())
        self.assertEquals(expected, actual)

    def testGroupAggrigateSortDesc(self):
        self.grid.data = [[1, 2, 3], [1, 2, 3], [1, 2, 3],  [4, 5, 6]]
        self.grid.groupby = ['one']
        self.grid.aggregate['two'] = vars(__builtin__)['sum']
        self.grid.aggregate['three'] = vars(__builtin__)['sum']
        self.grid.sortby = [('two', 'desc')]
        expected = ("[t][h/]"
                "[r][c]1[/c][c]6[/c][c]9[/c][/r]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]4[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]4[/c][c]5[/c][c]6[/c][/r]"
                "[f][c][/c][c]11[/c][c]15[/c][/f]"
                "[/t]")
        actual = self.grid.render(EchoRenderer())
        self.assertEquals(expected, actual)

    def testGroupAggrigateSortAsc(self):
        self.grid.data = [[1, 2, 3], [1, 2, 3], [1, 2, 3],  [4, 5, 6]]
        self.grid.groupby = ['one']
        self.grid.aggregate['two'] = vars(__builtin__)['sum']
        self.grid.aggregate['three'] = vars(__builtin__)['sum']
        self.grid.sortby = [('two', 'asc')]
        expected = ("[t][h/]"
                "[r][c]4[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]4[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]1[/c][c]6[/c][c]9[/c][/r]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[f][c][/c][c]11[/c][c]15[/c][/f]"
                "[/t]")
        actual = self.grid.render(EchoRenderer())
        self.assertEquals(expected, actual)

    def testGroupAggrigateSortAscComplex(self):
        self.grid.data = [[4, 2, 3], [4, 2, 3], [4, 2, 3],  [1, 5, 6]]
        self.grid.groupby = ['one']
        self.grid.aggregate['two'] = vars(__builtin__)['sum']
        self.grid.aggregate['three'] = vars(__builtin__)['sum']
        self.grid.sortby = [('two', 'asc')]
        expected = ("[t][h/]"
                "[r][c]1[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]1[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]4[/c][c]6[/c][c]9[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]3[/c][/r]"
                "[f][c][/c][c]11[/c][c]15[/c][/f]"
                "[/t]")
        actual = self.grid.render(EchoRenderer())
        self.assertEquals(expected, actual)

    def testGroupAggrigateSortDescComplex(self):
        self.grid.data = [[4, 2, 3], [4, 2, 3], [4, 2, 3],  [1, 5, 6]]
        self.grid.groupby = ['one']
        self.grid.aggregate['two'] = vars(__builtin__)['sum']
        self.grid.aggregate['three'] = vars(__builtin__)['sum']
        self.grid.sortby = [('two', 'desc')]
        expected = ("[t][h/]"
                "[r][c]4[/c][c]6[/c][c]9[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]1[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]1[/c][c]5[/c][c]6[/c][/r]"
                "[f][c][/c][c]11[/c][c]15[/c][/f]"
                "[/t]")
        actual = self.grid.render(EchoRenderer())
        self.assertEquals(expected, actual)

    def testMultiGroupAggrigate(self):
        self.grid.data = [[4, 2, 3], [4, 2, 3], [4, 2, 3],  [1, 5, 6]]
        self.grid.groupby = ['one','two']
        self.grid.aggregate['two'] = vars(__builtin__)['sum']
        self.grid.aggregate['three'] = vars(__builtin__)['sum']
        expected = ("[t][h/]"
                "[r][c]1[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]1[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]1[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]4[/c][c]6[/c][c]9[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]9[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]3[/c][/r]"
                "[f][c][/c][c]11[/c][c]15[/c][/f]"
                "[/t]")
        actual = self.grid.render(EchoRenderer())
        self.assertEquals(expected, actual)

    def testMultiGroupAggrigateSort(self):
        self.grid.data = [[4, 2, 3], [4, 2, 3], [4, 2, 3],  [1, 5, 6]]
        self.grid.groupby = ['one','two']
        self.grid.aggregate['two'] = vars(__builtin__)['sum']
        self.grid.aggregate['three'] = vars(__builtin__)['sum']
        self.grid.sortby = [('three', 'asc')]
        expected = ("[t][h/]"
                "[r][c]1[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]1[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]1[/c][c]5[/c][c]6[/c][/r]"
                "[r][c]4[/c][c]6[/c][c]9[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]9[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]4[/c][c]2[/c][c]3[/c][/r]"
                "[f][c][/c][c]11[/c][c]15[/c][/f]"
                "[/t]")
        actual = self.grid.render(EchoRenderer())
        self.assertEquals(expected, actual)

    def testFilter(self):
        self.grid.data = [[1,2,3],[4,5,6]]
        self.grid.filters = ["{one} == 1"]
        expected = ("[t][h/]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[f][c][/c][c][/c][c][/c][/f]"
                "[/t]")
        actual = self.grid.render(EchoRenderer())
        self.assertEquals(expected, actual)


    def testPostAggregateFilter(self):
        self.grid.data = [[1,2,3],[2,2,5], [4,5,6]]
        self.grid.aggregate['one'] = vars(__builtin__)['sum']
        self.grid.post_aggregate_filters = ['{two} == 2']
        expected = ("[t][h/]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[r][c]2[/c][c]2[/c][c]5[/c][/r]"
                "[f][c]7[/c][c][/c][c][/c][/f]"
                "[/t]")
        actual = self.grid.render(EchoRenderer())
        self.assertEquals(expected, actual)


    def testMultiPostAggregateFilter(self):
        self.grid.data = [[1,2,3],[2,2,5], [4,5,6]]
        self.grid.aggregate['one'] = vars(__builtin__)['sum']
        self.grid.post_aggregate_filters = ['{two} == 2', '{three} == 3']
        expected = ("[t][h/]"
                "[r][c]1[/c][c]2[/c][c]3[/c][/r]"
                "[f][c]7[/c][c][/c][c][/c][/f]"
                "[/t]")
        actual = self.grid.render(EchoRenderer())
        self.assertEquals(expected, actual)


class TestCalculatedOutput(unittest.TestCase):

    # Grid fixture
    grid = None

    def setUp(self):
        """Setup for all tests in class"""
        self.grid = DataGrid(testData, testCols)
        self.grid.calculatedcolumns = {"four": "{two}+{three}"}

    def testBasicRender(self):
        # Output of test run should look like this
        expected = ("[t][h/]"
                "[r][c]1[/c][c]2[/c][c]3[/c][c]5.0[/c][/r]"
                "[r][c]4[/c][c]5[/c][c]6[/c][c]11.0[/c][/r]"
                "[f][c][/c][c][/c][c][/c][c]--[/c][/f]"
                "[/t]")
        self.assertEquals(expected, self.grid.render(EchoRenderer()))

    def testFormattedRender(self):
       # Output of test run should look like this
        expected = ("[t][h/]"
                "[r][c]1[/c][c]2[/c][c]3[/c][c]5[/c][/r]"
                "[r][c]4[/c][c]5[/c][c]6[/c][c]11[/c][/r]"
                "[f][c][/c][c][/c][c][/c][c]--[/c][/f]"
                "[/t]")
        self.grid.formatters = {'four': format.number}
        self.assertEquals(expected, self.grid.render(EchoRenderer()))

    def testSortByRender(self):
        # Output of test run should look like this
        expected = ("[t][h/]"
                "[r][c]4[/c][c]5[/c][c]6[/c][c]11.0[/c][/r]"
                "[r][c]1[/c][c]2[/c][c]3[/c][c]5.0[/c][/r]"
                "[f][c][/c][c][/c][c][/c][c]--[/c][/f]"
                "[/t]")
        self.grid.sortby = [('four', 'desc')]
        self.assertEquals(expected, self.grid.render(EchoRenderer()))

    def testPostAggregateFilter(self):
        self.grid.data = [[1,2,3],[2,2,5],[4,5,2]]
        self.grid.aggregate['one'] = vars(__builtin__)['sum']
        self.grid.post_aggregate_filters = ['{four} == 7']
        expected = ("[t][h/]"
                "[r][c]2[/c][c]2[/c][c]5[/c][c]7.0[/c][/r]"
                "[r][c]4[/c][c]5[/c][c]2[/c][c]7.0[/c][/r]"
                "[f][c]7[/c][c][/c][c][/c][c]--[/c][/f]"
                "[/t]")
        actual = self.grid.render(EchoRenderer())
        self.assertEquals(expected, actual)


# Run tests if called from console
if __name__ == '__main__':
    unittest.main()

