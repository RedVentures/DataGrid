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

"""DataGrid Calculation Tools"""

from abc import ABCMeta


class CalculationFailureError(Exception):
    """Meta exception including Value, Type, and ZeroDivision Errors"""
    __metaclass__ = ABCMeta

# Register Type/Value/ZeroDivision Errors as part of this ABC
for Err in [TypeError, ValueError]:
    CalculationFailureError.register(Err)


class CalculatedValueError(Exception): 
    """Error generated if calculatedvalues method fails"""
    pass


def calculatevalues(data, calculations):
    """Calculate given formulas on data

    Example:
    >>> formulas = {'c': lambda d: 3}
    >>> r = calculatevalues({'a': 1, 'b': 2}, formulas)
    >>> r == {'a': 1, 'b': 2, 'c': 3}
    True
    >>> len(formulas)
    1
    >>> formulas = {'c': lambda d: d['a'] + d['b']}
    >>> r = calculatevalues({'a': 1, 'b': ''}, formulas)
    >>> r == {'a': 1, 'b': '', 'c': '--'}
    True
    >>> formulas = {'c': lambda d: d['a'] / d['b']}
    >>> r = calculatevalues({'a': 0, 'b': 0}, formulas)
    >>> r == {'a': 0, 'b': 0, 'c': 0}
    True
    """
    # Copy calculations to avoid destruction
    calculations = calculations.copy()

    while True:
        # Get count of calculations we have left to run
        start = len(calculations)   
        for key, calc in calculations.items():

            # Attempt to run calculation
            try: 
                data[key] = calc(data)
            except ZeroDivisionError:
                data[key] = 0
            except KeyError:
                # Apparently we are missing a value, presumably calculated.
                # Skip for now, we may find this in another round
                continue 
            except CalculationFailureError:
                # Data is not in a format we expect, set as '--' (or null)
                data[key] = '--'    

            # Calculation was a success, remove from list
            del calculations[key]

        # Check how many calculations we have left
        end = len(calculations) 
        if end == 0: 
            # We must be finished, exit loop
            break
        elif end == start:
            # No calculations have sucessfully been run.  Exit with exception
            raise CalculatedValueError()

    # Return initial data-row with addition of newly calculated values
    return data


def formula(calc_string):
    """Generate formula to run on given data

    Example:
    >>> f = formula('{a} + {b}')
    >>> f({'a': 1, 'b': 1})
    2.0
    """
    # replace place-holders with dictionary refs
    calc_string = calc_string.replace('{', 'float(d["').replace('}', '"])')

    # create new function and return
    calc_method = None
    exec 'calc_method = lambda d: ' + calc_string  # pylint: disable-msg=W0122
    return calc_method

def bool_formula(calc_string):
    """Generate formula to run on given data

    Example:
    >>> f = bool_formula('{a} < {b}')
    >>> f({'a': 1, 'b': 2})
    True
    """
    # replace place-holders with dictionary refs
    calc_string = calc_string.replace('{', 'd["').replace('}', '"]')

    # create new function and return
    calc_method = None
    exec 'calc_method = lambda d: ' + calc_string  # pylint: disable-msg=W0122
    return calc_method
