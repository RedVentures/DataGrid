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
        <table class='helper-gridview' cols='{3}'>
            {0}
            <tbody>{1}</tbody>
            {2}
        </table>
        """.format(head, body, tail, len(config.columns))

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
        if name is None:
            return "<tr class='l={0}'><td></td>{1}</tr>".format(level, cells)
        else:
            row = "<tr class='l-{0}'><td><i>{1}:</i><span>{2}</span></td>{3}</tr>"
            return row.format(level, name, value, cells)
    else: return "<tr>{0}</tr>".format(cells)

def cell(config, data, column): 
    """
    Generate table cell segment

    Example:
    >>> cell(None,'foo',2)
    '<td>foo</td>'
    """
    return "<td>{0}</td>".format(data)

def head(config):
    """
    Generate table head segment

    Example:
    >>> from collections import namedtuple
    >>> cfg = namedtuple('Cfg', 'columns aggregate')(('Heading',), [])
    >>> head(cfg)
    '<thead><tr><th>Heading</th></tr></thead>'
    """
    cells = ''.join("<th>{0}</th>".format(x) for x in config.columns)
    headformat = "<thead><tr>{0}</tr></thead>" if not config.aggregate else \
                 "<thead><tr><th></th>{0}</tr></thead>"
    return headformat.format(cells)

def tail(config, cells):
    """
    Generate table tail segment

    Example:
    >>> from collections import namedtuple
    >>> cfg = namedtuple('Cfg', 'aggregate')([])
    >>> tail(cfg,"<td></td>")
    '<tfoot><tr><td></td></tr></tfoot>'
    """
    tailformat = "<tfoot><tr>{0}</tr></tfoot>" if not config.aggregate else \
                 "<tfoot><tr><td></td>{0}</tr></tfoot>"
    return tailformat.format(cells)

