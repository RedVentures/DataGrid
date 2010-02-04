#------------------------------------------------------------------------#
# DataGrid - Tabular Data Rendering Library
# Copyright (C) 2009-2010 Adam Wagner <awagner@redventures.com>
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

import SocketServer
import SimpleHTTPServer
import threading
from time import sleep

class HTTPServer:
    """
    Simple HTTP Server
    """

    # internal SocketServer instance
    server = None

    def __init__(self, handler=None, port=8080):
        """Configure Server Setup"""
        self.port = port
        self.handler = handler or DefaultHandler

    def run(self):
        """Start Server"""
        self.server = SocketServer.ThreadingTCPServer(
                ('localhost', self.port), self.handler)
        print "serving at http://localhost:", self.port
        try:
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.setDaemon(True)
            server_thread.start()
            while True:
                sleep(10)
        except KeyboardInterrupt:
            print "\nshutting down..."
            self.server.shutdown()

class DefaultHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """
    The DefaultHandler serves up DataGrid results using native classes
    """
    def do_GET(self):
        """Process HTTP server get request"""
        if self.path == '/hello':
            self.request.send('Hello World!')
        else:
            # serve files, and directory listings by following self.path from
            # current working directory
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

