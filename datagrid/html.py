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

def table(config, head, body, tail):
    return """
        <table class='helper-gridview' cols='{2}'>
            {0}
            <tbody>{1}</tbody>
        </table>
        """.format(head, body, len(config.columns))

def row(config, cells, level=0, name=None, value=None):
    """
    Generate table row segment
    
    Example (flat table):
    >>> from collections import namedtuple
    >>> cfg = namedtuple('Cfg', 'aggregate')([])
    >>> row(cfg, '<td></td>')
    '<tr><td></td></tr>'
    """
    if config.aggregate:
        indent = ((len(config.aggregate) - level) * 5) + 2
        return "<tr class='l-{0}'><td><i>{2}:</i><span>{3}</span></td>{4}</tr>".format(
                level, indent, name, value, cells)
    else: return "<tr>{0}</tr>".format(cells)

def cell(config, data, maxwidth): 
    """
    Generate table cell segment

    Example:
    >>> cell(None,'foo',2)
    '<td>foo</td>'
    """
    return "<td>{0}</td>".format(data, maxwidth)

def head(config):
    """
    Generate table head segment

    Example:
    >>> from collections import namedtuple
    >>> cfg = namedtuple('Cfg', 'columns')(('Heading',))
    >>> head(cfg)
    '<thead><tr><th>Heading</th></tr></thead>'
    """
    cells = ''.join("<th>{0}</th>".format(x) for x in config.columns)
    return "<thead><tr>{0}</tr></thead>".format(cells)

def tail(config, cells):
    """
    Generate table tail segment

    Example:
    >>> tail(None,"<td></td>")
    '<tfoot><tr><td></td></tr></tfoot>'
    """
    return "<tfoot><tr>{0}</tr></tfoot>".format(cells)

