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

# Error generated while trying to run calculatevalues method
class CalculatedValueError(Exception): pass

def calculatevalues(data, calculations):
    """
    Calculate given formulas on data

    Example:
    >>> formulas = {'c': lambda d: 3}
    >>> r = calculatevalues({'a': 1, 'b': 2}, formulas)
    >>> r == {'a': 1, 'b': 2, 'c': 3}
    True
    >>> len(formulas)
    1
    """

    # copy calculations to avoid destruction
    calculations = calculations.copy()

    while True:
        # get count of calculations we have left to run
        start = len(calculations)   
        for key, calc in calculations.items():

            # attempt to run calculation
            try: data[key] = calc(data)
            except KeyError:    # we may get this missing val from some
                continue        # other calculated value, so continue for now
            except ValueError:
                data[key] = None    # data is not in a format we expect, set as null

            # calculation was a success, remove from list
            del calculations[key]

        # check how many calculations we have left
        end = len(calculations) 
        if end == 0: break      # we must be finished, exit loop
        elif end == start:      # no calculations have sucessfully been run
            raise CalculatedValueError()    # exit with exception

    # return initial data-row with addition of newly calculated values
    return data


def formula(calcString):
    """
    Generate formula to run on given data

    Example:
    >>> f = formula('{a} + {b}')
    >>> f({'a': 1, 'b': 1})
    2.0
    """
    # replace place-holders with dictionary refs
    calcString = calcString.replace('{', 'float(d["').replace('}', '"])')

    # create new function and return
    exec 'f = lambda d: ' + calcString
    return f

