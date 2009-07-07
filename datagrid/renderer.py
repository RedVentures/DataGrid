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

"""Base Renderer Class"""

from abc import ABCMeta, abstractmethod

class Renderer(object):
    __metaclass__ = ABCMeta

    columns = tuple()
    aggregation = tuple()
    
    @abstractmethod
    def table(self, body): pass

    @abstractmethod
    def row(self, level, name=None, value=None): pass

    @abstractmethod
    def cell(self, data, maxwidth): pass

    @abstractmethod
    def head(self): pass

    @abstractmethod
    def tail(self): pass

