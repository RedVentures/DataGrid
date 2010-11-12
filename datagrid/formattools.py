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

"""Tools for dealing with column formatting options"""

def str_formatter(string):
    """
    Return str formatter from given string

    Example:
    >>> f = str_formatter('%.1f')
    >>> f(10)
    '10.0'
    """
    return lambda v: string % v


def parse_options(formatters):
    """Parse format options passed to rendergrid and return the format required
    for datagrid.core

    Example:
    >>> formatters = parse_options(['colA|percent:1','colB|%.0f|percent:1'])
    >>> type(formatters['colA'])
    <type 'function'>
    >>> type(formatters['colB'])
    <type 'function'>
    >>> funcs = parse_options(['Score|percent:1', 'Z-Score|%0.2f'])

    >>> funcs['Score'](0.99)
    '99.0%'
    """
    # create dictionary from simple list, setting the first item in each list
    # as the dictionary key... the remaining values are set as the value at
    # that key
    formatters = dict((y[0], y[1:]) 
            for y in (x.split('|') for x in formatters))

    def make_fun(fun, *params):
        def ifun(x):
            return fun(x, *params)
        return ifun

    # generate/load format methods
    if len(formatters):
        import datagrid.format
        for key, methods in formatters.iteritems():
            
            # materialize all methods
            for i, method in enumerate(methods):

                # check for str-methods we need to generate
                if method.startswith('%'):
                    methods[i] = str_formatter(method)
                elif method[0] in ['"', "'"]:
                    methods[i] = str_formatter(method[1:-1])

                # if this is not a string formatter, look in format module
                else:
                    # if parameters were passed with method name
                    if ':' in method: 
                        # parse parameters and pass to formatter
                        method, parameters = method.split(':')

                        method = vars(datagrid.format)[method]
                        parameters = [p.strip() for p in parameters.split(',')]
                        
                        # pass through params given on console
                        methods[i] = make_fun(method, *parameters)

                    # no parameters were found with method
                    else:
                        methods[i] = vars(datagrid.format)[method]

            # Consolidate function into one callable, so that when we call 
            # returned function c, it's really calling a then passing the 
            # results through b.    (given we have method list [a,b])
            formatters[key] = reduce(_create_flow, methods)

    # return parsed formatters dictionary
    return formatters


def _create_flow(function_a, function_b):
    """Generate lambda to be used in formatter flow"""
    return lambda x: function_b(function_a(x))

