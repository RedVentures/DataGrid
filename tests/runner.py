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

# allow relative imports
import sys, os
sys.path.insert(0, os.path.dirname(__file__) + '/../')

import unittest
import core, calctools

# Create test suite
suite = unittest.TestSuite()

# Attach all appropriate test-modules
for module in [core, calctools]:
    suite.addTest(unittest.TestLoader().loadTestsFromModule(module))

# Begin tests
unittest.TextTestRunner(verbosity=1).run(suite)

