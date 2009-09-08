#------------------------------------------------------------------------#
# DataGrid - Tabular Data Rendering Library
# Copyright (C) 2009 Adam Wagner <awagner@redventures.com>
#                    Kenny Parnell <kparnell@redventures.com>
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

import datagrid.renderer.abstract

class Renderer(datagrid.renderer.abstract.Renderer):
    """
    HTML Table Renderer
    """

    # Options
    html_id = 'datagrid'        # Table ID ATTR
    html_class = 'datagrid'     # HTML Class ATTR 

    def table(self, config, thead, tbody, tfoot):
        """
        Generate HTML table from pregenerated head/body/tail sections
        """
        return """
            <table id='%s' class='%s' cols='%s'>
                %s<tbody>%s</tbody>%s
            </table>
            """ % (self.html_id, self.html_class, 
                    len(config.columns), thead, tbody, tfoot)


    def row(self, config, cells, level=0, name=None, value=None):
        """
        Generate table row segment
        
        Example (flat table):
        >>> from collections import namedtuple
        >>> cfg = namedtuple('Cfg', 'groupby')([])
        >>> row(cfg, '<td></td>')
        '<tr><td></td></tr>'
        """
        if config.groupby:
            if name is None:
                return "<tr class='l-%s'><td></td>%s</tr>" % (level, cells)
            else:
                group_name = ("<span>%s</span>" * 2) % (name, value)
                return "<tr class='l-%s'><td>%s</td>%s</tr>" % \
                        (level, group_name, cells)
        else: return "<tr>%s</tr>" % cells


    def cell(self, config, data, column): 
        """
        Generate table cell segment

        Example:
        >>> cell(None,'foo',2)
        '<td>foo</td>'
        """
        return "<td>%s</td>" % data


    def head(self, config):
        """
        Generate table head segment

        Example:
        >>> from collections import namedtuple
        >>> Cfg = namedtuple('Cfg', 'columns groupby descriptions')
        >>> cfg = Cfg(('Heading',), [], {})
        >>> head(cfg)
        '<thead><tr><th>Heading</th></tr></thead>'
        >>> cfg = Cfg(('Heading',), [], {'Heading': 'Hello World!'})
        >>> head(cfg)
        '<thead><tr><th title="Hello World!">Heading</th></tr></thead>'
        """
        # build list of cells
        cells = []
        for col in config.columns:
            try:
                cells.append("<th title=\"%s\">%s</th>" 
                        % (config.descriptions[col], col))
            except KeyError:    # title was not found, omit
                cells.append("<th>%s</th>" % col)

        # glue pieces together and return
        return ("<thead><tr>%s</tr></thead>" if not config.groupby else
                     "<thead><tr><th></th>%s</tr></thead>") % ''.join(cells)


    def tail(self, config, cells):
        """
        Generate table tail segment

        Example:
        >>> from collections import namedtuple
        >>> cfg = namedtuple('Cfg', 'groupby')([])
        >>> tail(cfg,"<td></td>")
        '<tfoot><tr><td></td></tr></tfoot>'
        """
        return ("<tfoot><tr>%s</tr></tfoot>" if not config.groupby else 
                     "<tfoot><tr><td></td>%s</tr></tfoot>") % cells

