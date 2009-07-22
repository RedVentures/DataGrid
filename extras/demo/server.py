# Import for Standard Library
import os
import sys
import re

# Get DataGrid stuff
sys.path.append(os.path.dirname(__file__) + '/../../')
from datagrid.server.core import (HTTPServer,DefaultHandler)

class DemoHandler(DefaultHandler):
    def do_GET(self):
        if self.path.endswith('.css') || self.path.endswith('.js'):
            DefaultHandler.do_GET(self)
        else:
            DefaultHandler.do_GET(self)

server = HTTPServer(DemoHandler)
server.run()
