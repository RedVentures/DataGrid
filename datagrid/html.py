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

import datagrid.renderer

class Renderer(datagrid.renderer.Renderer):

    def table(self, body):
        return """
            <table class='helper-gridview' cols='{1}'>
                <tbody>{0}</tbody>
            </table>
            """.format(body, len(self.columns))

    def row(self, cells, level, name=None, value=None):
        indent = ((len(self.aggregation) - level) * 5) + 2
        return """
            <tr class='l-{0}'>
                <td class='f' style='padding-left: {1}em; 
                        padding-top: {0}px;'>
                    <i>{2}:</i><span>{3}</span>
                </td>
                {4}
            </tr>
        """.format(level, indent, name, value, cells)

    def cell(self, data, maxwidth): 
        """
        >>> r = Renderer();
        >>> print r.cell('foo',2)
        <td>foo</td>
        """
        return "<td>{0}</td>".format(data, maxwidth)

    def head(self):
        """
        >>> r = Renderer()
        >>> r.columns = ('Heading',)
        >>> print r.head()
        <thead><tr><th>Heading</th></tr></thead>
        """
        return "<thead><tr>{0}</tr></thead>".format(
                ''.join("<th>{0}</th>".format(x) for x in self.columns)
                )
        

    def tail(self):
        """
        >>> r = Renderer()
        >>> r.columns = ('Heading',)
        >>> print r.tail()
        <tfoot><tr><td></td></tr></tfoot>
        """
        return ''
