#!/usr/bin/env python
#------------------------------------------------------------------------#
# DataGrid - Tabular Data Rendering Library
# Copyright (C) 2009-2010 Adam Wagner <awagner@redventures.com>
#                         Kenny Parnell <k.parnell@gmail.com>
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

"""DataGrid setup-tools"""

import sys
from setuptools import setup, find_packages
from datagrid import about

# Executables and bindings list
data_files = [('bin', ['rendergrid'])]

# Dispatch distutils setup magic
setup(
        name = about.NAME,
        version = about.VERSION,
        packages = find_packages(),
        data_files = data_files,
        author = 'Adam Wagner, Kenny Parnell',
        author_email = 'awagner83@gmail.com, k.parnell@gmail.com',
        description = 'Tabular data rendering library',
        url = 'http://github.com/redventures-oss/DataGrid',
        license = 'LGPL 3',
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Environment :: Console',
            'Programming Language :: Python',
            'Programming Language :: JavaScript',
            'Natural Language :: English',
            'License :: OSI Approved',
            'Intended Audience :: Developers',
            'Topic :: Utilities',
        ],
     )

