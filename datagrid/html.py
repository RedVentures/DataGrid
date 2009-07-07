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

"""HTML Table Rendering Module"""

def table(config, body):
    return """
        <table class='helper-gridview' cols='{1}'>
            <tbody>{0}</tbody>
        </table>
        """.format(body, len(config.columns))

def row(config, cells, level, name=None, value=None):
    indent = ((len(config.aggregate) - level) * 5) + 2
    return """
        <tr class='l-{0}'>
            <td class='f' style='padding-left: {1}em; 
                    padding-top: {0}px;'>
                <i>{2}:</i><span>{3}</span>
            </td>
            {4}
        </tr>
    """.format(level, indent, name, value, cells)

def cell(config, data, maxwidth): 
    """
    >>> print cell(None,'foo',2)
    <td>foo</td>
    """
    return "<td>{0}</td>".format(data, maxwidth)

def head(config):
    """
    >>> from collections import namedtuple
    >>> cfg = namedtuple('Cfg', 'columns')(('Heading',))
    >>> print head(cfg)
    <thead><tr><th>Heading</th></tr></thead>
    """
    return "<thead><tr>{0}</tr></thead>".format(
            ''.join("<th>{0}</th>".format(x) for x in config.columns) )

def tail(config, cells):
    """
    >>> print tail(None,"<td></td>")
    <tfoot><tr><td></td></tr></tfoot>
    """
    return "<tfoot><tr>{0}</tr></tfoot>".format(cells)

