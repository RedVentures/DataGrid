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

"""Base Renderer Class"""

from abc import ABCMeta, abstractmethod

class Renderer(object):
    """Abstract base class for class-based datagrid renderers"""
    __metaclass__ = ABCMeta

    def setup(self, config):
        """Optional setup method"""
        pass

    @abstractmethod
    def table(self, config, head, body, tail): 
        """Generate table's outer display"""
        pass

    @abstractmethod
    def row(self, config, style, level, name=None, value=None): 
        """Generate table row"""
        pass

    @abstractmethod
    def cell(self, config, style, data, column): 
        """Generate table cell"""
        pass

    @abstractmethod
    def head(self, config): 
        """Generate table header"""
        pass

    @abstractmethod
    def tail(self, config, cells): 
        """Generate table footer"""
        pass

