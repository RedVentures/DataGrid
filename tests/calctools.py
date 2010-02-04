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

"""datagrid.calculate test module"""

import unittest
from datagrid.calctools import calculatevalues, CalculatedValueError

class TestCalcTools(unittest.TestCase):
    """CalcTools unit-tests"""

    def testCalculatedValues(self):

        # Test calculations in 'normal' order
        data = {'one': 5, 'two': 10, 'three': 15}
        calculations = {
                'four': lambda d: d['one'] + d['three'],
                'five': lambda d: d['one'] + d['four'] }
        actual = calculatevalues(data, calculations)
        expected = {'one': 5, 'two': 10, 'three': 15, 'four': 20, 'five': 25}

        self.assertEquals(expected, actual)

        # Test calculations in 'reverse' order
        data = {'one': 5, 'two': 10, 'three': 15}
        calculations = {
                'five': lambda d: d['one'] + d['four'],
                'four': lambda d: d['one'] + d['three']}
        actual = calculatevalues(data, calculations)
        expected = {'one': 5, 'two': 10, 'three': 15, 'four': 20, 'five': 25}

        self.assertEquals(expected, actual)

    def testImproperCalculations(self):

        data = {'one': 5, 'two': 10, 'three': 15}
        calculations = { 'five': lambda d: d['one'] + d['four'] }

        self.assertRaises(CalculatedValueError, 
                calculatevalues, data, calculations)

# Run tests if called from console
if __name__ == '__main__':
    unittest.main()

