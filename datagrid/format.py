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

"""Format Method Library"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from functools import partial, wraps


def _handle_format_error(method):
    """Decorator to handle various exceptions we receive from formatting"""
    @wraps(method)
    def new_method(*args, **kargs):
        try:
            return method(*args, **kargs)
        except TypeError:
            return '--'
        except ValueError:
            return '--'
    return new_method


@_handle_format_error
def plain_number(value):
    """Format float or other numeric value as integer (in string form)

    Example:
    >>> plain_number(100.2)
    '100'
    >>> plain_number(12.0)
    '12'
    >>> plain_number('12.123123123123')
    '12'
    """
    return '%.0f' % float(value)


@_handle_format_error
def number(value, precision=0, delim=','):
    """Format value as number with thousands sep. with fixed precision.

    Example:
    >>> number(1000.5)
    '1,001'
    >>> number(0.25, 1)
    '0.3'
    >>> number(10000.123, 2)
    '10,000.12'
    >>> number('100')
    '100'
    >>> number(0.75, 1)
    '0.8'
    >>> number(0.75, 0)
    '1'
    >>> number('--')
    '--'
    """
    # Return empty values with no change
    if value == '':
        return ''

    try:
        float(value)
    except ValueError:
        return value

    try:
        d = '.' + ('1' * int(precision))
        value = Decimal(str(value)).quantize(Decimal(d), rounding=ROUND_HALF_UP)
    except (TypeError, InvalidOperation):
        value = Decimal(str(value)).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
    
    value = reversed(list(str(value)))

    # Rewrite decimal portion
    new_value = []
    if precision:
        for character in value:
            new_value.append(character)
            if character == '.':
                break
    
    # Add thousands delim every three characters
    new_value.extend("%s%s" % (s, delim) if i and not i % 3 else s 
            for i, s in enumerate(value))

    # Put value back together before we return
    return ''.join(reversed(new_value))


@_handle_format_error
def percent(value, precision=0):
    """Format value as percentage

    Example:
    >>> percent(0.95)
    '95%'
    >>> percent(0.125, 1)
    '12.5%'
    >>> percent(0.125)
    '13%'
    >>> percent(0.125, 2)
    '12.50%'
    >>> percent('--')
    '--'
    """
    # Avoid exceptions from empty cells
    if value == '': 
        return ''
    try:
        return "%s%%" % number(100 * float(value), precision)
    except ValueError:
        return '--'


@_handle_format_error
def currency(value):
    """Format value as currency

    Example:
    >>> currency(123.2)
    '$123.20'
    >>> currency(1)
    '$1.00'
    >>> currency(12322.127)
    '$12,322.13'
    """
    return "$%s" % number(value, 2)

