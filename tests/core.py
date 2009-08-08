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

"""datagrid.core test module"""

import unittest
from datagrid.core import DataGrid


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

    def row(self, config, cells, level=0, name=None, value=None): 
        return "[r]" + cells + "[/r]"

    def cell(self, config, data, column): 
        return "[c]" + data + "[/c]"

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
        self.grid = DataGrid(testData, StackTestRenderer(), testCols)
    
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
        self.grid.render()
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
        self.grid.render()
        self.assertEquals(testLog, self.grid.renderer.callLog)


class TestOutput(unittest.TestCase):
    
    # Grid fixture
    grid = None

    def setUp(self):
        """Setup for all tests in class"""
        self.grid = DataGrid(testData, EchoRenderer(), testCols)

    def testBasicRender(self): 
        # Output of test run should look like this
        expected = "[t][h/][r][c]1[/c][c]2[/c][c]3[/c][/r]" \
                "[r][c]4[/c][c]5[/c][c]6[/c][/r][f][c][/c][c][/c][c][/c][/f][/t]"
        self.assertEquals(expected, self.grid.render())

    def testHideColumn(self): 
        # Output of test run should look like this
        expected = "[t][h/][r][c]1[/c][c]2[/c][/r]" \
                "[r][c]4[/c][c]5[/c][/r][f][c][/c][c][/c][/f][/t]"

        # Only show first two columns
        self.grid.columns = ('one', 'two')
        self.assertEquals(expected, self.grid.render())


# Run tests if called from console
if __name__ == '__main__':
    unittest.main()

