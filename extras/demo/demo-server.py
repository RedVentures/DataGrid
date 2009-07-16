import os
import sys
sys.path.append(os.path.dirname(__file__) + '/../../')
from datagrid.server.core import (HTTPServer,DefaultHandler)

class DemoHandler(DefaultHandler):
    def do_GET(self):
        self.path = '/extras/demo' + self.path
        DefaultHandler.do_GET(self)

server = HTTPServer(DemoHandler)
server.run()
