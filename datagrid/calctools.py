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

"""DataGrid Calculation Tools"""

class CalculatedValueError(Exception): pass

def calculatevalues(data, calculations):
    while True:
        start = len(calculations)   
        for k, fun in calculations.items():
            data[k] = fun(data)
            del calculations[k]
        end = len(calculations) 
        if end == 0: break
        elif len(calculations) == start:
            raise CalculatedValueError()
    return data


