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

# allow relative imports
import sys, os
sys.path.append(os.path.dirname(__file__) + '/../')

from datagrid.core import DataGrid
import unittest

class RendererFixture(object):
    """
    TestRenderer - Allows testing of datagrid.core without intimate
    details of how any specific renderer works
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


class TestDataGrid(unittest.TestCase):
    """DataGrid core unit-test"""

    # Grid fixture
    grid = None

    # Test data: simple 2x3 table
    testData = [[1, 2, 3], [4, 5, 6]]

    # Column names for test table
    testCols = ['one', 'two', 'three']

    def setUp(self):
        """Setup fixtures"""
        self.grid = DataGrid(self.testData, None, self.testCols)
    
    def tearDown(self):
        """Cleanup and prep for next run"""
        RendererFixture.callLog = []

    def testRender(self):
        """Test DataGrid.render method"""

        # Evaluation order or render methods for given test table
        testLog = ['setup', 'head',             # Setup table and header
                'cell', 'cell', 'cell', 'row',  # Rendering Row 1 
                'cell', 'cell', 'cell', 'row',  # Rendering Row 2
                'cell', 'cell', 'cell', 'tail', # Rendering Footer
                'table']                        # Wrap up table render

        # Test simple render
        self.grid.renderer = RendererFixture()
        self.grid.render()
        self.assertEquals(testLog, self.grid.renderer.callLog)

    def testRenderAggregate(self):
        """Test DataGrid.render method - with aggregation"""

        # Aggregation eval order
        testLog = ['setup', 'head',             # Setup table and header
                'cell', 'cell', 'cell', 'row',  # Rendering Agg Row 1 
                'cell', 'cell', 'cell', 'row',  # Rendering Row 1 
                'cell', 'cell', 'cell', 'row',  # Rendering Agg Row 2
                'cell', 'cell', 'cell', 'row',  # Rendering Row 2 
                'cell', 'cell', 'cell', 'tail', # Rendering Footer
                'table']                        # Wrap up table render

        # Test simple render
        self.grid.renderer = RendererFixture()
        self.grid.aggregate = ['one']
        self.grid.render()
        self.assertEquals(testLog, self.grid.renderer.callLog)


# Run tests if called from console
if __name__ == '__main__':
    unittest.main()

