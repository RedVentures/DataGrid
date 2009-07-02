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

def table(body):
    return """
        <table class='helper-gridview'><tbody>{0}</tbody></table>
        """.format(body)

def row(cells, level, name=None, value=None):
    indent = (level * 5) + 2
    return """
    <tr class='l-{0}'>
        <td class='f' style='padding-left: {1}em; 
                padding-top: {0}px;'>
            <i>{2}:</i><span>{3}</span>
        </td>
        {4}
    </tr>
    """.format(level, indent, name, value, cells)

def cell(data): return "<td>{0}</td>".format(data)

