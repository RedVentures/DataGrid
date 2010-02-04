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

"""DataGrid install/dist utils"""

from os import tmpfile
from subprocess import check_call, CalledProcessError

def phpdir():
    """Locate PHP's include-dir"""
    with tmpfile() as phpinfo:
        try:
            check_call(['php -r "echo get_include_path();"'], stdout=phpinfo,
                    shell=True)
            phpinfo.seek(0)

            # attempt to find best match for php include dir
            include_path = phpinfo.read().split(':')

            # find the least significant dir that includes the name php
            return [dir_ for dir_ in include_path if 'php' in dir_][-1]
        except CalledProcessError:
            return False
                
